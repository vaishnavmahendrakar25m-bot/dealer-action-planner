"""Generate submission evidence from actual calculated simulated data."""
from pathlib import Path
from planner import db,simulator
from planner.engine import snapshot
from planner.narrative import brief

def export():
    db.create_tables()
    if db.read('weekly').empty: simulator.generate_history()
    path=Path('examples');path.mkdir(exist_ok=True)
    for week in [24,25]:
        if db.read('weekly').week.max()<week: simulator.advance_week()
        s=snapshot(week)
        s[s.sort_rank<5][['name','region','status','group','raw_index','adjusted_index','adjusted_change','capital_at_risk','reason']].to_csv(path/f'week{week}_queue.csv',index=False)
        if week==24:
            r=s[s.name=='Sri Venkateshwara Motors'].iloc[0].to_dict()
            (path/'headline_dealer_case_week24.txt').write_text('Simulated data · Week24 · Data as of 25 October 2026\n'+brief(r)+'\n'+str(r['plan'])+'\n')
    db.read('dealers').to_csv(path/'sample_dealers.csv',index=False)
    db.read('weekly').to_csv(path/'sample_weekly.csv',index=False)
    print('Generated week24_queue.csv, week25_queue.csv, headline_dealer_case_week24.txt, sample_dealers.csv, sample_weekly.csv')

if __name__=='__main__': export()
