"""Seeded synthetic weekly data. CONTEXT §7; no random state outside this module."""
import re
from pathlib import Path
import numpy as np
import pandas as pd
from planner import db

# §7.5 fixed dealer names, parsed from the authoritative catalogue.
def dealer_catalogue():
    text=Path(__file__).resolve().parents[1].joinpath('docs/CONTEXT.md').read_text()
    line=next(s for s in text.splitlines() if s.startswith('Dealer names:'))
    groups=re.findall(r'(Hyderabad|Bengaluru|Chennai): (.*?)(?=\. Bengaluru:|\. Chennai:|\.$)',line)
    labels={'Sri Venkateshwara Motors':'stock_push','Lakshmi Auto':'service_erosion','Deccan Wheels':'weak_conversion','Marina Motors':'cash_strain','Coastal Cars':'coastal','Charminar Wheels':'gaming_monthend','Nizam Auto':'gaming_cutoff','Godavari Autos':'stale_feed','Kaveri Cars':'market_dip','Coimbatore Cars':'disputed_invoices','Pondy Wheels':'new_outlet','Hosur Road Autos':'recovering','Malnad Motors':'under_penetrated','Mysuru Motors':'mild_stock'}
    rows=[]
    for region,names in groups:
        for name in names.split(', '):
            i=len(rows); market=['Metro','Urban','Semi-urban'][i%3];base=[36,27,18][i%3]
            rows.append(dict(dealer_id=f'D{i+1:02}',name=name,region=region,market_type=market,manager=f'{region} manager',outlet_open_week=6 if labels.get(name)=='new_outlet' else -52,base_retail=base,avg_cost=1000000,avg_price=1100000,market_share_base=.045 if labels.get(name)=='under_penetrated' else .12,sim_label=labels.get(name,'healthy')))
    return pd.DataFrame(rows)

def level(week,onset,ramp,intensity):
    # §7.4 onset, ramp and intensity; never apply before onset.
    return max(0,min(1,(week-onset+1)/ramp))*intensity

def make_week(dealers,week,seed,events):
    rows=[]
    for i,d in dealers.reset_index(drop=True).iterrows():
        rng=np.random.default_rng([int(seed),i,int(week),17]); b=d.base_retail
        seasonal=[.85,.95,1,1.2][(week-1)%4];shape=seasonal
        retail_factor=1.; market_factor=1.;aged=.07+rng.normal(0,.012);overdue=.03+rng.normal(0,.004 if d.sim_label=='healthy' else .008)
        ontime=.945;complaints=1.5;repeat=.03;severe=0;stock_factor=1.;recv_factor=1.;wholesale_factor=1.;disputed=0.
        label=d.sim_label
        effects=[]
        if label=='stock_push': effects=[('stock_push',10,16,1.2),('service_erosion',10,16,.35)]
        if label=='mild_stock': effects=[('stock_push',10,16,.5)]
        if label=='service_erosion': effects=[('service_erosion',12,8,1)]
        if label=='coastal': effects=[('service_erosion',20,4,.59)]
        if label=='cash_strain': effects=[('cash_strain',21,4,.75)]
        if label=='weak_conversion': effects=[('weak_conversion',9,8,1)]
        if label=='market_dip': effects=[('market_dip',10,8,1)]
        if label=='stale_feed': effects=[('cash_strain',12,6,.3)]
        for e in events.itertuples():
            if e.dealer_id==d.dealer_id: effects.append((e.kind,e.onset_week,e.ramp_weeks,e.intensity))
        for kind,onset,ramp,intensity in effects:
            r=level(week,onset,ramp,intensity)
            if kind=='stock_push':
                wholesale_factor*=1.02+.45*r;retail_factor*=1+.05*r;stock_factor*=1+.7*r;aged+=.25*r;recv_factor*=1+.5*r;overdue+=.17*r
            elif kind=='cash_strain': overdue+=.20*r;aged+=.04*r
            elif kind=='service_erosion':
                ontime-=.22*r;complaints+=3.8*r;repeat+=.06*r;severe=max(severe,2 if r>=.9 else 1 if r>=.6 else 0)
            elif kind=='market_dip': retail_factor*=1-.22*r;market_factor*=1-.25*r;overdue+=.06*r;aged+=.19*r
            elif kind=='weak_conversion': retail_factor*=1-.20*r;market_factor*=1+.06*r;aged+=.12*r;overdue+=.05*r
        if label=='gaming_monthend': shape=[.45,.65,.85,2.05][(week-1)%4];retail_factor*=1.04
        if label=='gaming_cutoff': overdue=.17*(.3 if week%4==0 else 1)
        if label=='disputed_invoices': overdue+=.15;disputed=.7;aged+=.20
        if label=='new_outlet':
            retail_factor*=min(1,max(1,week-d.outlet_open_week+1)/26);aged+=.19
        if label=='recovering': overdue+=.20*max(0,min(1,(27-week)/7))
        retail=max(0,b*shape*retail_factor*(1+rng.normal(0,.025 if label=='healthy' else .07)))
        stock=b*4*d.avg_cost*stock_factor;receivables=b*d.avg_cost*3*recv_factor;overdue_amt=receivables*np.clip(overdue,0,1)
        jobs=b*5.5
        rows.append(dict(dealer_id=d.dealer_id,week=week,retail_units=retail,wholesale_units=b*retail_factor*1.02*wholesale_factor,retail_target=b*1.03,py_retail=b*.95*seasonal*(1+rng.normal(0,.02 if label=='healthy' else .05)),market_units=b/d.market_share_base*seasonal*1.04*market_factor*(1+rng.normal(0,.03)),py_market=b/d.market_share_base*seasonal*(1+rng.normal(0,.03)),stock_value=stock,aged_stock_value=stock*np.clip(aged,0,1),receivables_total=receivables,overdue_30_amt=overdue_amt,disputed_amt=overdue_amt*disputed,payments_updated_week=week,service_jobs=jobs,ontime_jobs=jobs*np.clip(ontime,0,1),repeat_repairs=jobs*repeat,complaints=jobs*complaints/100,severe_unresolved=severe))
    return pd.DataFrame(rows)

