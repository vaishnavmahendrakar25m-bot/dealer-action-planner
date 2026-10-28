# Build progress — revised submission scope

The owner changed the goal to a workable prototype by 01:00 IST on 29 October. Deferred work below is intentional and is not claimed complete.

| Stage | Status | Actual evidence |
|---|---|---|
| 0 | Complete | PLAN.md; approved amendments and DECISIONS.md |
| 1 | Complete | stage1_evidence.txt: 2 passed |
| 2 | Complete | stage2_evidence.txt: 4 passed; stage2_preview.txt |
| 3 | Complete | stage3_evidence.txt: 6 passed; stage3_table.txt |
| 4 | Core complete | detection_week24.txt; seeded-group test passes in final suite |
| 5 | Core complete | transfer example, matching and KPI reconciliation tests pass |
| 6 | Complete | deterministic summary tested; no external AI |
| 7 | Core complete; browser verified | app compiles; Streamlit server started on 127.0.0.1:8501 |
| 8 | Core complete; browser verified | card groups/order calculated from snapshot |
| 9 | Core complete; browser verified | case facts, evidence, context and optional chart loading |
| 10 | Core complete; backend and browser verified | saved actions, duplicates, verdicts, urgent/deferral return tests pass |
| 11 | Core controls complete and browser verified | advancement, event timing and history preservation tests pass; settings editor deferred |
| 12 | Local CSV import added later | Weekly upload validates rows, rejects duplicates and displays partial-week Fix data; export-to-folder UI remains deferred |
| 13 | Basic preview implemented | Home top-five display-only preview; extended digest accounting deferred |
| 14 | Core complete | compilation, wording audit, 390×844 Home fit and core browser journey verified |
| 15 | Core submission package complete | README, ASSUMPTIONS, DEMO_SCRIPT, actual week24/week25 queues, sample CSVs, headline case, test report |
| 16 | Focused audit complete | core_audit.txt; full original audit not claimed |
| 17 | Complete for prototype | PITCH_QA.md: 15 questions; PITCH_90S.md: timed script and backup |

Final current test evidence: examples/test_report.txt — 11 passed in 3.72 seconds, exit 0. Optional pytest plugin auto-loading disabled. All core business logic tests ran; no tests were skipped.

An initial rerun with a project-local test directory failed because its parent directory was absent. Created the parent, reran, and all 11 passed. This was a harness setup error; rules were unchanged.

Local dependency imports were unusually slow. Restart, alternate local bytecode cache and process sampling were used to diagnose the delay. Persistent Python execution enabled verification. Streamlit startup succeeded at 00:26:45 IST; app display verification remains pending. Evidence charts now load only when requested, reducing initial imports.

## Release verification

Final suite: 11 passed in 4.60 seconds, exit0; actual output in examples/test_report.txt. Focused audit: core_audit.txt. Browser evidence: BROWSER_VERIFICATION.md. Core tests ran in a persistent NumPy/pandas process with optional PyArrow import disabled and optional pytest plugin auto-loading disabled; the actual Streamlit UI was separately tested with installed PyArrow. All eleven tests ran; none skipped. The full original seventeen-stage product remains intentionally reduced per owner deadline instruction.

## Later UI and data update

Home now uses a project-local automotive image and keeps both main decision buttons visible at 390px width. The Doing well screen directly filters Better than they look, Room to grow and Stars. The sidebar now offers a weekly CSV upload. The new importer checks exact columns, dealer IDs, dealer-week duplicates, dates and amount relationships, then appends only clean rows. Uploaded weeks are labelled alongside simulated history. Simulator advance and transfer scenarios pause after upload because vehicle and demand data remain simulated. A focused browser check showed the upload form and the corrected Home; phone geometry showed both main buttons by 309px with no horizontal overflow. The first 13-test run after the importer was added passed in 651.54 seconds; a later final rerun was started after the last UI edits.
