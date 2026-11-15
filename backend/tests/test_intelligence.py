from datetime import datetime, timezone
from app.main import Reading, assess, baseline

def test_empty_assessment_is_explicit():
    result = assess([])
    assert result["status"] == "NO_DATA"
    assert result["alerts"] == []

def test_alert_has_explanation_and_provenance_guardrail():
    row = Reading(astronaut_id="T", recorded_at=datetime.now(timezone.utc),
                  heart_rate_bpm=110, spo2_percent=98, source="SIMULATED")
    result = assess([row])
    assert result["status"] == "REVIEW_REQUIRED"
    assert any(a["metric"] == "heart_rate_bpm" for a in result["alerts"])
    assert "not a clinical threshold" in result["alerts"][0]["evidence"]

def test_baseline_reports_sample_count():
    rows = [Reading(astronaut_id="T", recorded_at=datetime.now(timezone.utc),
                    heart_rate_bpm=x, source="SIMULATED") for x in [60, 62, 64]]
    b = baseline(rows)
    assert b["heart_rate_bpm"]["n"] == 3
    assert b["heart_rate_bpm"]["mean"] == 62.0
