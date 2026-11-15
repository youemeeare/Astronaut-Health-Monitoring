from pydantic import ValidationError
import pytest
from app.main import HazardObservationIn, MissionLinkScenarioIn, ALLOWED_HAZARD_METRICS

def test_hazard_metric_vocabulary_has_all_eight_domains():
    assert set(ALLOWED_HAZARD_METRICS) == {"radiation", "behavioral", "distance", "gravity", "habitat", "immune", "cardiovascular", "sensorimotor"}

def test_hazard_observation_accepts_source_and_evidence_context():
    item = HazardObservationIn(domain="radiation", metric="dose_equivalent", value=0.2, unit="mSv", source="SIMULATED", evidence_ref="DEMO-ONLY")
    assert item.domain == "radiation"
    assert item.source == "SIMULATED"
    assert item.context == {}

def test_hazard_observation_rejects_unknown_domain():
    with pytest.raises(ValidationError):
        HazardObservationIn(domain="unknown", metric="anything", value=1, unit="x")

def test_link_scenario_caps_one_way_delay_at_twenty_minutes():
    item = MissionLinkScenarioIn(one_way_delay_minutes=20, outage_minutes=15, queued_messages=4, average_message_kb=5)
    assert item.one_way_delay_minutes == 20
    assert 2 * item.one_way_delay_minutes == 40
    with pytest.raises(ValidationError):
        MissionLinkScenarioIn(one_way_delay_minutes=21)
