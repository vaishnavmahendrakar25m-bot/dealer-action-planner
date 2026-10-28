"""CONTEXT §14: totals reconcile to the selected snapshot and region."""
from planner import db
from planner.engine import snapshot
from planner.config import defaults

def scorecard(week,cfg=None,region='All'):
    cfg=cfg or defaults();dealers=db.read('dealers');w=db.read('weekly').merge(dealers[['dealer_id','region','avg_price']],on='dealer_id');s=snapshot(week,cfg)
    if region!='All': w=w[w.region==region];s=s[s.region==region]
    start=4*((week-1)//4)+1;month=w[w.week.between(start,week)];latest=w[w.week==week]
    revenue=(month.retail_units*month.avg_price).sum();target=(month.retail_target*month.avg_price).sum()
    previous=w[w.week.between(start-4,week-4)]
    prev_revenue=(previous.retail_units*previous.avg_price).sum()
    need=s[s.sort_rank<5]
    old=snapshot(week-1,cfg)
    if region!='All': old=old[old.region==region]
    old_need=old[old.sort_rank<5]
    prior=w[w.week==week-1]
    previous_overdue=100*(prior.overdue_30_amt-prior.disputed_amt).sum()/prior.receivables_total.sum() if prior.receivables_total.sum() else 0
    previous_retail=previous.retail_units.sum()
    previous_capital=old_need.capital_at_risk.sum()
    return dict(previous_need=len(old_need),previous_capital=previous_capital,previous_overdue=previous_overdue,previous_retail=previous_retail,revenue=revenue,revenue_pct=100*revenue/target if target else 0,revenue_change=revenue-prev_revenue,retail=month.retail_units.sum(),retail_pct=100*month.retail_units.sum()/month.retail_target.sum() if month.retail_target.sum() else 0,overdue_pct=100*(latest.overdue_30_amt-latest.disputed_amt).sum()/latest.receivables_total.sum() if latest.receivables_total.sum() else 0,need_action=len(need),doing_well=len(s)-len(need),capital=need.capital_at_risk.sum(),snapshot=s)

def money(value):
    return f'₹{value/10000000:.2f} Cr' if abs(value)>=10000000 else f'₹{value/100000:.2f} L'

def insight_sentence(k):
    if not k['need_action']: return f"Region is at {k['revenue_pct']:.0f}% of revenue target; no dealers need action this week."
    return f"Region is at {k['revenue_pct']:.0f}% of revenue target, and {k['need_action']} dealers carry {money(k['capital'])} of overdue payments and aged stock."
