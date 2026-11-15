# Mission Data Repository

## Supported input formats
- CSV with a header row
- JSON array of records, or an object with a `records` or `data` array

## Import behavior
1. The browser reads the selected file and previews its first five records.
2. The operator selects a provenance label: `NASA_RESEARCH`, `MANUAL`, `SENSOR`, or `SIMULATED`.
3. `NASA_RESEARCH` rows are preserved as raw JSON in a separate research repository using `POST /api/v1/research/datasets/import`; they are never inserted into crew telemetry. Original column names and row values are retained.
4. `MANUAL`, `SENSOR`, and `SIMULATED` rows are normalized to supported ASTRA-MED fields and submitted to `POST /api/v1/readings/bulk` in batches of 250.
5. The API validates telemetry records using the same bounds as the single-reading endpoint and commits each batch.
6. The audit log records a bulk import event. Research dataset summaries are available from `GET /api/v1/research/datasets`.

The prototype UI limits each selected file to 50,000 rows. This is a browser-side file-read workflow, not a server-side streaming or resumable background job. NASA research rows are deliberately isolated from the astronaut telemetry table so heterogeneous study data cannot silently appear as crew vital signs. A production implementation should use multipart/resumable uploads, object storage, queue workers, checksums, schema-versioned metadata, import rollback/retry, and dataset-level access controls.

## Supported normalized fields
`recorded_at`, `heart_rate_bpm`, `spo2_percent`, `temperature_c`, `sleep_hours`, `fatigue_score`, `workload`, `radiation_msv`, `systolic_mmhg`, `diastolic_mmhg`, `glucose_mg_dl`, `mood_score`, `hydration_ml`, `weight_kg`, `exercise_minutes`, `cabin_co2_ppm`, `cabin_humidity_percent`, `cabin_temperature_c`.

## NASA OSDR data caution
OSDR includes heterogeneous study data (including omics, animal/model-organism studies, physiological/behavioral measures, imaging, environmental and hardware data). Do not assume every OSDR file represents human crew telemetry or is compatible with this vital-sign schema. Retain accession, study title, organism/subject, assay, units, release/version, license/access class, source URL and collection context in a future dataset-level metadata model. Controlled-access data must only be used after the repository's approval process.
