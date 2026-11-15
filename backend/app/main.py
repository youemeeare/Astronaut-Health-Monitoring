from __future__ import annotations
import os, hmac, hashlib, base64, json, secrets, random, math
from datetime import datetime, timezone, timedelta
from typing import Optional, Literal
import httpx
import numpy as np
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as DBField, Session, create_engine, select

APP_VERSION = "1.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./astra_med.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
TOKEN_SECRET = os.getenv("ASTRA_TOKEN_SECRET", "CHANGE_ME_BEFORE_DEPLOYMENT_" + secrets.token_hex(16))
DEMO_MODE = os.getenv("ASTRA_DEMO_MODE", "true").lower() == "true"

class Reading(SQLModel, table=True):
    id: Optional[int] = DBField(default=None, primary_key=True)
    astronaut_id: str = DBField(index=True)
    recorded_at: datetime = DBField(index=True)
    heart_rate_bpm: Optional[float] = None
    spo2_percent: Optional[float] = None
    temperature_c: Optional[float] = None
    sleep_hours: Optional[float] = None
    fatigue_score: Optional[int] = None
    workload: Optional[float] = None
    radiation_msv: Optional[float] = None
    systolic_mmhg: Optional[float] = None
    diastolic_mmhg: Optional[float] = None
    glucose_mg_dl: Optional[float] = None
    mood_score: Optional[int] = None
    hydration_ml: Optional[float] = None
    weight_kg: Optional[float] = None
    exercise_minutes: Optional[float] = None
    cabin_co2_ppm: Optional[float] = None
    cabin_humidity_percent: Optional[float] = None
    cabin_temperature_c: Optional[float] = None
    source: str = "SIMULATED"

class AstronautProfile(SQLModel, table=True):
    astronaut_id: str = DBField(primary_key=True)
    display_name: str
    mission: str = "DEMO-ORBIT"
    role: str = "astronaut"
    created_at: datetime = DBField(default_factory=lambda: datetime.now(timezone.utc))

class AuditEvent(SQLModel, table=True):
    id: Optional[int] = DBField(default=None, primary_key=True)
    actor: str
    action: str
    subject: str = ""
    created_at: datetime = DBField(default_factory=lambda: datetime.now(timezone.utc))
    detail: str = ""

class ResearchDatasetRow(SQLModel, table=True):
    id: Optional[int] = DBField(default=None, primary_key=True)
    dataset_name: str = DBField(index=True)
    source: str = "NASA_RESEARCH"
    row_json: str
    imported_at: datetime = DBField(default_factory=lambda: datetime.now(timezone.utc), index=True)
    imported_by: str = "demo-operator"

class HazardObservation(SQLModel, table=True):
    id: Optional[int] = DBField(default=None, primary_key=True)
    astronaut_id: str = DBField(index=True)
    domain: str = DBField(index=True)
    metric: str
    value: float
    unit: str
    observed_at: datetime = DBField(default_factory=lambda: datetime.now(timezone.utc), index=True)
    source: str = "MANUAL"
    evidence_ref: str = ""
    context_json: str = "{}"
    created_by: str = "demo-operator"

class HazardObservationIn(BaseModel):
    astronaut_id: str = Field(default="AST-001", min_length=2, max_length=64)
    domain: Literal["radiation","behavioral","distance","gravity","habitat","immune","cardiovascular","sensorimotor"]
    metric: str = Field(min_length=2, max_length=80)
    value: float = Field(ge=-1_000_000, le=1_000_000)
    unit: str = Field(min_length=1, max_length=24)
    observed_at: Optional[datetime] = None
    source: Literal["MANUAL","SENSOR","SIMULATED","NASA_OSDR","CSA_RESEARCH"] = "MANUAL"
    evidence_ref: str = Field(default="", max_length=300)
    context: dict = Field(default_factory=dict)

class MissionLinkScenarioIn(BaseModel):
    one_way_delay_minutes: float = Field(default=20, ge=0, le=20)
    outage_minutes: float = Field(default=0, ge=0, le=10080)
    queued_messages: int = Field(default=3, ge=0, le=10000)
    average_message_kb: float = Field(default=4, ge=0, le=100000)

class ResearchBatchIn(BaseModel):
    dataset_name: str = Field(min_length=1, max_length=255)
    source: Literal["NASA_RESEARCH"] = "NASA_RESEARCH"
    rows: list[dict] = Field(min_length=1, max_length=250)

