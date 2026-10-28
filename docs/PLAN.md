# Stage 0 plan

Weekly RM decision support across 30 simulated dealers, three regions, 24 weeks; transparent six-indicator scoring, urgent overrides, context fairness, separate pattern flags, strict group precedence, phone-first flow, saved human decisions, transfer scenarios, CSV validation and digest preview.

Modules: app.py (UI); planner/config.py (defaults); db.py (SQLite); simulator.py (seeded data); engine.py (indicators, scores, context, patterns, snapshots); playbooks.py (recommendations); transfers.py (matching/economics); kpis.py (reconciled totals); narrative.py (templates); actions.py (decisions/follow-up); ingest.py (CSV); digest.py (preview). tests/ covers pure rules and integration; scripts/ produces reproducible evidence; examples/ stores actual outputs. README, ASSUMPTIONS, DEMO_SCRIPT, PITCH_QA, PITCH_90S document the prototype.

Flow: simulator/validated CSV → SQLite → indicators → context/pattern checks → classification → playbooks → UI/digest → decisions → follow-up.

Build in guide order 1–17; audit again after pitch preparation. Highest risks: simulator acceptance tuning, context precedence, stale/partial data, history and deferrals, mobile layout. Approved amendments override previous ambiguity defaults. No external AI or services.

## Deadline scope revision — 29 October, 00:15 IST

Owner prioritises a workable submission prototype by 01:00 IST. Implement core Home/list/case/actions, simulator controls, transfer scenario, core tests and pitch documentation first. Defer CSV import/export, deployment, extended settings editor, and comprehensive audit extras if needed. Keep all approved business rules. Record unimplemented checks honestly; do not label deferred stages complete.
