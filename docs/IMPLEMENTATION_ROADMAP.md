# ASTRA-MED X v1.0.0 status

This release contains working prototype modules for the features listed in the README. Read `NASA_PROBLEM_MAPPING.md` for the exact scope and unimplemented operational requirements.

## Current status
- Mission control web dashboard: implemented in frontend.
- API profiles/telemetry/demo roles/audit: implemented in backend.
- Rule-based explainable multi-domain review and descriptive baselines: implemented.
- Digital twin: descriptive state summary + heuristic scenario only.
- Copilot: deterministic summary; no LLM or protocol retrieval.
- Space environment: dose-rate × duration arithmetic only.
- Emergency mode: tabletop checklists only.
- NASA OSDR: study metadata search only; no dataset ingestion.
- Mobile: Expo SDK 58 client with local secure-store queue and manual sync starter.
- Security: demo identity only; not production authentication.
- Validation: unit tests and synthetic benchmark fixture included; no astronaut/clinical validation.

## Next work after local install
1. Run backend tests and API smoke tests.
2. Build frontend and mobile on target machines.
3. Add authenticated, encrypted, durable offline queue with conflict/retry semantics.
4. Integrate a real identity provider and policy-enforced RBAC.
5. Select one NASA OSDR study and create a study-specific, provenance-preserving ingestion pipeline.
6. Replace heuristics with models trained/evaluated on authorized representative data.
7. Conduct formal hazard analysis, human-factors testing, cybersecurity review and independent validation.
