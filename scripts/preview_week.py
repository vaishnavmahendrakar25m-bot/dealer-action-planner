"""Real simulated week-24 preview, CONTEXT §7."""
from planner import db
if __name__=='__main__':
    from planner.simulator import generate_history
    db.create_tables()
    if db.read('weekly').empty: generate_history()
    d=db.read('dealers');w=db.read('weekly');a=w[w.week.between(21,24)].groupby('dealer_id').sum(numeric_only=True);s=w[w.week==24].set_index('dealer_id')
    a['sales']=100*a.retail_units/a.retail_target;a['aged']=100*s.aged_stock_value/s.stock_value;a['overdue']=100*s.overdue_30_amt/s.receivables_total;a['ontime']=100*a.ontime_jobs/a.service_jobs;a['complaints_rate']=100*a.complaints/a.service_jobs
    print(d.merge(a[['sales','aged','overdue','ontime','complaints_rate']],on='dealer_id').to_string(index=False))
