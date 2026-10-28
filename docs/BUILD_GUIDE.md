# Dealer Action Planner: complete build guide, zero to finished

How to use this file: do the parts in order. Part A gets your computer ready. Part B explains the working loop. Part C has every prompt, in the order to paste them. Parts D, E and F cover problems, the final checklist and the demo.

All prompts assume the agent has read `1_CONTEXT_for_ChatGPT.md` (called CONTEXT below). Do not skip that file: it holds every decision.

---

## Part A: get ready (about 20 minutes, once)

### A1. Install what you need

1. **Python 3.11 or newer.** Download from python.org. During installation on Windows, tick "Add Python to PATH". Check in a terminal: `python --version` (on Mac, try `python3 --version`).
2. **Git** (recommended, for save points). Download from git-scm.com. Check with `git --version`.
3. **A code editor** (optional but useful): Visual Studio Code.
4. **Your Codex tool.** Use whichever you have. The steps below are the same:
   - Codex command line or editor extension: open a terminal inside your project folder and start it there.
   - Codex in ChatGPT connected to a repository: create an empty repository, connect it, and use the same prompts.
   - Plain ChatGPT chat (fallback only): paste the context first, then ask for one file at a time and paste each file into your folder yourself. This is slower and error-prone.

### A2. Create the project folder

Open a terminal and run:

```bash
mkdir dealer_action_planner
cd dealer_action_planner
git init
python -m venv .venv
```

Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Mac or Linux: `source .venv/bin/activate`

Install the packages up front (so the first run is quick):

```bash
pip install streamlit pandas numpy altair pytest
```

Create the folders and save the two files:

```bash
mkdir docs
```

- Save `1_CONTEXT_for_ChatGPT.md` as `docs/CONTEXT.md`.
- Create `AGENTS.md` in the project root with the text in A3 below.
- Optionally save this guide as `docs/BUILD_GUIDE.md` for reference.

Then make the first save point:

```bash
git add .
git commit -m "Add context and agent rules"
```

### A3. AGENTS.md (save at the project root)

```markdown
# Agent instructions

You are building the "Dealer Action Planner" prototype. Read docs/CONTEXT.md fully before any change. It is the source of truth.

Rules:
- Do not change decisions in CONTEXT (weights, bounds, thresholds, screens, group names, wording rules). If something seems wrong, say so and ask.
- Python 3.11, Streamlit, pandas, numpy, sqlite3, altair, pytest only. No new services.
- Scoring and simulator code must be importable and testable without Streamlit.
- Deterministic scoring. No AI inside scoring. No randomness outside the seeded simulator.
- Comment each rule with its CONTEXT section number.
- Run pytest after each task and report the real results. Never claim tests pass without running them.
- Keep code simple and readable. The owner must be able to explain every rule in a pitch.
- Wording: never use "cheating", "fraud" or accusations. Use "pattern worth checking".
- All data is simulated and must be labelled so in the UI.
- Work on one task at a time. Do not build ahead of the current prompt.
- When a prompt says "show me the output", paste the real command output, not a summary.
```

### A4. Which model and effort

Start with the standard coding model (Sol) at default effort. Switch to Astra only if Sol fails the same step twice. The hardest steps are Stages 3, 4 and 16. Astra uses more of your allowance per task, so keep it for those.

---

## Part B: the working loop (use for every stage)

1. Paste the stage's prompt into Codex.
2. Let it finish. Do not interrupt it half way.
3. Run what the stage says (usually `pytest`, sometimes the app).
4. Compare with the "You should see" list for that stage.
5. If it matches, save a checkpoint: `git add . && git commit -m "Stage N done"`.
6. If it does not match, use the Fix prompt in Part D with the real error. Do not move on with a failing test.
7. If the agent changes a decision from CONTEXT, say: "Revert that. CONTEXT is fixed. Follow section X."

**If the agent seems to forget things** (long sessions drift), start a fresh session and paste the Context reset prompt in Part D.

**If you are short on time**, the minimum working version is Stages 0 to 5 and 7 to 11, plus Stage 14 and a quick Stage 16. Stages 6, 12, 13, 15 and 17 improve it and are safe to skip or do last. Stage 12 and 13 are the strongest extras for the pitch.

---

## Part C: the prompts

### Stage 0: understand and plan (no code)

