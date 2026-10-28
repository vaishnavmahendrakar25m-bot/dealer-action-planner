# Demonstration assumptions

All data and dates are simulated. All parameters below are demonstration assumptions, not benchmarks. The amended `docs/CONTEXT.md` is authoritative.

- Thirty fixed dealers; three regions, ten each; three market types; 24 initial weeks; default seed 42. Weeks are Monday–Sunday, beginning 11 May 2026. Week 24 ends 25 October 2026. A month is four weeks.
- Seeded random draws are isolated in `planner/simulator.py`; data generation is independently seeded by seed, dealer and week.
- Six weights: sales 15%, growth relative to market 10%, aged stock 20%, overdue 25%, on-time service 15%, complaints per 100 jobs 15%.
- Risk boundaries (zero, one hundred): sales (100,70), growth (0,-15), aged (10,40), overdue (2,20), on-time (95,70), complaints (1,6).
- Risk = clamp(100*(value-b0)/(b100-b0),0,100). Contribution = risk*weight/100.
- Dealer A: 108%, -6 pp, 32%, 20%, 88%, 4 gives contributions 0,4,14.6667,25,4.2,9 and score 56.8667, displayed 56.9. Non-disputed overdue >=20% or an unresolved severe complaint overrides to Urgent.
- High: score >=60 or four-week deterioration >=8. Elevated: >=35. Routine: below35, subject to flags and classification precedence.
- Same-market-type peers require five dealers. Missing/stale components are incomplete and never reweighted. Payment feed stale means more than one week behind.
- Context: market decline <=-8% with dealer gap >=-4 pp zeros sales and growth risks; disputed amounts are excluded from adjusted overdue; new outlets under26 weeks use a ramp target and zero growth contribution. Recovering requires a fall >=8, no urgent rule, and adjusted score <60; Doing well still requires Routine.
- Pattern checks require four complete blocks: month-end share >=15pp above peers in3/4 blocks; cut-off ratio <0.6 in3/4 blocks; stock build-up wholesale/retail >=1.15 plus aged increase >=3pp while sales >=100%.
- Capital at risk = non-disputed overdue plus aged stock value; it is a prioritisation measure, not a loss estimate.
- Transfers require matching model/variant, available aged stock and confirmed demand. Routes take2 days same-region or4 cross-region. Default transport is INR8000 or15000. Unknown permissions, financing conditions, taxes and fees remain pending.
- Transfer example: cost INR1000000, rate12%, held60 days, moved15 days: avoided14794.52, net6794.52, break-even24.33 days. At40 days moved, net is -1424.66. Round only for display.
- Action due dates use simulated week end. Deferred non-urgent dealers return at +5 adjusted points or on an urgent rule. Verdicts use a three-point score change. Escalations only record a decision.
- Simulator tuning details and exact amendments are recorded in `docs/DECISIONS.md`; scoring defaults were not tuned.