class ReadingIn(BaseModel):
    astronaut_id: str = Field(min_length=1, max_length=64)
    recorded_at: Optional[datetime] = None
    heart_rate_bpm: Optional[float] = Field(default=None, ge=25, le=240)
    spo2_percent: Optional[float] = Field(default=None, ge=50, le=100)
    temperature_c: Optional[float] = Field(default=None, ge=30, le=43)
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24)
    fatigue_score: Optional[int] = Field(default=None, ge=0, le=10)
    workload: Optional[float] = Field(default=None, ge=0, le=10)
    radiation_msv: Optional[float] = Field(default=None, ge=0, le=1000)
    systolic_mmhg: Optional[float] = Field(default=None, ge=50, le=300)
    diastolic_mmhg: Optional[float] = Field(default=None, ge=30, le=200)
    glucose_mg_dl: Optional[float] = Field(default=None, ge=20, le=1000)
    mood_score: Optional[int] = Field(default=None, ge=0, le=10)
    hydration_ml: Optional[float] = Field(default=None, ge=0, le=10000)
    weight_kg: Optional[float] = Field(default=None, ge=10, le=500)
    exercise_minutes: Optional[float] = Field(default=None, ge=0, le=1440)
    cabin_co2_ppm: Optional[float] = Field(default=None, ge=0, le=100000)
    cabin_humidity_percent: Optional[float] = Field(default=None, ge=0, le=100)
    cabin_temperature_c: Optional[float] = Field(default=None, ge=-100, le=100)
    source: Literal["SIMULATED","SENSOR","MANUAL","NASA_RESEARCH"] = "MANUAL"

class SimulateRequest(BaseModel):
    astronaut_id: str = "AST-001"
    count: int = Field(default=1, ge=1, le=500)
    scenario: Literal["normal","elevated_fatigue","unusual_hr","low_spo2","workload_spike","combined_event"] = "normal"

class ProfileIn(BaseModel):
    astronaut_id: str = Field(min_length=2, max_length=64)
    display_name: str = Field(min_length=2, max_length=100)
    mission: str = Field(default="DEMO-ORBIT", max_length=100)
    role: Literal["astronaut","medical_officer","mission_control","admin"] = "astronaut"

class TwinIn(BaseModel):
    astronaut_id: str = "AST-001"
    hours: int = Field(default=24, ge=1, le=168)
    intervention: Literal["baseline","rest","reduced_workload","sleep_extension"] = "baseline"

class EmergencyIn(BaseModel):
    scenario: Literal["degraded_telemetry","fatigue_event","oxygen_sensor_alert","communications_loss","combined_contingency"] = "combined_contingency"

app = FastAPI(title="ASTRA-MED X API", version=APP_VERSION, description="Research demonstrator for astronaut health intelligence; not for clinical or flight use.")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:8081,http://127.0.0.1:5173").split(","), allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

def token_for(role: str, actor: str):
    payload={"role":role,"sub":actor,"exp":int((datetime.now(timezone.utc)+timedelta(hours=8)).timestamp())}
    raw=base64.urlsafe_b64encode(json.dumps(payload,separators=(",",":")).encode()).decode().rstrip("=")
    sig=base64.urlsafe_b64encode(hmac.new(TOKEN_SECRET.encode(),raw.encode(),hashlib.sha256).digest()).decode().rstrip("=")
    return raw+"."+sig

def current_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        if DEMO_MODE: return {"sub":"demo-operator","role":"admin"}
        raise HTTPException(401,"Bearer token required")
    try:
        raw,sig=authorization[7:].split(".")
        expected=base64.urlsafe_b64encode(hmac.new(TOKEN_SECRET.encode(),raw.encode(),hashlib.sha256).digest()).decode().rstrip("=")
        if not hmac.compare_digest(sig,expected): raise ValueError()
        payload=json.loads(base64.urlsafe_b64decode(raw+"==="))
        if payload["exp"] < int(datetime.now(timezone.utc).timestamp()): raise ValueError()
        return payload
    except Exception: raise HTTPException(401,"Invalid or expired token")

