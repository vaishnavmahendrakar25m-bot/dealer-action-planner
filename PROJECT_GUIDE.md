# Dealer Action Planner — Project Guide

## 1. What this project does

A local Streamlit prototype for a regional manager's weekly dealer review. It shows which dealers need attention, the evidence behind each case, a proposed action with an owner and due date, and saved actions for follow-up.

The initial data is simulated. You can append local weekly CSV rows; the app labels the resulting mix of simulated history and uploaded rows. Scores and summaries use deterministic rules. The app does not send messages, change credit limits, execute transfers, or call external AI.

## 2. What is included in the ZIP

The ZIP contains one folder named `dealer_action_planner`. Keep its contents together.

| Item | Purpose |
|---|---|
| `app.py` | Streamlit application |
| `planner/` | Simulator, scoring, classification, recommendations, KPIs, actions and transfers |
| `requirements.txt` | Five direct dependencies pinned to the versions used for this prototype |
| `.streamlit/config.toml` | Local server and appearance settings; included even though the folder is hidden |
| `data/dealer_planner.db` | A consistent snapshot of the simulated database at packaging time |
| `docs/` | Authoritative context, approved amendments, plan, progress and verification evidence |
| `tests/` | Automated checks |
| `scripts/` | Example generation and focused audit tools |
| `examples/` | Actual calculated queues, sample CSVs, headline case and recorded test output |
| `README.md`, `ASSUMPTIONS.md` | Setup, architecture, formulas and demonstration assumptions |
| `DEMO_SCRIPT.md`, `PITCH_90S.md`, `PITCH_QA.md` | Presentation walkthrough and judge questions |
| `FINAL_REPORT.md` | Report from the prototype build; its original local folder path is historical |
| `PROJECT_GUIDE.md` | This guide |
| `Run Planner.command` | Mac launcher, usable after the environment is installed |
| `PACKAGE_MANIFEST.sha256` | Integrity hashes for the packaged files |

The ZIP intentionally excludes `.venv`, Git history, temporary work, bytecode and test caches. A virtual environment must be created separately on each computer. Application source, tests, documentation, examples and simulated data are included.

## 3. Setup on another computer

Use Python **3.13**, preferably the tested version **3.13.5**. Git, a database server, API keys and paid accounts are not needed. Internet is needed to download the packages during installation; normal local use does not need internet afterward.

1. Copy the ZIP to the other computer.
2. Extract the entire ZIP. Do not run the app from inside the ZIP viewer.
3. Open a terminal in the extracted `dealer_action_planner` folder. This is the folder containing `app.py` and `requirements.txt`, not its parent.
4. Run the commands for that computer below. Use the included pinned requirements rather than installing arbitrary newer versions.

### Windows — PowerShell or Command Prompt

Check Python:

```powershell
python --version
```

Create the environment, install packages and run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

If `python` is not recognised but the Python launcher is installed, use `py -3.13 --version` and `py -3.13 -m venv .venv` for the first two Python commands. The `.venv` commands stay the same. These commands do not require PowerShell activation scripts.

### Mac or Linux

Check Python:

```bash
python3 --version
```

Create the environment, install packages and run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

If several Python versions are installed, use `python3.13 -m venv .venv` to select Python 3.13 explicitly.

### Open the application

Open **http://127.0.0.1:8501** in a browser on that same computer. Keep the terminal running while using the app. Press **Ctrl+C** in the terminal to stop it.

This is a local installation. The included configuration binds to that computer's loopback address. It does not publish a public website, and another computer cannot use your localhost URL to reach it.

Allow enough time to install and open the app before presenting. Installation depends on the connection and computer. First imports were unusually slow on the original computer; open the app in advance and leave it running.

## 4. Starting it again later

Open a terminal in the extracted folder and run only the appropriate last command above. You do not need to recreate the environment or reinstall packages every time.

On a Mac, `Run Planner.command` is an additional launcher after setup. If the ZIP extractor did not preserve its executable permission or macOS will not open it, use the terminal command above instead.

## 5. Data and the clean demo state

The included database preserves the simulated data and any saved actions present when this archive was made. It is a snapshot; actions subsequently saved on the original computer are not copied automatically.

For the standard presentation, use the sidebar: **Reset simulation → Seed 42 → tick the explicit confirmation → Reset**. This regenerates the simulation and clears saved actions in that copy. It returns to week 24. Keep a copy of the database first if you need its saved actions.

With seed 42, week 24 and Region All, the verified prototype shows **8 Needs action** and **22 Doing well**. Week 24 ends on **25 October 2026**, a simulated date independent of the computer's current date. If the database is absent, the app creates one on first run.

The database is `data/dealer_planner.db`. Saved actions persist there across normal app restarts. Keep the folder writable and close the app before manually moving its database.

## 6. Suggested demo journey

