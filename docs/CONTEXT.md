# Dealer Action Planner: project context

Paste this whole file into ChatGPT or Codex (or save it as `docs/CONTEXT.md` and tell the agent to read it first). Every decision below was made in discussion. Do not change a decision without asking. Where a number is marked "tune", adjust it until the acceptance checks in section 16 pass.

---

## 1. The case

Case 02 (Illuminati Consulting Case Lab): **"Which dealers need management attention?"**

- An automobile manufacturer sells through a large dealer network. Some dealers grow consistently. Others see declining sales, rising inventory, delayed payments or customer complaints. Sales alone do not show whether a dealer is performing sustainably or heading for trouble.
- Regional managers (RMs) have limited time. They must decide which dealers need attention, why, and what support or corrective action would help.
- Challenge: build a prototype that helps management assess dealers, identify emerging concerns and prioritise actions.
- Illustrative data: sales vs targets, sales growth, inventory ageing, payment delays, service performance, customer complaints, local market potential.
- Submission: a working prototype showing a clear journey from sample inputs to a useful business recommendation; public or synthetic data with stated assumptions; any tool allowed (Excel, no-code, AI-assisted, coded); a 1.5-minute presentation covering the problem, a prototype demo, business value and one key limitation.
- Evaluation: business understanding, sound reasoning, prototype usefulness, clarity of communication.

## 2. The idea in one paragraph

A weekly decision tool for a regional manager. In about 10 minutes each Monday the RM sees how the region is doing, which dealers need action and why, and what to do about each. The tool is built around one claim: **it sees through dealers who look fine but are not, and it sees fairly for dealers who look bad but are not.** It scores dealers with transparent rules, adds pattern checks and context checks, recommends an action with an owner and due date, and tracks whether the action worked the following week.

## 3. Four kinds of dealer (the central framework)

| | Is actually fine | Is actually in trouble |
|---|---|---|
| **Looks fine on paper** | Stars | **Hidden risk** (stock-heavy while on target, month-end or cut-off patterns) |
| **Looks bad on paper** | **Complex dealers** ("better than they look") | Clear problems |

Plus two side groups: **Fix data** (missing or stale data, so we cannot judge) and **Room to grow** (healthy but low market share in a growing catchment).

## 4. Design principles (must hold everywhere)

1. Scoring is deterministic and transparent. Same inputs give the same outputs. No AI inside the scoring.
2. Every recommendation points to a metric or record, an explicit rule, and any material assumption.
3. The app flags and recommends. It never freezes credit, contacts dealers or executes anything. The RM decides.
4. Wording: "pattern worth checking", never "cheating" or "fraud". Never claim causation (for example, never say stock caused late payments). Show a "what we do not know yet" line on each case.
5. All data is synthetic and must be labelled "Simulated data". No invented accuracy, savings or ROI claims.
6. Never silently reweight. If a component is missing, show the index as incomplete and create a data-fix task.
7. Mobile-first, simple, plain language (see section 5).

## 5. User, language and UI rules

- User: the regional manager only. Specialists (finance lead, service head and so on) appear only as action owners. No logins.
- Plain words: "Needs action", "Capital at risk", "Doing well". Not "risk index" or "exposure" in headlines. The score is a small supporting number.
- Every status has a word and a colour. Never colour alone. One accent colour.
- Reasons are one-line sentences: "Sales are above target, but 32% of stock is over 90 days old and 20% of payments are late."
- Every number has context: "20% overdue (peers 6%)", a change arrow, and the time period.
- Always show "Data as of <date>" and a "Simulated data" label.
- Two levels of detail only: summary first, evidence on expand.
- About four taps from opening the app to a saved decision.
- Layout works at phone width (single column, large tap targets). Test at roughly 390px wide.

## 6. Screens and user flow

Flow: **Home -> list -> dealer case**, with a small "My actions" screen.

### 6.1 Home (weekly overview)

```
Week 24 · South region · Data as of 25 Oct · Simulated data

"Region is at 102% of revenue target, but
 5 dealers carry ₹4.6 Cr of overdue payments and aged stock."

[ Revenue this month ₹38.2 Cr · 102% of target ]
[ Retail units · 99% of target ]   [ Overdue 30+ days 7.4% ]
[ 7 need action  (+2 vs last week) ]  [ ₹4.6 Cr capital at risk ]

[ NEEDS ACTION (7)  > ]     <- primary button
[ DOING WELL   (21) > ]     <- secondary button
My actions (4) · 1 overdue >
More targets v   (collapsed)
```