```text
Read docs/CONTEXT.md and AGENTS.md completely. Do not write any code yet.

Reply with:
1. Your understanding of the product in 10 bullets.
2. The module and file plan (names and one-line responsibilities).
3. The data flow from simulator to scoring to classification to UI.
4. Any ambiguity or conflict you found in CONTEXT, each with your proposed default. Ask at most 5 questions, and only if you truly cannot proceed with a default.
5. The order in which you would build things, and which parts are riskiest.
```

**You should see:** a plan that matches sections 6 to 11 and 19. **If not:** if it invents features, say "Remove anything not in CONTEXT."

---

### Stage 1: scaffold, config and database layer

```text
Task: project scaffold. Follow docs/CONTEXT.md sections 7.2, 8.1, 12 and 19.

Create:
- requirements.txt, README.md (stub), .gitignore (include .venv, data/*.db, __pycache__, exports/), pytest.ini
- planner/__init__.py
- planner/config.py: DEFAULT_CONFIG holding indicator weights, risk boundaries (b0, b100), tier thresholds (high 60, elevated 35, deterioration 8, urgent overdue 20 percent), trend window 4 weeks, stale feed threshold, peer minimum 5, transfer assumptions (rate 12 percent, transport 8000 same region and 15000 cross-region, default days held 60, days transferred 15), pattern-flag thresholds (month-end gap 15 pp, cut-off ratio 0.6, minimum 3 of 4 blocks, stock build-up ratio 1.15 and aged increase 3 pp), context-check thresholds (market down 8 percent, gap -4 pp, new outlet 26 weeks), every numeric threshold used in the situation-choice rules in section 11.1, labels and units per indicator, and the playbook table from section 12. Provide helpers to serialise the config to JSON.
- planner/db.py: SQLite helpers using the schema in section 7.2 (create tables, read to DataFrame, write DataFrame, execute, a version string based on max week and event count). Database path from env var DEALER_DB or data/dealer_planner.db.
- tests/test_config.py: weights sum to 100 and every indicator has bounds.

Run pytest and show the output. Do not build the simulator or the app yet.
```

**You should see:** `pytest` passes. **Checkpoint commit.**

---

### Stage 2: the dealer data simulator

```text
Task: build planner/simulator.py following docs/CONTEXT.md section 7 exactly (7.1 to 7.7).

Requirements:
- 30 dealers with the fixed names and regions in 7.5, market types assigned so each type has at least 5 dealers, 24 weeks of history, default seed 42.
- Weekly generation using the baseline in 7.3 and the effects table in 7.4. Use numpy default_rng seeded from (seed, dealer index, week, salt) so output is fully reproducible and each week can be generated independently.
- Seeded behaviours exactly as in 7.5. Store each dealer's behaviour in dealers.sim_label (never shown to the RM; used only for validation tests).
- Functions: generate_history(seed=42), advance_week(), inject_event(dealer_id, kind, intensity), reset(seed), refresh_vehicles_and_demand(week) per 7.7.
- Include disputed_amt, outlet_open_week, avg_price, and payments_updated_week (stale_feed freezes receivable fields).
- The cut-off week is the 4th week of each 4-week block; week 24 must be a cut-off week.

Tests (tests/test_simulator.py):
- Same seed gives identical weekly data. Different seed gives different data.
- advance_week adds exactly one week (30 rows) and leaves history unchanged.
- An injected event changes the dealer's later weeks only.
- All 30 named dealers exist with 24 weeks each.
- Sanity: no negative units, aged_stock_value <= stock_value, overdue <= receivables_total, disputed <= overdue.

Then write scripts/preview_week.py that prints, for the seeded dealers at week 24, the 4-week sales vs target, aged stock percent, overdue percent, on-time percent and complaints per 100 jobs. Run the tests and the preview and show me the output.
```

**You should see:** Sri Venkateshwara Motors with sales at or above 100%, aged stock about 30% or more, overdue near 20%; Lakshmi Auto with low on-time; Kaveri Cars well below target; healthy dealers looking healthy. **Checkpoint commit.**

---

### Stage 3: scoring engine core