def audit(actor, action, subject="", detail=""):
    with Session(engine) as s:
        s.add(AuditEvent(actor=actor,action=action,subject=subject,detail=detail[:500])); s.commit()

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)
    if DATABASE_URL.startswith("sqlite"):
        additions = {
            "systolic_mmhg":"FLOAT", "diastolic_mmhg":"FLOAT", "glucose_mg_dl":"FLOAT",
            "mood_score":"INTEGER", "hydration_ml":"FLOAT", "weight_kg":"FLOAT",
            "exercise_minutes":"FLOAT", "cabin_co2_ppm":"FLOAT", "cabin_humidity_percent":"FLOAT",
            "cabin_temperature_c":"FLOAT"
        }
        with engine.connect() as conn:
            existing = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(reading)").fetchall()}
            for col, typ in additions.items():
                if col not in existing: conn.exec_driver_sql(f"ALTER TABLE reading ADD COLUMN {col} {typ}")
            conn.commit()
    with Session(engine) as s:
        if not s.get(AstronautProfile,"AST-001"):
            s.add(AstronautProfile(astronaut_id="AST-001",display_name="Demo Crew Member",mission="DEMO-ORBIT"))
            s.commit()

@app.get("/health")
def health():
    return {"status":"ok","service":"astra-med-x-api","version":APP_VERSION,"utc":datetime.now(timezone.utc),"mode":"DEMO" if DEMO_MODE else "AUTHENTICATED"}

@app.post("/api/v1/auth/demo-login")
def demo_login(role: Literal["astronaut","medical_officer","mission_control","admin"]="mission_control"):
    if not DEMO_MODE: raise HTTPException(403,"Demo login disabled")
    actor="demo-"+role
    return {"access_token":token_for(role,actor),"token_type":"bearer","role":role,"notice":"Demonstration identity only; replace with institutional OIDC/SSO before operational use."}

@app.get("/api/v1/auth/me")
def me(authorization: Optional[str]=Header(default=None)):
    return current_user(authorization)