- Five tiles only: three region targets and two dealer-health tiles. Each tile shows a change vs the previous period.
- "More targets" expander (progressive disclosure): market share, wholesale vs retail, aged stock %, service on-time %, complaints per 100 jobs.
- The one-line insight is generated by a rule from the numbers (no AI). Template: "Region is at {revenue_pct}% of revenue target, but {n} dealers carry {capital} of overdue payments and aged stock." If every region KPI is below target, adapt the sentence. If no dealer needs action, say so.
- The two buttons must be visible without scrolling on a phone.
- Sidebar or top bar holds the simulator controls and the "as of week" selector (section 7.6), kept out of the main flow.

Every count is computed from data. All numbers in wireframes are illustrative only.

### 6.2 Needs action (list)

- Filter chips: All, Clear problems, Hidden risk, Fix data.
- Cards sorted by priority tier, then capital at risk (descending), then index (descending).
- Card: dealer name, region, status word (Urgent, High, Elevated, Pattern check, Fix data), one-line reason, capital at risk in ₹ Cr or ₹ L, 4-week change arrow, and "since last week" tag (New, Worse, Better, Same).
- Groups and labels:
  - **Clear problems:** Urgent, High, Elevated.
  - **Hidden risk ("Looks fine, check closer"):** pattern flags or stock build-up on a dealer whose headline looks fine.
  - **Fix data ("Fix data first"):** stale or missing feed.
- Tap a card to open the dealer case. Back arrow on every screen.

### 6.3 Doing well (list)

- Groups:
  - **Better than they look:** weak on paper, healthy in context. Each card carries a "Check context" tag and the reason, for example "82% of target, but the market is down 24% and share is stable".
  - **Room to grow:** healthy, low market share in a growing catchment, with a suggested support action.
  - **Stars:** healthy on paper and in context.
- Tap a card for a light case view (strengths, context check, peer position).

### 6.4 Dealer case (one screen, two levels)

Top, always visible:
- Dealer name, region, market type, status, group label.
- One-line "why".
- Three key facts (metric, value, peer value).
- Recommended action: action name, owner, due date, estimated effort, evidence to inspect, what we will measure.
- Primary button **Accept plan**. Secondary: **Change**, **Defer (with reason)**, **Escalate**, **Request data correction**, **Schedule visit**, **Request remote review**.

Below, in expanders (level 2):
- **Evidence:** indicator table (value, peer median, risk score, contribution) with bars; 12-week index trend with threshold lines (35 and 60); weekly retail vs target chart (shows month-end spikes); last 8 weeks of raw rows.
- **Context check:** raw index vs context-adjusted index, and each adjustment with its reason. Shown on every case, and prominent for "Better than they look".
- **Pattern flags:** month-end pattern, cut-off payment pattern, stock build-up, each with its evidence sentence.
- **What we do not know yet:** missing information and what to check.
- **Stock transfer option** (only when a candidate exists): see section 13.

### 6.5 My actions

- List of saved actions: dealer, action, owner, due date, status, baseline vs current (overdue %, aged stock %, index), and a verdict: Improving, No change, Worse.
- Overdue actions are highlighted. Deferred dealers show their reason and the condition for returning (they return automatically if the index worsens by 5 or more points).

Use simulated week-end dates: week_end = week_start + 6 days; week 24 ends 25 October 2026. Due dates count from the as-of week end. Urgent cases always stay visible. A deferral hides only non-urgent dealers; a deferred dealer returns if the adjusted index worsens by 5 or more points or an urgent rule triggers.

## 7. Data and simulator

### 7.1 Network

30 dealers, 3 regions (Hyderabad, Bengaluru, Chennai; 10 dealers each), 3 market types (Metro, Urban, Semi-urban; assign so each type has at least 5 dealers). Weekly data, 24 weeks of history (weeks 1 to 24). Week 24 is the "current" week at start. Week 1 starts Monday 11 May 2026. Dates are synthetic.

Currency INR. A "month" is a 4-week block: weeks 1-4, 5-8 and so on. The cut-off (reporting) week of each month is the 4th week of the block (weeks 4, 8, 12, 16, 20, 24). Week 24 is therefore a cut-off week, which matters for the demo.

Use simulated week-end dates (week_start + 6 days); week 24 ends 25 October 2026.

### 7.2 Tables (SQLite)

- `dealers`: dealer_id, name, region, market_type, manager, outlet_open_week (negative or zero if open before week 1), base_retail (units per week), avg_cost (INR), avg_price (INR, about 1.1 x cost), market_share_base, sim_label (seeded behaviour, hidden from the RM UI, used only for validation).
- `weekly`: dealer_id, week, retail_units, wholesale_units, retail_target, py_retail (comparable prior-year units), market_units (catchment), py_market, stock_value, aged_stock_value (aged over 90 days), receivables_total, overdue_30_amt, disputed_amt (part of overdue under dispute), payments_updated_week, service_jobs, ontime_jobs, repeat_repairs, complaints, severe_unresolved.
- `vehicles` (latest week only, regenerated each advance): vehicle_id, dealer_id, model, variant, age_days, cost.
- `demand`: dest dealer_id, model, variant, qty, required_by_days, confirmed.
- `events`: dealer_id, kind, onset_week, ramp_weeks, intensity (user-injected events).
- `actions`: id, dealer_id, week_created, group_label, issue, playbook, owner, due_date, effort_hrs, baseline_json, status, decision (accepted, changed, deferred, escalated, data_fix, visit, remote_review), override_reason, created_at, evidence_refs, intended_result, review_date, approval_status.
- `sim_meta`: seed, history_weeks.