```text
Task: build planner/engine.py core scoring following docs/CONTEXT.md section 8.

Implement:
- risk(value, b0, b100) = clamp(100 * (value - b0) / (b100 - b0), 0, 100), NaN-safe.
- A pure function score_values(values: dict, cfg) -> dict with per-indicator risk, per-indicator contribution (risk x weight / 100) and the overall index. It must work without any database.
- indicators_all(cfg): reads the weekly and dealers tables and computes, for every dealer and every week from week 4, the rolling 4-week indicators in 8.1, share (retail / market), wholesale-to-retail ratio, capital at risk (8.5), feed age and stale flag (8.4), then risks, contributions, index, the 4-week deterioration, the base tier (urgent rule, High, Elevated, Routine from 8.2), and peer medians by market type with group size (suppress when under 5). Vectorise with pandas groupby; no per-row Python loops over all weeks.
- If the payment feed is stale, exclude the receivables component, mark the index incomplete, and do not reweight. The urgent overdue rule uses the last known value.
- Keep context adjustments, pattern flags and group classification OUT of this task. They come next.

Tests (tests/test_engine.py):
- Dealer A example from section 16 item 1: values 108 percent, -6 pp, 32 percent, 20 percent, 88 percent, 4 per 100 give risks 0, 40, 73.3, 100, 28, 60 and index 56.9. Assert the rounded values.
- Boundary tests for risk() in both directions.
- The urgent rule triggers at overdue 20 percent and on a severe complaint, even with sales above target.
- Stale feed gives an incomplete index and no reweighting.
- Peer suppression when a group is under 5.

Run pytest, then print the week-24 index, deterioration and base tier for all 30 dealers sorted by index. Show the output.
```

**You should see:** Dealer A test passes with 56.9; healthy dealers with an index below about 15; Sri Venkateshwara as Urgent. **If it fails twice:** switch to Astra for this stage. **Checkpoint commit.**

---

### Stage 4: context checks, pattern flags, classification, playbooks

```text
Task: extend planner/engine.py following docs/CONTEXT.md sections 9, 10, 11, 11.1 and 12.

Implement:
1. Context-adjusted index (section 9): market-driven shortfall, disputed invoices (exclude disputed from overdue and from the urgent overdue rule), new outlet ramp target, recovering tag. Return both raw and adjusted index plus a list of adjustments, each with a plain-language reason.
2. Pattern flags (section 10): month-end spike, cut-off payment pattern, stock build-up. Each returns a boolean and an evidence sentence using real numbers. Evaluate over the last 4 complete 4-week blocks.
3. Opportunity flag (section 11 item 6).
4. Classification (section 11): group, status word and the precedence order exactly as written. Output: group (Clear problems, Hidden risk, Fix data, Better than they look, Room to grow, Stars), status (Urgent, High, Elevated, Pattern check, Fix data, Routine), sort rank.
5. The situation choice and the one-line reason exactly as in section 11.1, then the playbook row from section 12 (action, owner, effort, due date from the as-of date, evidence to inspect, what to measure).
6. snapshot(asof_week, cfg): one row per dealer with raw and adjusted index, deterioration, status, group, situation, one-line reason, capital at risk, flags and evidence, recommended playbook, and "since last week" (New, Worse, Better, Same).
7. detection_report(asof_week) comparing each dealer's group with the expected group for its sim_label (section 7.5).

Tests (tests/test_classification.py): assert the expected results table in section 7.5 at week 24 using the detection report. If a seeded dealer lands in the wrong group, DO NOT change the scoring rules, weights or thresholds. Adjust the simulator parameters (section 7.4 magnitudes, onsets, intensities) until the expected results hold, and tell me exactly what you changed and why. If the rules in CONTEXT cannot produce an expected result, stop and explain the conflict.

Run pytest and print the detection report. Show the output.
```

**You should see:** all 14 seeded dealers in their expected groups, at most 2 healthy dealers flagged Elevated, none Urgent or High. **If it fails twice:** switch to Astra. **Checkpoint commit.**

---

### Stage 5: transfers, home KPIs, insight sentence

