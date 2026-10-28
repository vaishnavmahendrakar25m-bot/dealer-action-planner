"""CONTEXT §§6.5,12 and A9: records only; no autonomous action."""
import json
from datetime import datetime,timezone,timedelta,date
import pandas as pd
from planner import db
from planner.config import week_end

def verdict(baseline,current):
    if pd.isna(current) or pd.isna(baseline): return 'Unavailable'
    return 'Improving' if current-baseline<=-3 else 'Worse' if current-baseline>=3 else 'No change'

def save(row,decision='accepted',reason='',owner=None,effort=None,due=None):
    if decision!='accepted' and not reason.strip(): raise ValueError('A one-line reason is required')
    plan=row['plan'];issue=row['situation'];existing=db.read('actions')
    if not existing[(existing.dealer_id==row['dealer_id'])&(existing.issue==issue)&(existing.status=='open')].empty: raise ValueError('An open plan already exists for this dealer and issue')
    baseline={k:None if pd.isna(row.get(k)) else float(row[k]) for k in ['adjusted_index','overdue','aged','sales']}
    record=dict(dealer_id=row['dealer_id'],week_created=int(row['week']),group_label=row['group'],issue=issue,playbook=plan['action'],owner=owner or plan['owner'],due_date=str(due or plan['due_date']),effort_hrs=plan['effort_hrs'] if effort is None else effort,baseline_json=json.dumps(baseline),status='open',decision=decision,override_reason=reason,created_at=datetime.now(timezone.utc).isoformat(),evidence_refs=plan['evidence_refs'],intended_result=plan['intended_result'],review_date=str(date.fromisoformat(str(due or plan['due_date']))+timedelta(days=14)),approval_status='accepted' if decision in ['accepted','changed'] else 'recorded')
    db.write('actions',pd.DataFrame([record]));return record

def visible(snapshot):
    # A9: urgent always visible; missing current score cannot safely satisfy a deferral.
    a=db.read('actions');a=a[a.week_created<=snapshot.week.max()];hidden=set()
    for r in a[(a.decision=='deferred')&(a.status=='open')].itertuples():
        match=snapshot[snapshot.dealer_id==r.dealer_id]
        if match.empty: continue
        now=match.iloc[0];baseline=json.loads(r.baseline_json).get('adjusted_index')
        if now.status!='Urgent' and pd.notna(now.adjusted_index) and baseline is not None and now.adjusted_index-baseline<5: hidden.add(r.dealer_id)
    return snapshot[~snapshot.dealer_id.isin(hidden)]
