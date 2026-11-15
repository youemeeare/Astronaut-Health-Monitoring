# ASTRA-MED X v1.0.0 — five-person work split

| Member | Ownership | Concrete deliverables |
|---|---|---|
| 1 — Systems integration lead | Architecture, integration, release | API contract review, Git branches/PRs, end-to-end test, deployment, demo script, risk/limitations review |
| 2 — Frontend engineer | React dashboard | Five-hazard evidence entry/ledger UI, deep-space link lab UI, responsive QA, accessible labels and clear provenance display |
| 3 — Backend/data engineer | FastAPI, SQLModel, database | HazardObservation model/routes, schema validation, source metadata, database migration/startup check, API tests |
| 4 — AI/research engineer | Explainable analysis | Define non-diagnostic trend/quality checks, test on synthetic data, report precision/recall only on labelled test sets; no unvalidated clinical claims |
| 5 — NASA research/validation engineer | NASA sources, datasets, evidence | Verify candidate OSDR accessions and file metadata, prepare data dictionary, map modalities without mixing them, write hazard-to-evidence traceability and test cases |

## Integration contract

- `Reading` is for supported crew telemetry records.
- `ResearchDatasetRow` is for raw heterogeneous research records.
- `HazardObservation` is for source-labelled hazard-domain observations; it does not imply the source is a NASA operational feed.
- `SIMULATED`, `MANUAL`, `SENSOR`, `NASA_OSDR` and `CSA_RESEARCH` provenance labels must never be silently changed.
- All pull requests must include a test or a manual test procedure and state what has not been validated.
- Only the integration lead merges to the release branch after the member responsible for that module approves the change.
