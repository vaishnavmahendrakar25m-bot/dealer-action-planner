Dealer Action Planner — prototype release

The working prototype is ready for the revised submission scope and is running at http://127.0.0.1:8501. It is left on Home, seed 42, week 24, with a clean action list.

Project folder:
/Users/biren/Documents/Codex/2026-10-28/you-are-setting-up-a-new/dealer_action_planner

Delivered: Home with five KPIs; grouped dealer lists; case evidence and charts; raw/context-adjusted scores; saved plans and follow-up; simulator controls; transfer scenarios; a basic display-only digest; setup notes, assumptions, demo scripts, judge Q&A and actual-data example files.

Verification:

| Check | Result |
|---|---|
| Core automated suite | 11 passed in 4.60s; exit 0 |
| Dealer A calculation | 56.9 |
| Transfer worked example | INR14,795 avoided; INR6,795 net; 24.3 days break-even |
| Seeded dealer groups | Expected week-24 groups verified |
| Home counts | 8 Needs action; 22 Doing well |
| Missing/stale data | Incomplete; no silent reweighting or older-row backfill |
| Save plan → My actions | Verified in browser |
| Kaveri context | Raw37.0 → adjusted23.7 verified in browser |
| Transfer slider | Positive and negative scenarios verified |
| Phone Home | 390×844; both buttons visible; no horizontal overflow |
| Advance/reset | Week25 counts7/23; reset restored week24 counts8/22 |
| Evidence charts | Both visualizations rendered |

The core test process disabled optional PyArrow imports and optional pytest plugin auto-loading to work around unusually slow cold imports. The actual Streamlit UI was separately verified with installed PyArrow, including its calculated results, tables and charts. No tests in the core suite were skipped.

The later prototype update added a car-themed Home header, direct Doing well filters and validated local weekly CSV upload. CSV export-to-folder UI, public deployment, the extended settings editor and full digest accounting remain deferred. The full original seventeen-stage audit is therefore not claimed complete. No external AI is used.

All data and thresholds are demonstration assumptions. Transfer results are scenarios, not realised savings. Unknown conditions remain pending. Keep the running app open before the pitch; first dependency loading on this computer was unusually slow.

To restart later, double-click Run Planner.command in the project folder, or activate .venv and run: streamlit run app.py