```text
Task: add planner/transfers.py and planner/kpis.py following docs/CONTEXT.md sections 13 and 14.

transfers.py:
- transfer_candidates(dealer_id, cfg): match the dealer's vehicles older than 90 days to confirmed demand at other dealers by model and variant, one demand per vehicle, prefer same region, with transport cost by route (same region vs cross-region).
- transfer_economics(cost, rate, days_held, days_transferred, transport) -> avoided, net, break-even days. Round for display only.

kpis.py:
- Region scorecard for a given as-of week: revenue month-to-date vs target (current 4-week block to date, times average price), retail units vs target, overdue 30+ percent, Need-action count with change vs last week, capital at risk of the Needs action dealers, and the "More targets" list.
- insight_sentence(...) generating the one-line insight using the template in section 6.1, with sensible wording when everything is on target or nothing needs action.

Tests: the transfer example from section 13 (14,795 avoided, 6,795 net, 24.3 days break-even, -1,425 at 40 days); a viable candidate exists for Sri Venkateshwara Motors; home KPI counts equal the Needs action and Doing well list sizes from snapshot(); the KPIs reconcile with dealer data.

Run pytest and show the output.
```

**You should see:** transfer numbers 14,795 / 6,795 / 24.3 / -1,425. **Checkpoint commit.**

---

### Stage 6: auto-generated dealer summary (no external AI)

```text
Task: add planner/narrative.py following docs/CONTEXT.md section 15.

brief(snapshot_row) returns a 3-line summary: what is wrong, why (with the real numbers and peer values), what to do (the playbook action, owner and due date). It is template-based and deterministic, never claims causation, and for hidden-risk dealers uses "pattern worth checking". For Better than they look dealers, the three lines are: what looks weak, what the context shows, and what to confirm. Label it "Auto-generated summary" wherever shown.

Tests: the text includes the real numbers, contains none of the banned words (cheat, fraud, trick, manipulate, because, caused), and is identical across runs. Run pytest and show the output and the brief for Sri Venkateshwara Motors, Charminar Wheels and Kaveri Cars.
```

---

### Stage 7: Streamlit shell and Home page

```text
Task: create app.py with the Streamlit shell and the Home page following docs/CONTEXT.md sections 5, 6.1 and 14.

- First run: if the database does not exist, generate the history (seed 42).
- Navigation with st.session_state: pages Home, Needs action, Doing well, Dealer case, My actions. Every page except Home has a back button. Use callbacks to change page.
- Home: header with week, region and "Data as of", plus a visible "Simulated data" label; the one-line insight; the five KPI tiles with change indicators; the two big buttons "Needs action (n)" (primary) and "Doing well (n)" (secondary); "My actions" link; a collapsed "More targets" expander.
- Style: single accent colour, status words with colours, generous spacing, large tap targets, a layout that works around 390 px wide. Add minimal custom CSS.
- Cached functions keyed by the database version for loading and scoring.
- The other pages can be placeholders for now.

Run the app headless to confirm it starts without errors (streamlit run app.py --server.headless true and read the log). If a browser tool is available, screenshot at 390 px wide and check both buttons are visible without scrolling.
```

**You should see:** run `streamlit run app.py` yourself. A home page like the wireframe in section 6.1, with correct counts. **Checkpoint commit.**

---

### Stage 8: Needs action and Doing well lists

```text
Task: implement the two list pages following docs/CONTEXT.md sections 6.2 and 6.3.

Needs action:
- Filter chips: All, Clear problems, Hidden risk, Fix data.
- Cards sorted per section 11. Each card: dealer, region, status word with colour, one-line reason, capital at risk (Rs Cr or Rs L), 4-week change arrow, "since last week" tag, and an Open button that sets the selected dealer and navigates to Dealer case.

Doing well:
- Sections: Better than they look (with the "Check context" tag and short reason), Room to grow (with the suggested support action), Stars.
- Open button as above.

Rules: plain language, no jargon in headlines, no accusation words, counts equal to the home page counts, compact cards for a phone.

Verify with a screenshot at 390 px wide and print the card order for week 24 so I can check it against section 7.5.
```

**You should see:** Needs action starts with Sri Venkateshwara Motors and Lakshmi Auto; Charminar Wheels and Nizam Auto under Hidden risk; Godavari Autos under Fix data; Kaveri Cars, Coimbatore Cars, Pondy Wheels and Hosur Road Autos under Better than they look. **Checkpoint commit.**

---

### Stage 9: dealer case page

