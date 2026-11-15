# ASTRA-MED X v1.0.0 — NASA problem mapping and honest limits

ASTRA-MED X is a student-built research demonstrator exploring a provenance-aware evidence workspace, transparent review logic and delay-aware workflow scenarios. NASA already operates medical operations and crew-health support capabilities. This project is not a replacement and does not claim that NASA lacks a medical system.

| NASA human-spaceflight hazard / risk area | ASTRA-MED X contribution | Actual implementation status | Remaining gap |
|---|---|---|---|
| Space radiation | Radiation observation domain and existing rate × duration arithmetic | Source-labelled observation storage; user-configured arithmetic only | Calibrated dosimeter feed, particle spectrum, shielding/trajectory and organ-dose modelling; no CANS hardware link |
| Isolation & confinement | Sleep, fatigue, mood, workload fields plus behavioral evidence domain | Basic self-report and observations | Validated behavioral instruments, circadian phase/light exposure, team dynamics and longitudinal validation |
| Distance from Earth | Deep-space delay/outage calculator and emergency comms-loss tabletop | Deterministic delay arithmetic and workflow checklist | Actual network emulator, resilient encrypted queue, retry/deduplication/conflict handling and fault-injection testing |
| Gravity fields | Gravity and sensorimotor observation domains | Data-entry/ledger support for balance, coordination, motion-sickness and exercise indicators | Validated instruments, longitudinal bone/muscle data, vestibular test protocols and gravity-transition model |
| Hostile/closed environments | Habitat observation domain and existing CO₂/humidity/temperature fields | Data-entry support; limited current telemetry fields | Actual O₂, pressure, acoustics, lighting, microbial sampling and sensor integrations |
| Immune / cardiovascular | Additional research domains; existing HR/BP indicators | Observation storage and selected vital-sign capture | Dataset-specific assay interpretation, longitudinal cohorts and expert validation |
| Research traceability | OSDR metadata search plus raw research repository | Metadata search connected; manual CSV/JSON import preserves raw rows | Automated file-level ingestion, metadata harmonization, access governance and reproducible analysis |

## NASA data status — exact wording
- Connected: NASA OSDR study metadata search endpoint.
- Used as design references: NASA Human Research Program five-hazard and risk material.
- Not connected: live NASA astronaut telemetry, ISS medical systems, CANS neutron sensor or any operational NASA device feed.
- Not bundled/training: no named raw NASA study accession is bundled or used to train/validate the models in this release.
- Team may manually import public/authorized OSDR files. Research rows remain separate from crew telemetry.
- Synthetic test fixtures remain `SIMULATED`; never describe them as NASA data.

## What we can claim instead of “NASA system drawbacks”
NASA's own public documentation describes established medical operations, flight surgeons and biomedical flight controllers, and downlinked physiological, dosimetry, exercise and environmental information. NASA also documents inherent constraints of spaceflight medical operations, including limited stowage, possible ground-communication disruptions, radiation exposure and functional limitations in microgravity. These are mission/environment constraints, not evidence of an inferior NASA system.

A credible project contribution is to demonstrate, in a small student prototype, how one workspace can keep heterogeneous research evidence separate from crew telemetry, make provenance and missingness visible, record observations across all five hazard domains, and rehearse delay-aware information workflows. This is complementary exploration, not a claim of superiority or replacement.

## Judging metrics
Report measured results only: API response times under a stated setup, data import success and row counts, source-provenance completeness, number of scenarios tested, communication-delay arithmetic checks, offline queue behavior actually tested, and confusion matrix metrics on explicitly labelled synthetic test cases. Do not call synthetic precision/recall astronaut model accuracy.

## Explicit non-claims
- Not a NASA medical system replacement.
- Not clinical diagnosis, treatment, autonomous triage or flight-certified software.
- Not a validated physiological digital twin.
- Not live astronaut telemetry or a live CANS connection.
- Not a radiation transport, neutron dosimetry or organ-dose model.
- Not a network emulator; communication delay lab is arithmetic only.
- Not proof of clinical efficacy or superiority to NASA systems.
