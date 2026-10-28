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
