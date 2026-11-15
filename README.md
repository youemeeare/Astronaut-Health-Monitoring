# ASTRA-MED X v1.0.0 — Astronaut Health Intelligence Demonstrator

A modular research/hackathon demonstrator combining a FastAPI API, React mission-control dashboard and Expo mobile client. It is **not** a clinical device, autonomous medical system, flight-certified system or proof that all NASA human-spaceflight health problems are solved.

## Quick start — Windows

### 1) Backend (Python 3.12 recommended)
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

### 2) Web dashboard (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite, normally `http://localhost:5173`.

### 3) Expo SDK 58 mobile (Node 22.13+)
```powershell
cd mobile
npm install
npx expo install --fix
npx expo-doctor
```
Set the phone-reachable API address before starting Expo. Create `mobile/.env`:
```
EXPO_PUBLIC_API_URL=http://YOUR_PC_LAN_IP:8000
```
Find the PC LAN IP with `ipconfig`. Do not use `localhost` from a physical phone. Allow Python through Windows Firewall on a trusted private network only.
```powershell
npx expo start
```
SDK 58 targets React Native 0.88 and React 19.3.0; confirm installed package compatibility with `npx expo-doctor`. Expo Go availability may differ by platform; use an SDK 58 development build if needed.

## Features

- Mission-control web dashboard with responsive layout, crew profile selector, latest telemetry, trends, review queue and scenario injection.
- Self-assessment form for supported vital signs, sleep, fatigue, mood, hydration, body mass, exercise and workload.
- Five-hazard information center covering radiation, isolation/confinement, distance from Earth, gravity fields and hostile closed environments.
- FastAPI endpoints for profile creation, reading ingestion/listing, health summary, audit events and demo login tokens.
- Separate transparent review agents for heart-rate, oxygen signal, sleep, fatigue/workload; personal descriptive rolling baseline and z-score deviation when enough variance/history exists.
- Digital-twin *state summary* and explicitly heuristic counterfactual scenarios (not validated physiology), with a clear 409 response when no telemetry exists.
- Deterministic medical copilot summary with evidence; protocol retrieval intentionally marked unavailable.
- Radiation arithmetic scenario using operator-supplied rate and mission duration (not radiation transport or dose-risk model).
- Tabletop emergency workflows for comms loss, degraded telemetry, fatigue and oxygen-sensor alert.
- Hazard evidence ledger for source-labelled radiation, behavioral, distance, gravity, habitat, immune, cardiovascular and sensorimotor observations, with a controlled metric vocabulary and separate storage from basic vital-sign readings.
- Deep-space communication-delay/outage scenario calculator (one-way/round-trip delay, queued message count and estimated payload size) with offline workflow guidance. This is arithmetic, not a network emulator or transport layer.
- Mission Data Repository for CSV and JSON files, preview, provenance selection and sequential 250-row API imports (prototype limit: 50,000 rows per selected file). NASA_RESEARCH rows are stored raw in a separate repository; MANUAL/SENSOR/SIMULATED rows can be mapped into crew telemetry.
- NASA OSDR study-metadata search only; no automatic raw-data ingestion, harmonization or conversion to live physiology.
- Explicit NASA data provenance panel separating OSDR metadata, manually imported research, synthetic fixtures and live telemetry (not connected).
- Synthetic benchmark endpoint with seeded test signal and confusion matrix; benchmark is software-fixture behavior, not clinical validation.
- Expo SDK 58 mobile client with demo role selection, summary display, local pending-record queue and manual sync attempt.

## API highlights
- `GET /health`
- `POST /api/v1/auth/demo-login?role=mission_control`
- `GET /api/v1/profiles`, `POST /api/v1/profiles`
- `POST /api/v1/readings`, `GET /api/v1/readings`
- `POST /api/v1/demo/simulate`
- `GET /api/v1/health-summary`
- `GET /api/v1/intelligence/assess`
- `GET /api/v1/digital-twin`, `POST /api/v1/digital-twin/simulate`
- `GET /api/v1/mission/brief`
- `POST /api/v1/copilot`
- `GET /api/v1/environment/risk`
- `POST /api/v1/emergency/simulate`
- `POST /api/v1/hazard-observations`, `GET /api/v1/hazard-observations`, `GET /api/v1/hazard-summary`
- `POST /api/v1/mission/link-simulation`
- `GET /api/v1/nasa/search?term=spaceflight`
- `GET /api/v1/research/benchmark`
- `GET /api/v1/audit`

