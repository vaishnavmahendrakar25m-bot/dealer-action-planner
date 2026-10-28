"""Human-approved draft plans, CONTEXT §12."""
from datetime import timedelta
from planner.config import week_end

def recommendation(row,cfg):
    plan=cfg['playbooks'].get(row['situation'],dict(action='Continue weekly review',owner='Regional manager',effort_hrs=0,due_days=7)).copy()
    plan['due_date']=str(week_end(row['week'])+timedelta(days=plan['due_days']))
    plan['review_date']=str(week_end(row['week'])+timedelta(days=plan['due_days']+14))
    plan['evidence_refs']='weekly:'+row['dealer_id']+':'+str(row['week'])
    plan['evidence_to_inspect']=row['reason']
    plan['intended_result']='Review adjusted score, overdue %, aged stock %, and sales vs target at follow-up'
    plan['approval_status']='draft'
    return plan
