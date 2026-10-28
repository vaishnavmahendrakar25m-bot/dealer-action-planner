# Decisions

- A1: section 11.1 rule 9
- A2: section 9 recovery
- A2: section 11 precedence
- A3: section 7.5 simulator tuning
- A3: Coastal parameters
- A3: Marina parameters
- A4: section 7.2 action fields
- A5: section 9 new outlet
- A6: 10. Hidden-risk
- A6: 7.6
- A7: 7.2
- A7: 7.7
- A7: 13. Stock-transfer
- A8: section 20 partial weeks
- A8: week validation
- A9: section 6.5 dates and deferrals
- A9: section 7.1 dates
- A10: simulator reference
- A10: transfer reference
- A10: section 6.1 counts
- A10: section 19 Python
- A11: section 8.1 custom settings
- A11: section 15 deterministic summaries

The attachment has no Completion Protocol; the user-message protocol governs. Optional external AI is excluded. No global environment changes.

## Stage 4 candidate simulator tuning (pending verification)

- Marina: onset 19, ramp 8, intensity 0.85, to produce deterioration at week 24.
- Coastal: onset 20, ramp 4, intensity 0.59; below severe-complaint threshold.
- Market dip: aged-share effect 0.19 rather than 0.08, to make raw concern visible while context-adjusted concern remains Routine.
- Disputed invoices and new outlet: add 0.19 aged-share effect, to satisfy raw index >=35 without changing scoring.
- Recovery decline: (27-week)/7 rather than (30-week)/10, for a sufficiently strong four-week improvement.
- Healthy-dealer retail noise SD 0.025, overdue noise SD 0.004, prior-year retail noise SD 0.02, to avoid noise-driven recovery labels.
- Scoring rules, weights, bounds and thresholds unchanged.

## Verification environment

Python imports began taking minutes while reading installed NumPy/PyArrow/pandas files. Process samples show file reads during import, before scoring execution. Restart and alternate project-local bytecode cache tried. Stage 4 is not complete until its checks pass.

The exact approved wording and section edits are recorded in approved_amendments.diff.
Second tuning pass: Marina onset 21, ramp 4, intensity 0.75 (still rising in week 24); disputed-invoice aged-share effect 0.20 to cross the raw 35-point condition. Scoring unchanged.

## Deadline revision approved by owner

Prioritise the workable submission prototype, target 01:00 IST, 29 October. Defer complex CSV ingestion/export UI, deployment, extended settings editing and comprehensive extras. Core rules remain unchanged. The reduced scope supersedes strict completion of all seventeen stages. Real tests and browser evidence remain required; deferred features will be listed in FINAL_REPORT.md.

Focused test invocation disables optional pytest plugin auto-loading; application business logic does not need anyio's pytest plugin. The ten-test run passed in 3.03 seconds; report saved in examples/test_report.txt. A further partial-week test and edited due-date review calculation will be rerun before final delivery.

Home and case summaries now avoid eager Altair imports: Evidence includes an explicit chart checkbox. This preserves evidence charts while keeping the core review journey independent of their first-load delay. KPI tiles now show previous-period changes. Status badges use colour and text.

The project-local pytest rerun initially failed because .venv/test-runs did not exist; creating its parent resolved the harness error. Subsequent run: 11 passed in 3.72 seconds. No business-rule change was involved.

Final polish: Doing well cards are grouped as Better than they look, Room to grow, Stars. Rounded action-baseline displays; unavailable values are labelled. Added spaces before pp/complaints units. Chart data is limited to week and score so simulation validation labels are never passed to the chart UI. No scoring changes.

Release test transparency: the persistent core-test process used NumPy/pandas with optional PyArrow import disabled to get past the cold-import delay; all eleven core tests ran without skips. Streamlit browser checks used the actual installed PyArrow and verified calculated results, tables and charts independently. This is a focused prototype validation, not a complete production audit.