Transfers are offered only for the latest inventory snapshot week. Earlier weeks show "Transfer option is shown for the latest week only". Default route time is 2 days same region and 4 days cross-region. Unknown permissions, financing conditions and fees are "pending", never assumed satisfied.

### 7.3 Baseline for a healthy dealer (weekly)

Seasonal factor by week in month: [0.85, 0.95, 1.0, 1.2] (averages 1.0, so 4-week sums are unaffected). Noise comes from a seeded generator (seed, dealer, week), so the same seed always gives the same data.

| Field | Baseline |
|---|---|
| retail_units | base_retail x seasonal x (1 + noise sd 0.07) |
| retail_target | base_retail x 1.03 (flat per week) |
| py_retail | base_retail x 0.95 x seasonal x (1 + noise 0.05) |
| market_units | base_retail / share x seasonal x 1.04 x (1 + noise 0.03), share about 0.12 |
| py_market | base_retail / share x seasonal x (1 + noise 0.03) |
| wholesale_units | retail trend (without month-end shape) x about 1.02 |
| stock_value | base_retail x 4 x avg_cost (4 weeks of supply) |
| aged share of stock | about 7% (sd 1.2 pts) |
| receivables_total | base_retail x avg_cost x 3 |
| overdue ratio | about 3% (sd 0.8 pts) |
| service_jobs | base_retail x 5.5 |
| on-time rate | about 94.5% |
| complaints per 100 jobs | about 1.5 |
| repeat repairs | about 3% of jobs |
| severe_unresolved | 0 |

Base_retail: Metro about 36, Urban about 27, Semi-urban about 18 units per week.

### 7.4 Seeded behaviours (effects)

Each effect has onset week, ramp length (weeks to full strength) and intensity. Level r(week) = min(1, (week - onset + 1) / ramp) x intensity, or a constant when ramp is 0.

| Effect | What changes at level r |
|---|---|
| stock_push | wholesale x (1.02 + 0.45r); retail x (1 + 0.05r); stock units x (1 + 0.7r); aged share + 0.25r; receivables total x (1 + 0.5r); overdue ratio + 0.17r |
| cash_strain | overdue ratio + 0.20r; aged share + 0.04r |
| service_erosion | on-time rate - 0.22r; complaints per 100 + 3.8r; repeat-repair rate + 0.06r; severe_unresolved = 1 if r >= 0.6, 2 if r >= 0.9 |
| market_dip | retail x (1 - 0.22r); market_units x (1 - 0.25r); overdue ratio + 0.06r; aged share + 0.08r |
| weak_conversion | retail x (1 - 0.20r); market_units x (1 + 0.06r); aged share + 0.12r; overdue ratio + 0.05r |
| gaming_monthend | weekly retail shape [0.45, 0.65, 0.85, 2.05] by week in month instead of the seasonal one (sums to 4, so the month is on target); wholesale stays steady |
| gaming_cutoff | underlying overdue ratio about 17%; in the cut-off week of each month it is multiplied by 0.3, then rebounds the next week |
| stale_feed | from the onset week, receivables, overdue and disputed fields freeze at the last update; payments_updated_week stops advancing |
| under_penetrated | market share about 0.045 instead of 0.12; otherwise healthy |
| disputed_invoices | overdue ratio + 0.15r, of which 70% is disputed (disputed_amt) |
| new_outlet | outlet opened recently (age under 26 weeks); retail ramps with age (about min(1, age/26) of normal) while the target stays at full level |
| recovering | cash_strain that peaked and then falls back to zero over about 10 weeks |

Gaming and cut-off patterns need the weekly shape, which is why the data is weekly.

### 7.5 Seeded dealers and expected results at week 24

Names are fixed. Tune parameters until the expected result holds.