```text
Task: implement the Dealer case page following docs/CONTEXT.md section 6.4 (display only; the action buttons are wired in the next stage).

Top (always visible): name, region, market type, status, group label, the one-line why, three key facts with peer values, the "Auto-generated summary" box, the recommended action card (action, owner, due date, effort, evidence to inspect, what we will measure), and the decision buttons (disabled placeholders for now).

Expanders (level 2):
- Evidence: indicator table with value, peer median, risk score, contribution and bars; 12-week index trend chart with threshold lines at 35 and 60; weekly retail vs target chart (altair) that makes month-end spikes visible; last 8 weeks of raw rows.
- Context check: raw vs adjusted index with each adjustment and its reason.
- Pattern flags: each flag with its evidence sentence, using the wording rules.
- What we do not know yet: missing information and legitimate alternative explanations.
- Stock transfer option (only when a candidate exists), with a slider for days to sell if moved and the live result from transfers.py.

Two levels only. Use a lighter version for Doing well dealers (strengths, context check, peer position). Check the pages for Sri Venkateshwara Motors, Charminar Wheels, Kaveri Cars and Godavari Autos and describe what each shows.
```

**You should see:** Sri Venkateshwara shows an Urgent status and a transfer option; Charminar shows the month-end spike in the weekly chart; Kaveri shows raw vs adjusted index; Godavari shows an incomplete index. **Checkpoint commit.**

---

### Stage 10: decisions, saved actions and My actions

```text
Task: implement saving decisions and the My actions page following docs/CONTEXT.md sections 6.4, 6.5 and 12.

- Wire the buttons on Dealer case: Accept plan, Change (edit owner, effort, due date, with a reason), Defer (reason required, with quick options "Already handled", "Waiting for dealer", "Disagree with the data", plus free text), Escalate, Request data correction, Schedule visit, Request remote review. Validate that a reason exists where required and show an inline error otherwise.
- Save to the actions table with the baseline metrics at creation (index, overdue percent, aged stock percent, sales vs target). Show a clear confirmation ("Plan saved, due 7 Nov").
- Deferred dealers return to the list automatically if the index worsens by 5 or more points since deferral.
- My actions page: list with status, due date, overdue highlighting, and baseline vs current with a verdict (Improving if the index fell 3 or more points, Worse if it rose 3 or more, otherwise No change).
- Escalation only records and flags. Nothing is executed.
- Prevent duplicate open actions for the same dealer and issue.

Tests for persistence and follow-up logic (no Streamlit): saving an action, reading it back, verdict calculation, the deferral return rule, duplicate prevention. Run pytest and show the output.
```

**You should see:** accept a plan in the app, open My actions, and see it listed. **Checkpoint commit.**

---

### Stage 11: simulator controls, as-of week, scoring settings

```text
Task: add the simulator controls and the as-of week selector following docs/CONTEXT.md section 7.6.

Sidebar:
- As-of week selector (from week 8 to the latest week).
- Advance one week (also moves the as-of week to the new latest week and clears caches).
- Inject event: dealer, kind, intensity; confirm it is queued for the next week.
- Reset simulation with a seed input (default 42), with a confirmation, which also clears saved actions.
- Region filter.
- A collapsed "Scoring settings" expander to edit weights and thresholds, with validation that weights sum to 100 and a reset-to-default button. Label them as demonstration assumptions.

Make sure that advancing a week updates the Home KPIs, the lists and the "since last week" tags, and that cached data refreshes correctly. Add a script that advances from week 24 to week 25 and prints which dealers changed status, and the effect of an injected stock_push event on a healthy dealer over three weeks.
```

**You should see:** click Advance one week; the week label changes; at least one dealer changes status; Nizam Auto's overdue rebounds because week 25 is not a cut-off week. **Checkpoint commit.**

---

### Stage 12: CSV export and import (the weekly-extract story)

```text
Task: implement docs/CONTEXT.md section 20 (data export and import).

1. Export: a button (sidebar) that writes the dealers and weekly tables to CSV files in an exports/ folder with the exact database column names.
2. Import page "Load weekly data": upload a CSV with the weekly columns. Before saving, run the data-quality checks in section 20 and show a report with counts and examples. Reject rows with errors, accept clean rows, and state how many of each. Never silently fix or fill values. Loading a valid file appends the new week, refreshes the scores and lists, and regenerates nothing else.
3. Provide a script scripts/make_sample_week.py that writes a valid week-25 CSV and a second file with one example of each error type, so I can demo both.
4. Tests: one clean file, one file with each error type, a duplicate-week file, and a gap in weeks.
5. Do not change scoring. Add a README paragraph explaining that this stands in for the weekly extracts from the dealer management, finance and service systems.

Run pytest and show the output.
```

