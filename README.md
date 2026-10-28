# Dealer Action Planner

A local Streamlit prototype helping a regional manager prioritise weekly dealer reviews. The initial data is simulated; managers can append their own weekly CSV rows through the sidebar. Recommendations support human decisions; nothing is sent or executed automatically.

## Demo video

[Watch or download the recorded prototype walkthrough](https://github.com/vaishnavmahendrakar25m-bot/dealer-action-planner/raw/refs/heads/main/presentation/dealer-action-planner-demo.mp4) · MP4, 13.1 MB.

The walkthrough demonstrates the Dealer Action Planner using simulated data.

## Run

Python 3.11+ (built with 3.13.5).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --browser.gatherUsageStats false
```

Open the local URL printed by Streamlit. First run generates 30 dealers and 24 weeks with seed 42. No network is needed after dependencies are installed. The default database is `data/dealer_planner.db`; `DEALER_DB` can select another project-local database.

## Add weekly data

In the left sidebar, open **Your data → Load weekly data**. Download the blank CSV template, fill its exact columns using an existing `dealer_id` from `examples/sample_dealers.csv`, and upload it. The app reports clean and rejected rows before saving. It accepts only missing dealer rows in the latest week or rows for the immediately following week; it never replaces an existing dealer-week. The default demo ends at week 24, so week 25 is the first new week. All other historical rows remain simulated and the UI labels this mixed source after import. Simulation advance is paused after import. Reset can return to the demo after an explicit confirmation; preserve a copy of the database first if you need your uploaded rows.

## Demo

Start at week 24 and region All. Open Needs action, Sri Venkateshwara Motors, inspect evidence and accept the plan. Inspect Charminar Wheels and Nizam Auto for patterns, then Kaveri Cars under Doing well for the context adjustment. Try the stock-transfer slider. Open My actions, then use Advance one week. Reset through the sidebar to return to seed 42; resetting clears saved actions after explicit confirmation.

## Tests

```bash
source .venv/bin/activate
pytest -q
```

Real results are recorded in `docs/PROGRESS.md` and evidence files. Do not interpret a missing report as a pass.

## Architecture

`simulator → SQLite → rolling indicators → context and pattern checks → classification → draft playbook → Streamlit → saved action → follow-up`

Business logic lives in `planner/` and imports without Streamlit. Defaults and rule references come from `docs/CONTEXT.md`. The UI uses deterministic summaries, fixed source defaults and SQLite persistence.

## Submission scope and limitations

The owner prioritised a workable prototype by 01:00 IST on 29 October. Core screens, human decisions, simulator controls, transfer scenarios and local weekly CSV import are included. Public deployment, the extended settings editor and full export/digest accounting remain deferred. The digest is a display-only Home preview. No external AI exists.

Synthetic parameters and thresholds are demonstration assumptions, not benchmarks. Patterns are worth checking, not proof of intent or causation. Unknown transfer permissions, financing conditions and fees stay pending; scenario economics are not realised savings. Browser/mobile verification and acceptance results must be checked in the final report.