| Dealer | Region | Behaviour | Expected result at week 24 |
|---|---|---|---|
| Sri Venkateshwara Motors | Hyderabad | stock_push (onset about 10, ramp about 16, intensity about 1.2) plus mild service_erosion (about 0.35) | Needs action, Clear problems, Urgent (overdue at or above 20%), sales at or above 100% of target, index about 50-60, rising 8+ points in 4 weeks |
| Lakshmi Auto | Chennai | service_erosion (onset 12, ramp 8, intensity 1.0) | Urgent through the severe-complaint rule |
| Deccan Wheels | Hyderabad | weak_conversion (onset 9, ramp 8) | Clear problems, Elevated or higher |
| Marina Motors | Chennai | cash_strain (still rising at week 24; for example onset 16, ramp 10, intensity about 0.7) | Clear problems, High |
| Coastal Cars | Chennai | service_erosion (intensity below 0.6, fast ramp; for example onset 20, ramp 4) | High through deterioration (4-week rise of 8+ points) |
| Charminar Wheels | Hyderabad | gaming_monthend | Needs action, Hidden risk; headline looks fine (on target) |
| Nizam Auto | Hyderabad | gaming_cutoff | Needs action, Hidden risk; looks healthy at week 24 because week 24 is a cut-off week |
| Godavari Autos | Hyderabad | stale_feed (onset 20) with mild cash_strain before it | Needs action, Fix data |
| Kaveri Cars | Bengaluru | market_dip (onset 10, ramp 8) | Doing well, Better than they look: raw index 35 or more, context-adjusted below 35 |
| Coimbatore Cars | Chennai | disputed_invoices | Better than they look (overdue mostly disputed) |
| Pondy Wheels | Chennai | new_outlet (opened about week 6) | Better than they look (ramping outlet) |
| Hosur Road Autos | Bengaluru | recovering | Better than they look (improving fast) |
| Malnad Motors | Bengaluru | under_penetrated | Doing well, Room to grow |
| Mysuru Motors | Bengaluru | mild stock_push (about 0.5) | Routine or Elevated |
| all other dealers | | healthy | Stars (Routine, no flags) |

Healthy dealers must essentially never be flagged Urgent or High. Occasional Elevated from noise is tolerable but should be rare.

Dealer names: Hyderabad: Sri Venkateshwara Motors, Deccan Wheels, Charminar Wheels, Nizam Auto, Godavari Autos, Banjara Motors, Secunderabad Auto Hub, Warangal Wheels, Karimnagar Cars, Nalgonda Motors. Bengaluru: Malnad Motors, Kaveri Cars, Lalbagh Auto, Mysuru Motors, Indiranagar Cars, Hosur Road Autos, Tumakuru Wheels, Hubballi Motors, Belagavi Cars, Mangaluru Auto. Chennai: Lakshmi Auto, Coastal Cars, Marina Motors, Coimbatore Cars, Madurai Motors, Trichy Wheels, Salem Autos, Vellore Motors, Pondy Wheels, Kanchi Autos.

Simulator onsets, ramps, intensities and magnitudes may be tuned until acceptance checks hold; scoring rules, weights, bounds and thresholds must never change. Coastal Cars must have intensity below 0.6 and reach High through deterioration (for example onset 20, ramp 4). Marina Motors must still be rising at week 24 (for example onset 16, ramp 10). Hosur Road Autos must have adjusted index below 35 and 4-week index change at most -8 at week 24.

### 7.6 Simulator controls (in the app, sidebar)

- **Advance one week:** generates week N+1 for all dealers (deterministic from the seed and any injected events) and regenerates vehicles and demand. Increases the as-of week.
- **Inject event:** choose dealer, event kind (stock_push, cash_strain, service_erosion, market_dip, weak_conversion), intensity (0.3 to 1.0). Starts next week with a ramp of 3 weeks. Not retroactive.
- **Reset simulation:** regenerate all history with a seed (default 42). Clears actions.
- **As-of week selector:** view any past week (from week 8, when trends exist).
- The demo moment: advance a week, watch the queue re-rank, and see "since last week" tags.

Pattern flags show "Insufficient history" until four complete 4-week blocks exist (as-of week 16 or later).

### 7.7 Vehicles and demand (for the transfer option)

For each dealer, number of aged vehicles is about aged_stock_value / avg_cost (cap 40). Models: Aria Hatch (about 6.5 L), Sora Sedan (9.5 L), Vanta SUV (12.5 L), Vanta XL (16.5 L), Volt EV (14.5 L), each with 1-2 variants. Ages 91-240 days. Demand rows: for the top aged dealers, create confirmed demand at other dealers (prefer same region) for matching model and variant, so at least the headline dealer has a viable candidate. Add some unrelated noise demand.

Transfers are offered only for the latest inventory snapshot week. Earlier weeks show "Transfer option is shown for the latest week only". Default route time is 2 days same region and 4 days cross-region. Unknown permissions, financing conditions and fees are "pending", never assumed satisfied.

## 8. Scoring (deterministic)

Risk index 0 to 100, higher means more concern. Computed per dealer per week from rolling 4-week windows (weeks w-3 to w), except stock and receivables (snapshot at week w).

### 8.1 Indicators, weights and risk boundaries