**You should see:** the clean file loads as week 25; the bad file shows a clear error report. **Checkpoint commit.**

---

### Stage 13: weekly digest preview

```text
Task: implement docs/CONTEXT.md section 21 (weekly digest preview).

Build planner/digest.py that produces the digest text from snapshot() and the actions table, and show it in an expander "Weekly digest preview" on the Home page. Display only, nothing is sent. Use the same reasons as the lists. Add a test that the digest lists the top 5 dealers in priority order and that its counts match the lists. Run pytest and show the output and the digest for week 24 and week 25.
```

---

### Stage 14: polish, mobile pass, wording audit

```text
Task: polish pass. Follow docs/CONTEXT.md sections 4, 5 and 6.

1. Mobile pass at about 390 px wide on every page: single column, large tap targets, no horizontal scrolling, both Home buttons visible without scrolling.
2. Wording audit: search the whole codebase and every UI string for accusation words (cheat, fraud, trick, manipulate) and for jargon in headlines (risk index, exposure). Replace per the UI rules. Confirm "Simulated data" and "Data as of" appear on every page.
3. Consistency: same status colours and words everywhere, reasons as one-line sentences, every number with peer or period context.
4. Empty and edge states: no dealers needing action, no transfer candidate, no actions saved yet, stale data, and the first run with no database.
5. Speed: confirm each page loads quickly (caching), and report the time for Home and Dealer case.

Show me a summary of every change and screenshots (or a description) of every page at phone width.
```

**You should see:** every page tidy at phone width, nothing cut off. **Checkpoint commit.**

---

### Stage 15: submission package

```text
Task: create the submission package in docs/CONTEXT.md section 22.

1. README.md: what it is, setup (python -m venv, pip install -r requirements.txt), run (streamlit run app.py), reset and simulate, how to run tests, the architecture in a short paragraph and a simple text diagram (sources, ingest, validate, snapshot store, score, classify, recommend, follow up), and the limitations.
2. ASSUMPTIONS.md: data definitions, simulator parameters, weights, boundaries, thresholds, formulas (with the Dealer A worked example), and every assumption marked as a demonstration assumption, not a benchmark.
3. DEMO_SCRIPT.md: the 90-second walkthrough from section 17 with exact dealers and clicks at week 24, the week 24 to 25 advance, and the CSV load as an optional extra.
4. examples/: week24_queue.csv and week25_queue.csv (priority queues), headline_dealer_case_week24.txt (the Sri Venkateshwara Motors case as text), and the sample data CSVs.
5. Run pytest and save the output to examples/test_report.txt.

Everything must be generated from the real app data, not typed by hand. List the files created.
```

---

### Stage 16: final audit against the acceptance checks

```text
Task: audit the whole project against docs/CONTEXT.md section 16 (checks 1 to 9), sections 4 and 5, and these extra checks:
10. The CSV import accepts a clean week and rejects bad rows with a clear report (section 20).
11. The weekly digest matches the lists (section 21).
12. The submission package files exist and match the app (section 22).

For each check, run the relevant test or script and report PASS or FAIL with the evidence (output lines, numbers). Do not claim a pass without running it. Then:
- Fix every FAIL. For data-driven failures adjust simulator parameters only, never scoring rules, weights or thresholds. If a rule in CONTEXT makes a check impossible, stop and explain.
- Re-run pytest and the detection report.
- List any place where the UI or code deviates from CONTEXT, even if you think it is an improvement.

Finish with a short table: check, result, evidence.
```

**You should see:** a table of 12 checks, all PASS. **If it fails twice:** switch to Astra. **Final checkpoint commit.**

---

### Stage 17: pitch preparation

```text
Task: read the code and docs/CONTEXT.md and write PITCH_QA.md with the 15 hardest questions a judge could ask about this prototype (why these weights, how do you know the flags are right, what if data is missing, how would this run weekly in real life, how do you avoid unfair flags, why not machine learning, what stops a dealer gaming the flags themselves, and so on). Each answer is short and honest and points to the exact rule or file. Include the three limitations I should admit. Then write PITCH_90S.md: a timed 90-second script with the exact on-screen steps for each line, based on the real week 24 data (use the real numbers shown in the app), and a 30-second backup version in case the demo fails.
```