@app.get("/api/v1/profiles")
def profiles(authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    with Session(engine) as s: return s.exec(select(AstronautProfile)).all()

@app.post("/api/v1/profiles")
def create_profile(p: ProfileIn, authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    if u["role"] not in ("admin","medical_officer"): raise HTTPException(403,"Role not permitted")
    with Session(engine) as s:
        if s.get(AstronautProfile,p.astronaut_id): raise HTTPException(409,"Profile already exists")
        obj=AstronautProfile(**p.model_dump()); s.add(obj); s.commit(); s.refresh(obj)
    audit(u["sub"],"PROFILE_CREATED",p.astronaut_id)
    return obj

@app.post("/api/v1/readings")
def create_reading(p: ReadingIn, authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    obj=Reading(**p.model_dump(exclude={"recorded_at"}),recorded_at=p.recorded_at or datetime.now(timezone.utc))
    with Session(engine) as s: s.add(obj); s.commit(); s.refresh(obj)
    audit(u["sub"],"READING_CREATED",p.astronaut_id,p.source)
    return obj

@app.post("/api/v1/readings/bulk")
def bulk_readings(payload: list[ReadingIn], authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    if not payload or len(payload)>5000: raise HTTPException(422,"Submit between 1 and 5000 rows per batch.")
    made=[]
    with Session(engine) as s:
        for item in payload:
            obj=Reading(**item.model_dump(exclude={"recorded_at"}), recorded_at=item.recorded_at or datetime.now(timezone.utc))
            s.add(obj); made.append(obj)
        s.commit()
        for obj in made: s.refresh(obj)
    audit(u["sub"],"BULK_READINGS_IMPORTED",payload[0].astronaut_id,f"rows={len(made)}; source={payload[0].source}")
    return {"imported":len(made),"astronaut_id":payload[0].astronaut_id,"source":payload[0].source,"message":"Batch accepted. Review data provenance and units before interpreting results."}

@app.get("/api/v1/readings")
def list_readings(astronaut_id: str="AST-001",limit:int=Query(100,ge=1,le=1000),authorization:Optional[str]=Header(default=None)):
    current_user(authorization)
    with Session(engine) as s:
        return list(s.exec(select(Reading).where(Reading.astronaut_id==astronaut_id).order_by(Reading.recorded_at.desc()).limit(limit)).all())

@app.post("/api/v1/demo/simulate")
def simulate(p: SimulateRequest, authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    if not DEMO_MODE: raise HTTPException(403,"Simulation disabled")
    now=datetime.now(timezone.utc); made=[]
    with Session(engine) as s:
        for i in range(p.count):
            hr=random.gauss(68,5); spo2=min(100,max(94,random.gauss(98,.7))); temp=random.gauss(36.7,.2)
            sleep=max(0,random.gauss(7.2,.6)); fatigue=min(10,max(0,round(random.gauss(2,1)))); workload=min(10,max(0,random.gauss(3,1.2))); rad=max(0,random.gauss(.015,.004))
            if p.scenario in ("elevated_fatigue","combined_event"): sleep, fatigue= random.gauss(4.1,.3),random.randint(7,9)
            if p.scenario in ("unusual_hr","combined_event"): hr=random.gauss(108,5)
            if p.scenario in ("low_spo2","combined_event"): spo2=random.gauss(91.5,1)
            if p.scenario=="workload_spike": workload=random.gauss(9,.3)
            row=Reading(astronaut_id=p.astronaut_id,recorded_at=now-timedelta(minutes=(p.count-i-1)*5),heart_rate_bpm=round(hr,1),spo2_percent=round(spo2,1),temperature_c=round(temp,2),sleep_hours=round(sleep,1),fatigue_score=fatigue,workload=round(workload,1),radiation_msv=round(rad,5),source="SIMULATED")
            s.add(row); made.append(row)
        s.commit()
    audit(u["sub"],"SYNTHETIC_BATCH_CREATED",p.astronaut_id,f"{p.count}:{p.scenario}")
    return {"created":len(made),"source":"SIMULATED","scenario":p.scenario,"notice":"Generated values are synthetic test fixtures, not astronaut telemetry."}

def get_rows(aid,limit=300):
    with Session(engine) as s:
        return list(s.exec(select(Reading).where(Reading.astronaut_id==aid).order_by(Reading.recorded_at.desc()).limit(limit)).all())

def baseline(rows):
    fields=["heart_rate_bpm","spo2_percent","temperature_c","sleep_hours","fatigue_score","workload","systolic_mmhg","diastolic_mmhg","glucose_mg_dl","mood_score","hydration_ml","weight_kg","exercise_minutes","cabin_co2_ppm","cabin_humidity_percent","cabin_temperature_c"]
    result={}
    for f in fields:
        vals=[float(getattr(r,f)) for r in rows if getattr(r,f) is not None]
        result[f]={"n":len(vals),"mean":round(float(np.mean(vals)),3) if vals else None,"std":round(float(np.std(vals,ddof=1)),3) if len(vals)>1 else None,"method":"personal rolling descriptive baseline; requires adequate stable history"}
    return result

def assess(rows):
    if not rows:return {"status":"NO_DATA","agents":[],"alerts":[],"explanation":"No readings available."}
    recent=rows[:1][0]; hist=rows[1:61]
    b=baseline(hist)
    agents=[]; alerts=[]
    def check(agent,metric,val,rule,desc,severity="REVIEW"):
        if rule:
            alert={"agent":agent,"metric":metric,"value":val,"severity":severity,"reason":desc,"evidence":"Demonstration rule / deviation; not a clinical threshold."}
            alerts.append(alert); agents.append({"agent":agent,"status":"REVIEW","finding":desc})
        else: agents.append({"agent":agent,"status":"NO_RULE_TRIGGERED","finding":"No configured demonstration rule triggered."})
    hr=recent.heart_rate_bpm; spo=recent.spo2_percent; sl=recent.sleep_hours; fat=recent.fatigue_score; wl=recent.workload
    check("CARDIAC_TREND","heart_rate_bpm",hr,hr is not None and hr>=100,"Heart-rate value crossed the configurable demo review threshold.")
    check("OXYGEN_SIGNAL","spo2_percent",spo,spo is not None and spo<94,"Oxygen saturation value crossed the configurable demo review threshold.","URGENT_REVIEW")
    check("SLEEP_CIRCADIAN","sleep_hours",sl,sl is not None and sl<5,"Reported sleep duration is short; review timing and individual context.")
    check("FATIGUE_WORKLOAD","fatigue_score",fat,fat is not None and fat>=7,"Self-reported fatigue score is high in this scenario.")
    check("FATIGUE_WORKLOAD","workload",wl,wl is not None and wl>=8,"Reported workload is high in this scenario.")
    sbp=recent.systolic_mmhg; dbp=recent.diastolic_mmhg; glucose=recent.glucose_mg_dl; mood=recent.mood_score; temp=recent.temperature_c
    check("CARDIOVASCULAR","blood_pressure",f"{sbp}/{dbp}" if sbp is not None and dbp is not None else None,(sbp is not None and sbp>=140) or (dbp is not None and dbp>=90),"Blood-pressure value crossed a configurable demonstration review threshold.")
    check("METABOLIC_SIGNAL","glucose_mg_dl",glucose,glucose is not None and (glucose<70 or glucose>200),"Glucose value crossed a configurable demonstration review threshold.")
    check("THERMOREGULATION","temperature_c",temp,temp is not None and (temp>=38.0 or temp<=35.0),"Temperature value crossed a configurable demonstration review threshold.")
    check("BEHAVIORAL_WELLBEING","mood_score",mood,mood is not None and mood<=3,"Self-reported mood score is low in this demonstration scale; follow approved wellbeing procedures.")
    deviations=[]
    for f in ("heart_rate_bpm","spo2_percent","temperature_c","sleep_hours","fatigue_score","workload","systolic_mmhg","diastolic_mmhg","glucose_mg_dl","mood_score"):
        v=getattr(recent,f); st=b.get(f,{})
        if v is not None and st.get("std") and st["std"]>0:
            z=(float(v)-st["mean"])/st["std"]
            if abs(z)>=2.5: deviations.append({"metric":f,"z_score":round(z,2),"baseline_n":st["n"]})
    return {"status":"REVIEW_REQUIRED" if alerts or deviations else "NO_DEMO_ALERTS","alerts":alerts,"agents":agents,"baseline_deviations":deviations,"baseline":b,"explanation":"Explainable prototype rules and descriptive deviations. All alert limits are configurable demonstration triggers, not clinical thresholds or diagnoses; insufficient history is explicitly reflected by missing baseline statistics."}

@app.get("/api/v1/health-summary")
def health_summary(astronaut_id:str="AST-001",authorization:Optional[str]=Header(default=None)):
    current_user(authorization); rows=get_rows(astronaut_id,100)
    return {"astronaut_id":astronaut_id,"latest":rows[0] if rows else None,"reading_count":len(rows),"assessment":assess(rows),"source_counts":{k:sum(1 for r in rows if r.source==k) for k in ["SIMULATED","NASA_RESEARCH","SENSOR","MANUAL"]}}

@app.get("/api/v1/intelligence/assess")
def intelligence(astronaut_id:str="AST-001",authorization:Optional[str]=Header(default=None)):
    u=current_user(authorization); rows=get_rows(astronaut_id,300); result=assess(rows)
    result["astronaut_id"]=astronaut_id; result["method"]="rule-based review + personal descriptive baseline + transparent z-score deviation"; result["prediction_horizon"]="Not available: this prototype does not claim a trained clinical forecasting model."
    audit(u["sub"],"INTELLIGENCE_ASSESSED",astronaut_id)
    return result

ALLOWED_HAZARD_METRICS = {
    "radiation": {"dose_equivalent","dose_rate","neutron_dose","solar_event_flag"},
    "behavioral": {"sleep_hours","sleep_midpoint_shift_hours","fatigue_score","mood_score","workload_score","social_connection_score"},
    "distance": {"one_way_delay_minutes","outage_minutes","queued_messages","onboard_resource_days"},
    "gravity": {"gravity_level_g","balance_score","motion_sickness_score","coordination_score","exercise_minutes","body_mass_kg"},
    "habitat": {"co2_ppm","oxygen_percent","cabin_pressure_kpa","humidity_percent","temperature_c","noise_db","lighting_lux"},
    "immune": {"immune_marker_value","symptom_score","sample_available_flag"},
    "cardiovascular": {"heart_rate_bpm","blood_pressure_systolic","blood_pressure_diastolic","orthostatic_response"},
    "sensorimotor": {"balance_score","gait_score","hand_eye_coordination_score","motion_sickness_score"},
}

@app.post("/api/v1/hazard-observations")
def create_hazard_observation(p: HazardObservationIn, authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    if p.metric not in ALLOWED_HAZARD_METRICS[p.domain]:
        raise HTTPException(422, f"Metric '{p.metric}' is not in the supported vocabulary for domain '{p.domain}'.")
    if p.source in ("NASA_OSDR", "CSA_RESEARCH") and not p.evidence_ref.strip():
        raise HTTPException(422, "Research-sourced observations require a dataset accession, study identifier or source reference.")
    obj=HazardObservation(astronaut_id=p.astronaut_id,domain=p.domain,metric=p.metric,value=p.value,unit=p.unit,
        observed_at=p.observed_at or datetime.now(timezone.utc),source=p.source,evidence_ref=p.evidence_ref,
        context_json=json.dumps(p.context,ensure_ascii=False),created_by=u["sub"])
    with Session(engine) as s:
        s.add(obj); s.commit(); s.refresh(obj)
    audit(u["sub"],"HAZARD_OBSERVATION_RECORDED",p.astronaut_id,f"{p.domain}:{p.metric}; source={p.source}")
    return {"id":obj.id,"astronaut_id":obj.astronaut_id,"domain":obj.domain,"metric":obj.metric,"value":obj.value,
        "unit":obj.unit,"observed_at":obj.observed_at,"source":obj.source,"evidence_ref":obj.evidence_ref,
        "context":p.context,"interpretation":"Stored observation only; no clinical or radiation-risk inference is made."}

@app.get("/api/v1/hazard-observations")
def list_hazard_observations(astronaut_id:str="AST-001",domain:Optional[str]=None,limit:int=Query(100,ge=1,le=1000),authorization:Optional[str]=Header(default=None)):
    current_user(authorization)
    with Session(engine) as s:
        q=select(HazardObservation).where(HazardObservation.astronaut_id==astronaut_id)
        if domain: q=q.where(HazardObservation.domain==domain)
        rows=list(s.exec(q.order_by(HazardObservation.observed_at.desc()).limit(limit)).all())
    return {"astronaut_id":astronaut_id,"count":len(rows),"observations":[{"id":r.id,"domain":r.domain,"metric":r.metric,"value":r.value,"unit":r.unit,"observed_at":r.observed_at,"source":r.source,"evidence_ref":r.evidence_ref,"context":json.loads(r.context_json or "{}"),"created_by":r.created_by} for r in rows],"notice":"Observations are source-labelled and are not automatically interpreted as clinical or operational risk."}

@app.get("/api/v1/hazard-summary")
def hazard_summary(astronaut_id:str="AST-001",authorization:Optional[str]=Header(default=None)):
    current_user(authorization)
    with Session(engine) as s:
        rows=list(s.exec(select(HazardObservation).where(HazardObservation.astronaut_id==astronaut_id).order_by(HazardObservation.observed_at.desc()).limit(2000)).all())
    domains={d:0 for d in ALLOWED_HAZARD_METRICS}
    for r in rows: domains[r.domain]=domains.get(r.domain,0)+1
    return {"astronaut_id":astronaut_id,"observation_count":len(rows),"by_domain":domains,
        "coverage_note":"Counts indicate recorded observations, not hazard safety or completeness. Missing observations must not be interpreted as normal."}

@app.post("/api/v1/mission/link-simulation")
def mission_link_simulation(p:MissionLinkScenarioIn,authorization:Optional[str]=Header(default=None)):
    u=current_user(authorization)
    total_kb=p.queued_messages*p.average_message_kb
    result={"scenario":"DEEP_SPACE_COMMUNICATION_DELAY","one_way_delay_minutes":p.one_way_delay_minutes,
        "round_trip_time_minutes":round(2*p.one_way_delay_minutes,2),"outage_minutes":p.outage_minutes,
        "queued_messages":p.queued_messages,"estimated_queued_payload_mb":round(total_kb/1024,4),
        "message_delivery_after_link_recovery":"queued messages become eligible for transmission; actual transport is not implemented",
        "operational_design_checks":["Use locally cached, approved procedures during link outages","Timestamp and retain local events with provenance","Prioritize and deduplicate queued messages before later synchronization","Require human authority for medical decisions"],
        "limitations":"Arithmetic tabletop scenario only. It does not emulate a network, predict a Mars link, or transmit messages."}
    audit(u["sub"],"MISSION_LINK_SCENARIO","DEEP_SPACE",json.dumps(result)[:500])
    return result

@app.get("/api/v1/digital-twin")
def digital_twin(astronaut_id:str="AST-001",authorization:Optional[str]=Header(default=None)):
    current_user(authorization); rows=get_rows(astronaut_id,200)
    if not rows:return {"status":"NO_DATA","astronaut_id":astronaut_id}
    return {"status":"DESCRIPTIVE_TWIN","astronaut_id":astronaut_id,"latest":rows[0],"baseline":baseline(rows[1:]),"model":"transparent state summary; not a validated physiological simulator","dimensions":["cardiovascular","oxygenation","temperature","sleep","fatigue","workload"]}

@app.post("/api/v1/digital-twin/simulate")
def twin_simulate(p:TwinIn,authorization:Optional[str]=Header(default=None)):
    current_user(authorization); rows=get_rows(p.astronaut_id,200)
    if not rows: raise HTTPException(409,"No telemetry exists for this astronaut. Generate a labelled demo scenario or enter a reading, then retry.")
    last=rows[0]; hours=p.hours
    sleep_gain={"baseline":0,"rest":.0,"reduced_workload":.15,"sleep_extension":1.5}[p.intervention]
    fatigue_delta={"baseline":0,"rest":-1.0,"reduced_workload":-.7,"sleep_extension":-1.5}[p.intervention]
    hr_delta={"baseline":0,"rest":-1.5,"reduced_workload":-2.0,"sleep_extension":-1.0}[p.intervention]
    return {"mode":"COUNTERFACTUAL_SCENARIO","intervention":p.intervention,"horizon_hours":hours,"observed_state":{"heart_rate_bpm":last.heart_rate_bpm,"sleep_hours":last.sleep_hours,"fatigue_score":last.fatigue_score,"workload":last.workload},"illustrative_scenario":{"heart_rate_bpm":round(max(25,(last.heart_rate_bpm or 70)+hr_delta),1),"sleep_hours":round(min(24,(last.sleep_hours or 7)+sleep_gain),1),"fatigue_score":round(min(10,max(0,(last.fatigue_score or 2)+fatigue_delta)),1)},"assumptions":["Linear heuristic deltas selected for demonstration","No causal or physiological validity established","Scenario is not a treatment or operational recommendation"]}

@app.get("/api/v1/mission/brief")
def mission_brief(astronaut_id:str="AST-001",authorization:Optional[str]=Header(default=None)):
    current_user(authorization); rows=get_rows(astronaut_id,100); a=assess(rows)
    return {"generated_at":datetime.now(timezone.utc),"mission":"DEMO-ORBIT","crew_member":astronaut_id,"telemetry_count":len(rows),"data_provenance":{k:sum(1 for r in rows if r.source==k) for k in ["SIMULATED","SENSOR","NASA_RESEARCH","MANUAL"]},"review_status":a["status"],"priority_alerts":a["alerts"],"operational_note":"Human review required. No autonomous medical action is authorized."}

@app.post("/api/v1/copilot")
def copilot(payload:dict,authorization:Optional[str]=Header(default=None)):
    u=current_user(authorization); aid=str(payload.get("astronaut_id","AST-001")); rows=get_rows(aid,100); a=assess(rows)
    findings=[f'{x["agent"]}: {x["finding"]}' for x in a.get("agents",[]) if x["status"]=="REVIEW"]
    answer=("Review the latest available telemetry and verify sensor quality, timestamp, and crew context. " + ("Triggered review items: "+"; ".join(findings) if findings else "No configured demonstration rules triggered in the latest record.") + " This is a transparent, rules-based summary, not a generative medical model or diagnosis. A qualified medical officer must consult mission-approved protocols.")
    audit(u["sub"],"COPILOT_SUMMARY",aid)
    return {"assistant":"ASTRA-MED Copilot (deterministic prototype)","astronaut_id":aid,"summary":answer,"evidence":a.get("alerts",[]),"protocol_retrieval":"Not connected; no protocol was retrieved.","requires_human_review":True}

@app.get("/api/v1/environment/risk")
def environment_risk(astronaut_id:str="AST-001",mission_days:int=180,radiation_rate_msv_day:float=0.5,authorization:Optional[str]=Header(default=None)):
    current_user(authorization)
    if not 1<=mission_days<=2000 or not 0<=radiation_rate_msv_day<=100: raise HTTPException(422,"Scenario inputs out of allowed demo range.")
    rows=get_rows(astronaut_id,1); observed=rows[0].radiation_msv if rows else None
    return {"mission_days":mission_days,"assumed_rate_msv_day":radiation_rate_msv_day,"scenario_cumulative_msv":round(mission_days*radiation_rate_msv_day,2),"latest_reading_msv":observed,"status":"SCENARIO_ONLY","note":"User-configured arithmetic scenario, not a space radiation transport model, dose forecast, or health-risk estimate. Use mission-specific calibrated dosimetry and radiation expertise."}

@app.post("/api/v1/emergency/simulate")
def emergency(p:EmergencyIn,authorization:Optional[str]=Header(default=None)):
    u=current_user(authorization)
    workflows={
      "degraded_telemetry":["Mark affected channel unavailable","Check device power, timestamp and sensor contact","Preserve raw packets and local buffer","Escalate to flight/medical operations per approved procedure"],
      "fatigue_event":["Confirm crew self-report and recent sleep/workload context","Cross-check schedule and sensor quality","Notify medical officer for review","Consider approved workload/sleep scheduling procedures"],
      "oxygen_sensor_alert":["Check sensor validity, fit, calibration and repeat measurement","Cross-check independent source if available","Notify medical officer and mission control","Follow approved mission contingency checklist"],
      "communications_loss":["Switch to onboard cached decision-support view","Queue signed local events for later sync","Use only pre-approved onboard procedures","Log start/end and unresolved events"],
      "combined_contingency":["Prioritize sensor/data integrity checks","Identify which channels are affected and preserve provenance","Notify onboard medical authority and mission control when available","Execute approved emergency checklist; do not rely on this prototype for treatment"]
    }
    audit(u["sub"],"EMERGENCY_SCENARIO",p.scenario)
    return {"scenario":p.scenario,"simulation":True,"recommended_workflow":workflows[p.scenario],"authority":"Human crew/medical officer; follow mission-approved procedures","notice":"Tabletop workflow simulation only. Not an autonomous emergency response or flight-certified system."}

@app.get("/api/v1/audit")
def audit_log(limit:int=Query(50,ge=1,le=500),authorization:Optional[str]=Header(default=None)):
    u=current_user(authorization)
    if u["role"] not in ("admin","mission_control"): raise HTTPException(403,"Role not permitted")
    with Session(engine) as s:return list(s.exec(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)).all())

@app.post("/api/v1/research/datasets/import")
def import_research_dataset(payload: ResearchBatchIn, authorization: Optional[str]=Header(default=None)):
    u=current_user(authorization)
    with Session(engine) as s:
        for row in payload.rows:
            s.add(ResearchDatasetRow(dataset_name=payload.dataset_name, source="NASA_RESEARCH", row_json=json.dumps(row, ensure_ascii=False), imported_by=u["sub"]))
        s.commit()
    audit(u["sub"],"RESEARCH_DATASET_BATCH_IMPORTED",payload.dataset_name,f"rows={len(payload.rows)}; source=NASA_RESEARCH")
    return {"imported":len(payload.rows),"dataset_name":payload.dataset_name,"source":"NASA_RESEARCH","storage":"RAW_RESEARCH_REPOSITORY","message":"Stored as research records, separate from astronaut telemetry. Inspect study context, units, access class and metadata before analysis."}

@app.get("/api/v1/research/datasets")
def list_research_datasets(authorization: Optional[str]=Header(default=None)):
    current_user(authorization)
    with Session(engine) as s:
        records=s.exec(select(ResearchDatasetRow).order_by(ResearchDatasetRow.imported_at.desc()).limit(5000)).all()
    grouped={}
    for row in records:
        item=grouped.setdefault(row.dataset_name,{"dataset_name":row.dataset_name,"source":row.source,"rows":0,"last_imported":row.imported_at})
        item["rows"]+=1
    return {"datasets":list(grouped.values()),"stored_rows":len(records),"notice":"Raw research rows are kept separate from crew telemetry."}

@app.get("/api/v1/nasa/search")
async def nasa_search(term:str=Query(min_length=2,max_length=120),size:int=Query(10,ge=1,le=25),authorization:Optional[str]=Header(default=None)):
    current_user(authorization)
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r=await client.get("https://osdr.nasa.gov/osdr/data/search",params={"term":term,"from":0,"size":size})
            r.raise_for_status(); data=r.json()
        return {"source":"NASA_OSDR","query":term,"data":data,"data_type":"STUDY_METADATA","notice":"Metadata discovery only. No raw files are ingested, harmonized or interpreted as live physiology. Verify accession, cohort, assay, units, data dictionary, permissions and citation."}
    except (httpx.HTTPError,ValueError) as e: raise HTTPException(502,f"NASA OSDR unavailable: {type(e).__name__}")

@app.get("/api/v1/research/benchmark")
def benchmark():
    rng=np.random.default_rng(42); n=1000
    normal=rng.normal(0,1,n); injected=normal.copy(); injected[700:760]+=4.0
    threshold=2.5; pred=np.abs(injected)>threshold; truth=np.zeros(n,dtype=bool); truth[700:760]=True
    tp=int(np.sum(pred&truth)); fp=int(np.sum(pred&~truth)); fn=int(np.sum(~pred&truth))
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0
    return {"dataset":"SEEDED_SYNTHETIC_UNIT_TEST","n":n,"injected_anomaly_window":[700,759],"method":"absolute z-like synthetic signal threshold","threshold":threshold,"confusion":{"tp":tp,"fp":fp,"fn":fn,"tn":n-tp-fp-fn},"precision":round(precision,4),"recall":round(recall,4),"f1":round(2*precision*recall/(precision+recall),4) if precision+recall else 0,"warning":"Not NASA astronaut data, not clinical validation, not evidence of real-world generalization."}