## Dataset import

Use Mission Data Repository to upload CSV or JSON. CSV headers can use names such as `recorded_at`, `heart_rate_bpm`, `spo2_percent`, `temperature_c`, `sleep_hours`, `fatigue_score`, `systolic_mmhg`, `diastolic_mmhg`, `glucose_mg_dl`, `mood_score`, `workload`, and `radiation_msv`. Download the in-app CSV template for a starter format. Choose the correct provenance before importing. The browser sends records in batches of 250; each batch is committed to the backend database. The current prototype reads the selected file into browser memory, so split very large files rather than treating this as an unlimited streaming pipeline.

NASA OSDR research files may contain omics, phenotypic, physiological, behavioral, biomedical imaging, environmental and other research data. Not every file is a row-based astronaut vital-sign table. Preserve study metadata, units, access restrictions and licenses; do not map arbitrary omics or animal-study data into crew telemetry fields. Controlled-access human-derived datasets require the applicable access request and approval process. NASA OSDR research records are not live crew telemetry.

## NASA data status — read this before presenting

The current application connects to NASA OSDR **study metadata search**. It does not bundle a named NASA raw dataset, train on NASA astronaut data, or receive live astronaut telemetry. NASA HRP pages inform the five-hazard design framework. Candidate research studies and access notes are documented in `docs/NASA_DATA_AND_COMPLEMENTARITY.md`. All generated data remains labelled `SIMULATED`.

## Scientific and safety boundaries — read before presenting
1. All demo-generated telemetry has `SIMULATED` provenance. Never relabel it as NASA or astronaut telemetry.
2. NASA OSDR search returns study metadata. Before any future ingestion, preserve study accession, file ID, original filename, source URL, retrieval time, access/license, cohort/population, assay, units, timepoint, data dictionary, preprocessing code/version and citation. Do not merge heterogeneous omics/clinical datasets as if they were interchangeable vital signs.
3. Alert thresholds are configurable demonstration triggers, not clinical thresholds. Personal baselines are descriptive only and are not a diagnosis.
4. The digital twin is a state summary plus simple what-if arithmetic; it is not a validated human physiological model.
5. Copilot is deterministic and does not retrieve NASA medical protocols. All decisions require qualified human review and approved mission procedures.
6. Radiation output is rate × duration arithmetic only. It is not an organ dose model, transport simulation or health-risk prediction.
7. Emergency workflows are tabletop prompts. They do not command spacecraft, devices or treatment.
8. The benchmark uses a seeded synthetic signal. It does not establish accuracy on astronauts, NASA data or real-world conditions.

This is a research/hackathon demonstrator. Demo rules and scenario calculations are not clinically validated thresholds, medical diagnoses, treatment plans, or flight-qualified decision systems. Actual sensor, NASA operational data, clinical protocol, identity provider, production encryption, hardened audit retention, server-side streaming imports, and operational validation are not included merely by the presence of these interface modules.

## Authentication / security status
Demo login is deliberately open while `ASTRA_DEMO_MODE=true`; it is for a local hackathon demonstration only. Token signing is a small stdlib HMAC demonstration and is not a substitute for an institutional OIDC/SSO provider, managed secret storage, key rotation, MFA, production authorization policy, TLS, encryption at rest, hardened audit storage, rate limiting or independent security review. Set `ASTRA_DEMO_MODE=false` only after implementing and testing a real identity provider; otherwise no login path is provided.

Do not enter real astronaut, patient or other sensitive health data. For real-world use, require ethics/governance approvals, NASA/partner data authorization, validated devices, human-factors testing, hazard analysis, clinical validation, flight software assurance, cybersecurity verification, operational safety case and mission authority approval.

## Test
```powershell
cd backend
pytest -q
```
No external NASA service availability is guaranteed. Network failures should be presented as unavailable, not as zero-risk or zero-data.

## Release status
v1.0.0 is a functional research prototype. It is not independently audited or certified.