| Indicator | Weight | Risk 0 at | Risk 100 at |
|---|---|---|---|
| Retail sales vs target (4-week retail units / 4-week target, %) | 15% | 100% or above | 70% or below |
| Dealer growth minus market growth (percentage points; 4-week retail vs py_retail, minus 4-week market vs py_market) | 10% | 0 pp or above | -15 pp or below |
| Share of stock value aged over 90 days | 20% | 10% or below | 40% or above |
| Receivables more than 30 days past due / total receivables | 25% | 2% or below | 20% or above |
| Service jobs completed on time (4-week) | 15% | 95% or above | 70% or below |
| Service complaints per 100 jobs (4-week) | 15% | 1 or below | 6 or above |

Risk for a value v with boundaries (b0, b100): `risk = clamp(100 * (v - b0) / (b100 - b0), 0, 100)`. The same formula works for both directions because b0 and b100 are ordered as above.

Overall index = sum of (risk x weight). Show contributions per indicator. Weights, boundaries and thresholds live in a config (editable in the UI) and are labelled as demonstration assumptions, not benchmarks.

Default weights, bounds and thresholds stay fixed as specified. UI edits create a demonstration scenario: show "Custom settings active" and a reset-to-default button.

### 8.2 Rules, tiers and trend

- **Urgent** (regardless of index): a verified unresolved severe complaint (severe_unresolved > 0), or non-disputed receivables more than 30 days past due at 20% or more.
- **High:** index at least 60, or deterioration of at least 8 index points over 4 weeks.
- **Elevated:** index from 35 to below 60.
- **Routine:** below 35, subject to flags.
- Deterioration = current index minus index 4 weeks earlier. Computed with unchanged definitions and weights. If either end is incomplete, treat deterioration as unavailable (not zero) and say so.

### 8.3 Peers

Peer group = same market type. Show the peer median and group size. Suppress peer conclusions if the group has fewer than 5 dealers.

### 8.4 Missing and stale data

Payment feed stale if payments_updated_week is more than 7 days behind (more than 1 week). Then: show the index as incomplete (receivables component excluded, not reweighted), create a "Fix data" task, and still apply the urgent rule using the last known overdue value.

### 8.5 Capital at risk

Capital at risk = overdue_30_amt (non-disputed) + aged_stock_value, in INR. Shown as ₹ Cr (10,000,000) or ₹ L (100,000). Compare currencies only with currencies. Never add complaint counts to currency.

## 9. Context checks (protect complex dealers)

Show raw index and context-adjusted index side by side, with each adjustment and its reason. Urgent rules are never relaxed by context except the dispute rule below.

| Adjustment | Rule |
|---|---|
| Market-driven shortfall | If market growth is at or below -8% and the dealer's growth minus market growth is at least -4 pp, set the sales-vs-target and growth risks to 0 and note "target unrealistic for this market; review the target, not the dealer" |
| Disputed invoices | Exclude disputed_amt from overdue before computing the receivables ratio and the urgent overdue rule; show disputed amount separately as an item to resolve with the manufacturer |
| New outlet | Outlets under 26 weeks old: score sales against a ramp target (target x min(1, age/26)) and set the growth-vs-market contribution to 0, keep all other weights unchanged, and show growth vs market as context only with the adjustment and its reason |
| Recovering | If the index fell by 8 or more points over 4 weeks and the adjusted index is below 60 with no urgent rule, tag "Recovering" |
| Rates, not counts | Complaints always per 100 jobs |

A dealer is **Better than they look** when the raw tier would be Elevated or higher (raw index 35 or more) but the context-adjusted tier is Routine, or when it carries the Recovering tag and its adjusted tier is Routine, and no urgent rule applies. A Recovering dealer with an adjusted tier of Elevated or higher stays in Clear problems and keeps the Recovering tag. Always show "Check context" on its card.

## 10. Hidden-risk flags (pattern checks)

These are flags beside the index. They are not part of the weighted score. The wording is "pattern worth checking". The recommended action is "verify records", not an accusation.

1. **Month-end sales spike:** for each completed 4-week block, the share of the month's retail units sold in the 4th week. Flag if the dealer's share is at least 15 percentage points above the peer median in at least 3 of the last 4 complete blocks. Evidence sentence: "Sold 51% of the month's units in the last week vs a peer median of 30%, in 4 of 4 months."
2. **Cut-off payment pattern:** for each block, overdue amount in the cut-off week divided by the average overdue of the other three weeks. Flag if the ratio is below 0.6 in at least 3 of the last 4 blocks. Evidence: "Overdue falls to 30% of its mid-month level at month-end in 4 of 4 months."
3. **Stock build-up:** 4-week wholesale / retail at or above 1.15, and aged-stock share up at least 3 pp vs 4 weeks ago, while sales attainment is at or above 100%.

Legitimate alternative explanations (schemes, seasonality, customer financing cycles) are listed on the case under "What we do not know yet".

