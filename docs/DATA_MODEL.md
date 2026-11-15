# ASTRA-MED X v1.0.0 data model

## Reading — crew telemetry / self-report
- Crew profile key and UTC timestamp
- Optional physiological, sleep, fatigue, wellness and cabin indicators
- Provenance: `SIMULATED`, `SENSOR`, `MANUAL` or legacy `NASA_RESEARCH` (new research imports should use the separate raw research table)

## ResearchDatasetRow — heterogeneous research records
- Dataset name, source, raw JSON row, import timestamp and importing actor
- Kept separate from crew `Reading` rows; the row is not automatically normalized into vital signs

## HazardObservation — structured evidence ledger
- Crew/profile key, hazard/research domain, controlled metric key, numeric value, unit and observed timestamp
- Source: `MANUAL`, `SENSOR`, `SIMULATED`, `NASA_OSDR` or `CSA_RESEARCH`
- Evidence/accession reference and JSON context
- This entity stores observations only; it does not produce a diagnosis, risk score or safety determination

## Domains and metric vocabulary
See `ALLOWED_HAZARD_METRICS` in `backend/app/main.py`. Domains include radiation, behavioral, distance, gravity, habitat, immune, cardiovascular and sensorimotor. The vocabulary is intentionally limited and should be extended only with a documented definition, unit, source and validation rule.

## Research ingestion rule
For each future NASA dataset, retain accession, file identifier, original filename, source URL, retrieval timestamp, license/access classification, study population, assay/modality, units, timepoint, data dictionary, preprocessing version and citation. Do not combine measurements across studies until units, protocol, cohort and semantics are verified. Controlled-access human-derived data require the applicable authorization.