1. **Home:** show the five KPIs, data date and Simulated data label.
2. **Needs action → Sri Venkateshwara Motors:** explain that sales above target do not override overdue payments. Show the Urgent label, evidence, owner and due date.
3. **Evidence:** open the indicator table; tick **Show trend and retail charts** to load the two charts.
4. **Accept plan → Home → My actions:** show that the manager's decision was saved with baseline metrics.
5. **Needs action → Charminar Wheels or Nizam Auto:** show a pattern worth checking and the underlying evidence.
6. **Doing well → Kaveri Cars → Context check:** show raw score about 37.0 versus adjusted score about 23.7.
7. **Headline case → Stock transfer option:** move the days-to-sell slider. Explain that the result can become negative and that unknown conditions remain pending.
8. **Advance one week:** week 25 refreshes KPIs and lists. In the verified default simulation, counts become 7/23 and Deccan Wheels changes from Elevated to Routine. Nizam Auto's overdue rebounds.

Use the included 90-second script for rehearsal. The Home wireframe values in CONTEXT are illustrative; the app calculates its displayed values from the simulated data.

## 7. How decisions and scores work

Six indicators cover sales attainment, growth relative to market, aged stock, overdue payments, on-time service and complaints per 100 jobs. Their weights are 15%, 10%, 20%, 25%, 15% and 15%.

The score is supporting evidence. Urgent overrides apply to unresolved severe complaints or non-disputed overdue of at least 20%. Context checks cover market weakness, disputed invoices, new outlets and recovery. Separate pattern flags do not add points to the weighted score. Missing/stale components are marked incomplete and never silently reweighted.

The manager accepts, changes, defers or records another decision. A non-urgent deferral returns on a five-point adjusted-score worsening or an urgent rule. The app records escalations; it does not execute them. All defaults and approved amendments are documented in `docs/CONTEXT.md` and `docs/DECISIONS.md`.

## 8. Testing and evidence

The build's recorded core run passed 11 tests. See the supplied test report and browser verification notes for the actual validation conditions; this is a prototype audit, not a production certification.

To run the suite on the destination computer:

Windows PowerShell:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
.venv\Scripts\python.exe -m pytest -q
```

Mac/Linux:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q
```

Disabling optional plugin auto-loading avoids loading unrelated test integrations; it does not skip this project's tests. A destination computer has not been tested merely because the archive was verified here. Review the real result from that computer.

## 9. Add your own weekly data

To add your own weekly figures, open **Your data → Load weekly data** in the left sidebar. Download the blank CSV template and keep its exact column names. Use an existing `dealer_id` from `examples/sample_dealers.csv`. The demo has data through week 24, so the first new file can contain week 25. The app previews how many rows are clean or rejected and explains rejected rows. It appends clean rows only; an existing dealer-week can never be overwritten. A partly received week shows missing dealers under **Fix data**. Once rows are uploaded, **Advance one week** is paused so simulated rows cannot silently mix into your new week. The sidebar reset explicitly replaces uploaded rows, so save a copy of `data/dealer_planner.db` first if you need them.

## 10. Troubleshooting

| Problem | What to do |
|---|---|
| `app.py` or requirements cannot be found | Open the terminal in the extracted inner project folder. |
| Python cannot be found | Install Python 3.13, reopen the terminal, and check its version. |
| Streamlit or another module cannot be found | Use the `.venv` Python commands above and install `requirements.txt` there. |
| Package download times out | Retry installation with `-m pip install --timeout 120 --retries 5 -r requirements.txt`. |
| Browser cannot connect | Keep the launch terminal open and inspect its error output. Use the exact local URL it prints. |
| Port 8501 is already in use | Open the existing app, or add `--server.port 8502` to the launch command and open http://127.0.0.1:8502. |
| First page loads slowly | Let the first imports finish; avoid repeatedly launching more server copies. |
| Database is locked | Close duplicate app processes and retry. Preserve the database if saved actions matter. |
| Counts differ from the expected demo | Set Region All and week24; explicitly reset to seed42 only if you want to clear that copy's actions. |
| Charts are missing | Open Evidence and tick Show trend and retail charts. |
| A test fails | Keep the actual output; do not loosen business thresholds to force a pass. |

## 11. Current limits and submission checklist

Local weekly CSV upload is available. Public deployment, an export-to-folder UI, the extended scoring-settings editor and full digest accounting remain deferred. Sample CSVs and a basic display-only digest preview are included. No live dealer-system connection or external AI is provided.

Before presenting:

- Install dependencies and open the app on the actual presentation computer.
- Rehearse seed42/week24/Region All, accepting a plan, showing context, changing the transfer slider and advancing one week.
- Confirm the simulated-data label and explain that thresholds are demonstration assumptions.
- Keep the server running and keep the sample outputs available as backup.
- Do not describe scenario benefits as realised savings or pattern flags as proof of intent.