Pattern flags show "Insufficient history" until four complete 4-week blocks exist (as-of week 16 or later).

## 11. Classification and priority

Order of precedence for each dealer at the as-of week:

1. Urgent rule hit -> **Clear problems / Urgent**.
2. Context-adjusted tier High or Elevated -> **Clear problems**.
3. Stale feed (and not already above) -> **Fix data**.
4. Pattern flag or stock build-up flag -> **Hidden risk** (status "Pattern check").
5. Better-than-they-look conditions -> **Doing well / Better than they look**.
6. Opportunity: market share (4-week retail / market) below 0.7 x peer median share, market growth above 0, and adjusted index below 35 -> **Room to grow**.
7. Otherwise Routine with no flags -> **Stars**.

Sort order in Needs action: Urgent, High, Elevated, Pattern check, Fix data; then capital at risk descending; then index descending.

"Since last week": compare the status at week w with week w-1: New (not in Needs action before), Worse, Better, Same.

Recovering follows this precedence: Better than they look requires an adjusted Routine tier; Elevated or higher remains Clear problems with the Recovering tag.

### 11.1 Choosing the situation (playbook) and the one-line reason

Use the context-adjusted contributions (points of the 100-point index, section 8.1). The first matching rule wins. All thresholds are config values.

1. severe_unresolved > 0 -> "Severe unresolved complaint".
2. Payment feed stale and no urgent rule -> "Fix data".
3. Month-end or cut-off pattern flag on a dealer whose adjusted tier is Routine -> "Hidden risk (patterns)".
4. The disputed-invoices adjustment applied and the adjusted receivables contribution is below 8 -> "Disputed invoices".
5. Receivables contribution at least 8 and aged-stock contribution at least 8 -> "Stock build-up with payment strain".
6. Receivables contribution at least 12 -> "Payment strain".
7. Aged-stock contribution at least 10 -> "Ageing inventory".
8. On-time contribution plus complaints contribution at least 8 -> "Service erosion".
9. If the market-driven adjustment applied and no higher-priority rule (1 to 8) matched, the situation is "Market-driven shortfall" (action: Review target realism against the market). Otherwise, if sales contribution plus growth contribution is at least 8, the situation is "Sales opportunity gap".
10. Opportunity flag (section 11 item 6) -> "Room to grow".
11. Otherwise -> "No action" (Stars).

Each situation maps to a row of the playbook table in section 12. A stock build-up flag on its own (section 10 item 3) does not choose a situation; it only supports rules 5 and 7 and appears in the evidence.

**One-line reason (plain language, no causation words such as "because" or "caused by"):**
- Take up to 3 indicators with a contribution of at least 3 points, highest first. Phrase each as: sales "{v}% of target"; growth "{v} pp vs market"; aged stock "{v}% of stock aged 90+ days"; receivables "{v}% of payments 30+ days late"; on-time "{v}% of service jobs on time"; complaints "{v} complaints per 100 jobs". Add the peer value where available: "(peers {p})".
- If sales are at or above 100% of target and at least one other indicator qualifies, start with "Sales are on or above target, but ". Example: "Sales are on or above target, but 32% of stock is aged 90+ days (peers 14%) and 20% of payments are 30+ days late (peers 6%)."
- Hidden risk: use the pattern flag's evidence sentence from section 10.
- Fix data: "Payment data is {n} days old, so the score is incomplete."
- Better than they look: the raw reasons, then ", but " and the adjustment's reason. Example: "82% of target, but the market is down 24% and share is stable."
- Severe complaint: "A severe complaint is still unresolved."

## 12. Playbooks (recommended action by group)

| Situation | Action | Owner | Effort | Due |
|---|---|---|---|---|
| Stock build-up with payment strain | Joint finance and inventory review; check transfer option | Regional finance lead + inventory manager | 3 h | 7 days |
| Payment strain | Finance-led collection review | Regional finance lead | 2 h | 7 days |
| Ageing inventory | Inventory intervention: pricing, merchandising, transfers | Regional inventory manager | 2 h | 7 days |
| Service erosion | Identify the bottleneck; target staffing, parts or process support | Regional service manager | 4 h | 10 days |
| Severe unresolved complaint | Escalate and visit | Service head | 1.5 h | 2 days |
| Sales opportunity gap | Targeted sales coaching and stock support | Regional sales manager | 3 h | 10 days |
| Market-driven shortfall | Review target realism against the market | Regional manager | 1 h | 10 days |
| Hidden risk (patterns) | Verify records: check daily sales and payment data, ask the dealer to explain, review scheme timing | Regional analyst | 2 h | 7 days |
| Fix data | Correct the data feed before drawing conclusions | Data owner | 0.5 h | 3 days |
| Room to grow | Plan market-share growth support | Sales development manager | 2 h | 14 days |
| Disputed invoices | Resolve disputed invoices with the manufacturer's finance team | Regional finance lead | 2 h | 10 days |

