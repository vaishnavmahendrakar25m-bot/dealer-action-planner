"""CONTEXT §13: illustrative economics, never claimed savings."""
from planner import db
from planner.config import defaults

def transfer_economics(cost,rate,days_held,days_transferred,transport):
    if cost<=0 or rate<=0: raise ValueError('Cost and annual rate must be positive')
    if min(days_held,days_transferred,transport)<0: raise ValueError('Days and costs cannot be negative')
    avoided=cost*rate*(days_held-days_transferred)/365
    return dict(avoided=avoided,net=avoided-transport,break_even_days=transport/(cost*rate/365))

def transfer_candidates(dealer_id,cfg=None,asof_week=None):
    cfg=cfg or defaults();latest=int(db.read('weekly').week.max())
    if asof_week is not None and asof_week!=latest: return []
    vehicles=db.read('vehicles');demand=db.read('demand').copy();dealers=db.read('dealers').set_index('dealer_id');out=[]
    for v in vehicles[(vehicles.dealer_id==dealer_id)&(vehicles.age_days>90)].itertuples():
        matches=demand[(demand.dealer_id!=dealer_id)&(demand.model==v.model)&(demand.variant==v.variant)&(demand.confirmed==1)&(demand.qty>0)]
        matches=matches.assign(same=matches.dealer_id.map(dealers.region)==dealers.loc[dealer_id,'region']).sort_values('same',ascending=False)
        for i,m in matches.iterrows():
            route=cfg['transfer']['same_days' if m.same else 'cross_days']
            if route>m.required_by_days: continue
            out.append(dict(vehicle_id=v.vehicle_id,model=v.model,variant=v.variant,cost=v.cost,destination=dealers.loc[m.dealer_id,'name'],route_days=route,transport=cfg['transfer']['same_region' if m.same else 'cross_region'],pending='Permissions, financing conditions, taxes and fees pending'))
            demand.loc[i,'qty']-=1;break
    return out