---

### Optional: language-model summary (do last, only if everything passes)

```text
Task: add an optional "Generate AI summary" button on the Dealer case page. It sends only the calculated numbers, flags and playbook for that dealer (no raw personal data) to a language-model API using a key from an environment variable, and shows the result in a box labelled "AI-written summary". It must only explain the numbers it was given, cite the fields it used, and never infer causation. If the key is missing, or the call fails or times out, fall back to the template summary from Stage 6 and say so. Log the prompt and response to a local file. Do not change any scoring.
```

---

### Optional: deployment

```text
Task: prepare deployment. Add a Dockerfile (python slim, install requirements, expose the Streamlit port, run streamlit headless) and DEPLOY.md with two routes: Streamlit Community Cloud (requirements.txt, entry point app.py, first-run data generation) and a container host. The app must generate its database on first start if none exists. Do not put secrets in the repository.
```

Note: for the pitch, the safest plan is to run it locally and keep a screen recording as backup. Deployment is a bonus.

---

## Part D: helper prompts

### Fix prompt (whenever something breaks)

```text
Something is wrong. Here is the exact problem:

[paste the error text, or describe what you see and what you expected]

Do this:
1. Find the root cause. Do not guess; reproduce it by running the failing code or test.
2. Fix it with the smallest change that follows docs/CONTEXT.md. Do not change rules, weights or thresholds to make a test pass.
3. Run pytest and the app start-up check and show the output.
4. Tell me what was wrong and what you changed, in 3 lines.
```

### Review prompt (after any big change)

```text
Review the last change against docs/CONTEXT.md. List any deviation from the decisions, any feature added that was not asked for, and any place where a number shown to the RM could disagree with another screen. Do not fix anything yet; report first.
```

### Context reset prompt (new session or the agent drifts)

```text
Read AGENTS.md and docs/CONTEXT.md fully. Then inspect the repository (file list, git log, pytest results) and tell me: which stages of the build are complete, which are not, and what you would do next. Do not change anything yet.
```

### "Explain this to me" prompt (so you can defend it in the pitch)

```text
Explain, in plain language and under 150 words, how [name a rule or file, for example the cut-off payment pattern, or planner/engine.py classification] works, with one worked example using real numbers from the current data. Point to the exact function.
```

---

## Part E: final checklist before the demo

Tick each one:

- [ ] `pytest` passes (all tests).
- [ ] `streamlit run app.py` starts from a fresh clone with no errors (delete the database and run once to confirm it regenerates).
- [ ] Home shows both buttons without scrolling on a phone-width window.
- [ ] Needs action starts with Sri Venkateshwara Motors; Hidden risk shows Charminar Wheels and Nizam Auto; Fix data shows Godavari Autos.
- [ ] Doing well shows Kaveri Cars under "Better than they look".
- [ ] Dealer A example gives 56.9 and the transfer example gives Rs 6,795 net.
- [ ] Advance one week works and changes at least one status.
- [ ] CSV load works for the clean file and shows errors for the bad file.
- [ ] Every page shows "Simulated data" and "Data as of".
- [ ] You can explain the weights, the urgent rules and the three pattern flags without looking at notes.
- [ ] You have rehearsed the 90-second script twice with a timer.
- [ ] You have a **screen recording** of the full demo as backup, and the app running locally on your laptop.
- [ ] Your one admitted limitation is ready: synthetic data and assumed thresholds; real performance needs validation against dealers that actually had problems.

---

## Part F: common problems

| Problem | What to do |
|---|---|
| `streamlit` not found | Activate the virtual environment, then `pip install streamlit` |
| Port already in use | `streamlit run app.py --server.port 8502` |
| Numbers do not change after Advance | The cache is stale. Ask the agent to key the cache on the database version and clear it on advance |
| Database is locked | Close other copies of the app, delete `data/dealer_planner.db` and restart (regenerates) |
| A test fails after a change | Use the Fix prompt with the exact output. Never loosen a threshold to pass a test |
| Agent changed a decision | "Revert that. CONTEXT is fixed. Follow section X." |
| Agent claims success without evidence | "Run it and paste the real output." |
| Layout looks wrong on a phone | Use browser developer tools at 390 px width, then ask the agent to fix the specific page |
| Out of usage allowance | Pause, finish the current stage on the next window, and do the optional stages last |