Each action also lists: evidence to inspect, what will be measured, and the review date (due date + 14 days). Effort, owner and due date are editable. Any override requires a one-line reason (quick options: "Already handled", "Waiting for dealer", "Disagree with the data", plus free text).

Action record stores: dealer, issue, evidence references, action, owner, effort, due date, baseline metrics (index, overdue %, aged stock %, sales vs target), intended result, decision and status, override reason, review date. A generated plan is a draft until the RM accepts it. Actions beyond an RM's authority (credit limit, allocation cut, target change) are "Escalate": the app records and flags them, it does not execute them.

## 13. Stock-transfer option (differentiator)

Offer a candidate only when an aged vehicle matches confirmed demand at another dealer. Feasibility checks before value: model and variant match, vehicle available, confirmed demand, delivery deadline, route time and cost. Permission, financing conditions, taxes and fees that are not known are shown as "pending", never assumed satisfied.

Economics per vehicle (all inputs editable):
- Carrying cost avoided = cost x annual_rate x (days_if_held - days_if_transferred) / 365
- Net benefit = carrying cost avoided - incremental transport and handling
- Break-even acceleration (days) = transport / (cost x annual_rate / 365)

Default example: cost ₹1,000,000 fully financed, 12% annual rate, 60 days if held, 15 days if transferred (including transit), transport ₹8,000 (same region; use ₹15,000 cross-region).
- Avoided = 1,000,000 x 0.12 x 45 / 365 = ₹14,795 (rounded)
- Net = ₹6,795
- Break-even = 24.3 days
- If the destination sale takes 40 days instead: avoided = ₹6,575, net = -₹1,425 (negative).

Show a slider for "days to sell if moved" and display the net result live. Say clearly: these are scenarios under stated assumptions, not savings. Financing is counted at both locations until the final sale. Do not double count discount avoidance and margin improvement. Do not claim ROI.

Transfers are offered only for the latest inventory snapshot week. Earlier weeks show "Transfer option is shown for the latest week only". Default route time is 2 days same region and 4 days cross-region. Unknown permissions, financing conditions and fees are "pending", never assumed satisfied.

## 14. Home KPI definitions

- **Revenue this month:** sum over dealers of (retail units in the current 4-week block to date x avg_price). Target = sum of retail_target to date x avg_price. Show % of target and change vs the same point last month.
- **Retail units:** current month-to-date units vs target.
- **Overdue 30+ days:** total non-disputed overdue / total receivables (latest snapshot).
- **Need action:** count of dealers in Needs action, with change vs last week.
- **Capital at risk:** sum of capital at risk (section 8.5) for dealers in Needs action.
- **More targets:** market share (4-week retail / 4-week market), wholesale vs retail ratio, aged stock %, service on-time %, complaints per 100 jobs.

KPIs must reconcile with the dealer data. The KPI list is config-driven (RMs have different targets).

## 15. Deterministic brief

No external AI or language-model call anywhere. The optional language-model stage is excluded. Summaries are deterministic and template-based, labelled "Auto-generated summary", cite calculated fields and playbooks, never invent facts or infer causation.

## 16. Acceptance checks

1. **Dealer A worked example** (unit test): retail 108% of target -> risk 0; growth +2% vs market +8% = -6 pp -> risk 40; aged stock 32% -> risk 73.3; overdue 20% -> risk 100; on-time 88% -> risk 28; complaints 4 per 100 -> risk 60. Contributions 0, 4.0, 14.7, 25.0, 4.2, 9.0. Overall index 56.9. Priority Urgent (overdue rule) although sales exceed target and the index alone would be Elevated.
2. **Transfer example** (unit test): 14,795 avoided, 6,795 net, 24.3 days break-even, -1,425 net at 40 days.
3. **Reproducibility:** same seed gives identical data. Advancing a week adds exactly one week of rows.
4. **Seeded results** at week 24 match section 7.5 (detection test over the `sim_label` column: all problem and complex dealers land in their expected group; at most 2 healthy dealers flagged Elevated; none Urgent or High).
5. **Home KPIs reconcile** with the dealer data. Counts on the home buttons equal the list lengths.
6. **No silent reweighting:** the Godavari Autos index is marked incomplete.
7. **Wording check:** no accusation words (cheating, fraud) anywhere in the UI; "Simulated data" label visible on every page.
8. **Phone layout** at about 390px wide: the home page shows both buttons without scrolling.
9. **Advance-a-week demo:** advancing from week 24 to 25 changes at least one status, and the "since last week" tags appear. Week 25 is not a cut-off week, so Nizam Auto's overdue rebounds and its cut-off pattern becomes visible in the evidence.