def generate_history(seed=42):
    db.create_tables()
    if not db.read('weekly').empty: raise ValueError('History already exists; use reset explicitly')
    dealers=dealer_catalogue();db.write('dealers',dealers);db.write('sim_meta',pd.DataFrame([dict(seed=seed,history_weeks=24)]))
    for week in range(1,25): _append_week(week,seed,dealers)
    refresh_vehicles_and_demand(24)

def _append_week(week,seed,dealers):
    frame=make_week(dealers,week,seed,db.read('events'))
    # §7.4 freeze the actual last-known payment fields, not a newly generated value.
    if week>=20:
        previous=db.read('weekly'); previous=previous[previous.week==19].set_index('dealer_id')
        for dealer in dealers[dealers.sim_label=='stale_feed'].dealer_id:
            for col in ['receivables_total','overdue_30_amt','disputed_amt','payments_updated_week']:
                frame.loc[frame.dealer_id==dealer,col]=previous.loc[dealer,col]
    db.write('weekly',frame)

def advance_week():
    meta=db.read('sim_meta').iloc[0];week=int(db.read('weekly').week.max())+1
    _append_week(week,int(meta.seed),db.read('dealers'))
    db.execute('UPDATE sim_meta SET history_weeks=?',(week,));refresh_vehicles_and_demand(week);return week

def inject_event(dealer_id,kind,intensity):
    if kind not in ['stock_push','cash_strain','service_erosion','market_dip','weak_conversion']: raise ValueError('Unknown event')
    if not .3<=intensity<=1: raise ValueError('Intensity must be 0.3 to 1.0')
    if dealer_id not in set(db.read('dealers').dealer_id): raise ValueError('Unknown dealer')
    week=int(db.read('weekly').week.max())+1
    db.write('events',pd.DataFrame([dict(dealer_id=dealer_id,kind=kind,onset_week=week,ramp_weeks=3,intensity=intensity)]))

def reset(seed=42):
    # Explicit reset control §7.6; no files are deleted.
    db.create_tables()
    for table in db.SCHEMA: db.execute(f'DELETE FROM {table}')
    generate_history(seed)

def refresh_vehicles_and_demand(week):
    db.execute('DELETE FROM vehicles');db.execute('DELETE FROM demand')
    dealers=db.read('dealers'); weekly=db.read('weekly');weekly=weekly[weekly.week==week]
    models=[('Aria Hatch',650000),('Sora Sedan',950000),('Vanta SUV',1250000),('Vanta XL',1650000),('Volt EV',1450000)]
    vehicles=[]; demand=[]
    for d in dealers.itertuples():
        match=weekly[weekly.dealer_id==d.dealer_id]
        if match.empty: continue
        count=min(40,int(match.iloc[0].aged_stock_value/d.avg_cost))
        same=dealers[(dealers.region==d.region)&(dealers.dealer_id!=d.dealer_id)].iloc[0].dealer_id
        for i in range(count):
            model,cost=models[i%5];vehicles.append(dict(vehicle_id=f'{d.dealer_id}-{week}-{i}',dealer_id=d.dealer_id,model=model,variant='Standard',age_days=91+(i*13)%150,cost=cost))
            demand.append(dict(dealer_id=same,model=model,variant='Standard',qty=1,required_by_days=14,confirmed=1))
    db.write('vehicles',pd.DataFrame(vehicles));db.write('demand',pd.DataFrame(demand))
