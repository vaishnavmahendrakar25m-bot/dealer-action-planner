# Browser verification — 29 October 2026

Actual UI checks performed in the in-app browser against http://127.0.0.1:8501.

- Home: week24, date25 Oct2026, Simulated data, 8 Needs action, 22 Doing well; five calculated KPI tiles.
- Phone viewport: innerWidth390, innerHeight844, document scrollWidth390. Needs action button bounds y513.83–553.83; Doing well y562.63–602.63. Both visible without scrolling.
- Needs action: Sri Venkateshwara Motors and Lakshmi Auto first, then Marina, Coastal, Deccan, pattern cases and Godavari; status badges contain text and colour.
- Headline case: sales101.8%, aged37.1%, overdue22.2%; Urgent; owner and due2026-11-01 visible.
- Accept plan: actual confirmation “Plan saved, due 2026-11-01”; My actions showed accepted/open, the correct dealer/owner/date, baseline and No change verdict.
- Kaveri case: Better than they look; context expander displayed raw37.0 versus adjusted23.7 and target-realism explanation.
- Transfer candidate: Aria Hatch Standard to Deccan Wheels, 2-day route; unknown conditions pending. At15 days moved, net INR1616. Moving slider to120 recalculated net to INR-20822.
- Evidence: both Vega visualizations rendered, plus indicator table and raw-row table.
- Advance one week: selector and header moved to25; date01 Nov2026; Needs action7, Doing well23. KPIs refreshed.
- Reset with explicit checkbox: restored seed42, week24 and counts8/22; reset checkbox subsequently unchecked.
- Final Doing well groups rendered in order: Better than they look, Room to grow, Stars.

Cold dependency imports were unusually slow on this computer. The running server is warm. Charts load on demand through the Evidence checkbox. No production deployment or full CSV import check is claimed.