## 17. The 90-second pitch (the app must support this)

- 0-15 s: "Regional managers decide where limited attention goes. Sales alone can hide inventory, payment and service problems, and can also make good dealers look bad."
- 15-35 s: Home page: region on target, but 7 dealers need action. Open Needs action, open the stock-heavy dealer that beats target and is flagged urgent. Every flag shows its numbers and rule.
- 35-55 s: Open "Looks fine, check closer" (month-end or cut-off pattern), then Doing well, "Better than they look" (market-driven dealer): the app does not punish a good dealer.
- 55-75 s: Action plan: owner and due date, accept it. Stock-transfer slider: change days to sell and watch the benefit change. Advance a week and watch the queue re-rank.
- 75-90 s: Value: managers spend limited time on the right dealers, with clear accountability. Limitation: synthetic data and assumed thresholds; real performance needs validation against dealers that actually had problems.

## 18. Out of scope

Live SAP or DMS connections, logins and roles, multi-agent orchestration, autonomous execution, a trained default-prediction model, real dealer data. Mention them only as production next steps: weekly extracts from DMS, ERP and service systems into a database, the same scoring rules, and a hosted web app.

## 19. Technical constraints

- Python 3.11+, Streamlit, pandas, numpy, SQLite (via sqlite3), altair for charts, pytest. No other services.
- Project layout: `app.py`, `planner/` (config, db, simulator, engine, playbooks, transfers, narrative), `tests/`, `data/`, `README.md`, `requirements.txt`, optional `Dockerfile`.
- Scoring and simulator code must be importable and testable without Streamlit.
- Weights, thresholds, playbooks and KPI list in a config module, editable in the UI sidebar.
- Cache heavy computation (Streamlit cache keyed by a data version).
- Runs locally with `streamlit run app.py`. A pre-built database or a first-run generation step so the demo needs no network.
- Keep code readable: the builder must be able to explain every rule. Comment the rules and cite section numbers of this document.

Python 3.13.5 is acceptable for the Python 3.11+ requirement. Keep AGENTS.md verbatim as provided.

## 20. Data export and import (stand-in for weekly extracts)

Purpose: show how real weekly extracts would arrive. In production the same files would come from the dealer management, finance and service systems, and everything after the load stays unchanged.

- **Export:** write the `dealers` and `weekly` tables to CSV (one file per table, exact database column names) into an `exports/` folder.
- **Import page ("Load weekly data"):** upload a CSV with the same columns as `weekly`. Before saving, run a data-quality check and show a report with counts and examples:
  - unknown dealer_id
  - duplicate dealer-week rows (in the file, or already in the database)
  - missing or negative values in required fields
  - a week other than the latest week (only missing dealer rows may be added) or the immediately following week (gaps or going backwards)
  - overdue_30_amt greater than receivables_total, disputed_amt greater than overdue_30_amt, aged_stock_value greater than stock_value
  - payments_updated_week later than the row's week
- Rows with errors are rejected, clean rows are accepted, and the page states how many of each. Loading a valid file appends the new week, refreshes scores and lists, and does not regenerate anything else.
- Never silently fix or fill values.

Accept clean rows. A week is partial until all 30 dealers have rows. Dealers with no row for that week show as Fix data ("No data received for week N") and are never scored from older data. A later file may add rows only for dealers with no row yet for that week; existing dealer-week rows are rejected as duplicates. Latest week means the highest week with at least one row.

## 21. Weekly digest preview

A read-only preview of the message an RM would receive each Monday (display only, nothing is sent). Format:

```
Week 25 · South region: 5 dealers need your attention
1. Sri Venkateshwara Motors (Urgent): {one-line reason} · ₹1.8 Cr at risk · Action: {action}, due {date}
2. ...
(top 5 by priority)
New this week: {n} · Worse: {n} · Improved: {n}
Actions due: {n} ({n} overdue)
Open the app to review.
```

Built from the same snapshot data as the lists. Shown in an expander on the Home page or in My actions, labelled "Weekly digest preview".

## 22. Submission package

The case asks for a working prototype, sample data, assumptions and calculation notes, a short setup guide, a saved example output and a demonstration script. The repository must contain:

- `README.md`: what it is, setup, run, reset and simulate, tests, architecture paragraph and diagram, limitations.
- `ASSUMPTIONS.md`: data definitions, simulator parameters, weights, boundaries, thresholds, formulas, and every assumption marked as a demonstration assumption (not a benchmark).
- `DEMO_SCRIPT.md`: the 90-second walkthrough with exact dealers and clicks.
- `examples/`: saved example outputs (week 24 and week 25 priority queues as CSV, the week 24 dealer case for the headline dealer as text) and the sample data CSVs.
- `PITCH_QA.md`: hard questions and honest answers.
- Test results from a final `pytest` run saved to `examples/test_report.txt`.
