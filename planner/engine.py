"""Deterministic scoring and rolling metrics, CONTEXT §8."""
import numpy as np
import pandas as pd
from planner import db
from planner.config import defaults


def risk(value,b0,b100):
    if pd.isna(value): return float('nan')
    return float(np.clip(100*(value-b0)/(b100-b0),0,100))

def score_values(values,cfg=None):
    cfg=cfg or defaults(); risks={k:risk(values.get(k,np.nan),v['b0'],v['b100']) for k,v in cfg['indicators'].items()}
    contributions={k:r*cfg['indicators'][k]['weight']/100 for k,r in risks.items()}
    return dict(risks=risks,contributions=contributions,index=sum(v for v in contributions.values() if pd.notna(v)),incomplete=any(pd.isna(v) for v in contributions.values()))

def tier(index,delta,urgent,cfg):
    # §8.2 urgent always wins; missing deterioration is unavailable, never zero.
    return 'Urgent' if urgent else 'High' if index>=cfg['high'] or pd.notna(delta) and delta>=cfg['deterioration'] else 'Elevated' if index>=cfg['elevated'] else 'Routine'

def indicators_all(cfg=None):
    cfg=cfg or defaults();w=db.read('weekly').sort_values(['dealer_id','week']);d=db.read('dealers')
    sums=['retail_units','retail_target','py_retail','market_units','py_market','service_jobs','ontime_jobs','complaints','wholesale_units']
    r=w.groupby('dealer_id')[sums].transform(lambda s:s.rolling(4,min_periods=4).sum())
    # §20: a missing week must not be replaced by an older dealer row in a rolling window.
    contiguous=w.groupby('dealer_id').week.shift(3).eq(w.week-3)
    r=r.where(contiguous)
    out=w.merge(d,on='dealer_id');out.index=w.index
    # §8.1 ratios are calculated from sums, not averages of weekly ratios.
    def ratio(a,b): return a/b.replace(0,np.nan)
    out['sales']=100*ratio(r.retail_units,r.retail_target)
    out['dealer_growth']=100*(ratio(r.retail_units,r.py_retail)-1)
    out['market_growth']=100*(ratio(r.market_units,r.py_market)-1)
    out['growth']=out.dealer_growth-out.market_growth
    out['aged']=100*ratio(w.aged_stock_value,w.stock_value)
    out['overdue']=100*ratio(w.overdue_30_amt,w.receivables_total)
    out['non_disputed_overdue']=100*ratio(w.overdue_30_amt-w.disputed_amt,w.receivables_total)
    out['ontime']=100*ratio(r.ontime_jobs,r.service_jobs)
    out['complaints']=100*ratio(r.complaints,r.service_jobs)
    out['share']=ratio(r.retail_units,r.market_units)
    out['wholesale_ratio']=ratio(r.wholesale_units,r.retail_units)
    out['feed_age_days']=7*(w.week-w.payments_updated_week)
    out['stale']=w.week-w.payments_updated_week>cfg['stale_weeks']
    out['capital_at_risk']=w.overdue_30_amt-w.disputed_amt+w.aged_stock_value
    out['urgent']=(w.severe_unresolved>0)|(out.non_disputed_overdue>=cfg['urgent_overdue'])
    out['incomplete']=False;out['index']=0.
    for k,spec in cfg['indicators'].items():
        value=out[k].mask(out.stale) if k=='overdue' else out[k]
        out[k+'_risk']=(100*(value-spec['b0'])/(spec['b100']-spec['b0'])).clip(0,100)
        out[k+'_contribution']=out[k+'_risk']*spec['weight']/100
        out['index']+=out[k+'_contribution'].fillna(0)
        out['incomplete']|=value.isna()
        group=out.groupby(['week','market_type'])[k]
        out[k+'_peer']=group.transform('median').where(group.transform('count')>=cfg['peer_min'])
    previous=out[['dealer_id','week','index','incomplete']].copy();previous['week']+=4
    out=out.merge(previous.rename(columns={'index':'previous_index','incomplete':'previous_incomplete'}),on=['dealer_id','week'],how='left')
    out['deterioration']=(out['index']-out.previous_index).mask(out.incomplete|out.previous_incomplete.fillna(True).astype(bool))
    out['base_tier']=[tier(i,g,u,cfg) for i,g,u in zip(out['index'],out.deterioration,out.urgent)]
    out['peer_size']=out.groupby(['week','market_type']).dealer_id.transform('count')
    return out[out.week>=4].reset_index(drop=True)


def adjusted_all(cfg=None):
    """CONTEXT §9 and A2/A5: adjust explicitly without reweighting."""
    cfg=cfg or defaults();a=indicators_all(cfg);a['raw_index']=a['index'];a['adjustments']=[[] for _ in range(len(a))]
    a['market_adjustment']=(a.market_growth<=cfg['market_down'])&(a.growth>=cfg['market_gap'])
    a['new_outlet']=(a.week-a.outlet_open_week+1)<cfg['new_outlet_weeks']
    for i,row in a.iterrows():
        notes=[]
        if row.market_adjustment: notes.append('Target unrealistic for this market; review the target, not the dealer')
        if row.disputed_amt>0: notes.append('Disputed invoices excluded; resolve with manufacturer')
        if row.new_outlet: notes.append('New outlet: ramp target; growth shown as context only')
        a.at[i,'adjustments']=notes
    values=a.overdue.where(a.disputed_amt<=0,a.non_disputed_overdue).mask(a.stale)
    spec=cfg['indicators']['overdue'];a['overdue_risk']=(100*(values-spec['b0'])/(spec['b100']-spec['b0'])).clip(0,100)
    a['overdue_contribution']=a.overdue_risk*spec['weight']/100
    # §9 new outlet: per-week ramp targets summed over the rolling window.
    for i,row in a[a.new_outlet].iterrows():
        ages=np.array([max(1,w-row.outlet_open_week+1) for w in range(int(row.week)-3,int(row.week)+1)])
        ramp=np.minimum(1,ages/cfg['new_outlet_weeks']).mean()
        a.at[i,'sales_risk']=risk(row.sales/ramp,**{k:cfg['indicators']['sales'][k] for k in ['b0','b100']})
    for k in ['sales','growth']:
        a.loc[a.market_adjustment,k+'_risk']=0
    a.loc[a.new_outlet,'growth_risk']=0
    for k,spec in cfg['indicators'].items(): a[k+'_contribution']=a[k+'_risk']*spec['weight']/100
    a['adjusted_index']=a[[k+'_contribution' for k in cfg['indicators']]].sum(axis=1)
    prev=a[['dealer_id','week','adjusted_index','incomplete']].copy();prev.week+=4
    a=a.merge(prev.rename(columns={'adjusted_index':'previous_adjusted','incomplete':'prior_incomplete'}),on=['dealer_id','week'],how='left')
    a['adjusted_change']=(a.adjusted_index-a.previous_adjusted).mask(a.incomplete|a.prior_incomplete.fillna(True).astype(bool))
    a['recovering']=(a.adjusted_change<=-cfg['recovering_drop'])&(a.adjusted_index<cfg['high'])&~a.urgent
    a['adjusted_tier']=[tier(i,g,u,cfg) for i,g,u in zip(a.adjusted_index,a.adjusted_change,a.urgent)]
    return a


def pattern_flags(dealer_id,week,cfg):
    # §10, A6: completed four-week blocks only; no look-ahead.
    if week<4*cfg['pattern_blocks']: return dict(monthend=False,cutoff=False,stock=False,evidence=['Insufficient history'])
    w=db.read('weekly');d=db.read('dealers');w=w[w.week<=week].copy();w['block']=(w.week-1)//4
    last=week//4-1;w=w[w.block.between(last-3,last)]
    # §10, §20: each of the four pattern blocks must contain all four dealer weeks.
    own=w[w.dealer_id==dealer_id]
    if len(own)!=16 or own.groupby('block').week.nunique().ne(4).any():
        return dict(monthend=False,cutoff=False,stock=False,evidence=['Insufficient history'])
    sums=w.groupby(['dealer_id','block']).retail_units.sum();ends=w[w.week%4==0].set_index(['dealer_id','block'])
    shape=(100*ends.retail_units/sums).rename('shape').reset_index().merge(d[['dealer_id','market_type']],on='dealer_id')
    shape['median']=shape.groupby(['market_type','block'])['shape'].transform('median');shape['size']=shape.groupby(['market_type','block']).dealer_id.transform('count')
    own=shape[shape.dealer_id==dealer_id];hits=((own['shape']-own['median']>=cfg['monthend_gap'])&(own['size']>=cfg['peer_min'])).sum()
    ownw=w[w.dealer_id==dealer_id];cut=ownw[ownw.week%4==0].set_index('block').overdue_30_amt;mid=ownw[ownw.week%4!=0].groupby('block').overdue_30_amt.mean();ratios=cut/mid.replace(0,np.nan);cut_hits=(ratios<cfg['cutoff_ratio']).sum()
    evidence=[]
    if hits>=cfg['pattern_hits']: evidence.append(f"Sold {own['shape'].mean():.0f}% of the month's units in the last week vs peers {own['median'].mean():.0f}%, in {hits} of 4 months: pattern worth checking")
    if cut_hits>=cfg['pattern_hits']: evidence.append(f'Overdue falls to {100*ratios.mean():.0f}% of its mid-month level at month-end in {cut_hits} of 4 months: pattern worth checking')
    return dict(monthend=bool(hits>=cfg['pattern_hits']),cutoff=bool(cut_hits>=cfg['pattern_hits']),stock=False,evidence=evidence)


def _snapshot(week,cfg,all_rows):
    rows=all_rows[all_rows.week==week].copy(); dealers=db.read('dealers');result=[]
    for d in dealers.itertuples():
        match=rows[rows.dealer_id==d.dealer_id]
        if match.empty:
            result.append(dict(dealer_id=d.dealer_id,name=d.name,region=d.region,market_type=d.market_type,week=week,group='Fix data',status='Fix data',sort_rank=4,reason=f'No data received for week {week}',incomplete=True,capital_at_risk=0,adjusted_index=np.nan,raw_index=np.nan,adjusted_change=np.nan,flags={},adjustments=[],situation='Fix data'));continue
        r=match.iloc[0].to_dict();flags=pattern_flags(d.dealer_id,week,cfg)
        before=all_rows[(all_rows.dealer_id==d.dealer_id)&(all_rows.week==week-4)]
        flags['stock']=bool(not before.empty and r['wholesale_ratio']>=cfg['stock_ratio'] and r['aged']-before.iloc[0].aged>=cfg['aged_increase'] and r['sales']>=cfg['stock_sales'])
        if flags['stock']: flags['evidence'].append(f"Wholesale/retail {r['wholesale_ratio']:.2f}; aged stock {r['aged']:.1f}%: pattern worth checking")
        opportunity=r['share']<cfg['opportunity_share']*rows[rows.market_type==r['market_type']]['share'].median() and r['market_growth']>0 and r['adjusted_index']<cfg['elevated']
        better=(r['raw_index']>=cfg['elevated'] or r['recovering']) and r['adjusted_tier']=='Routine' and not r['urgent']
        if r['urgent'] or r['adjusted_tier'] in ['High','Elevated']: group='Clear problems';status=r['adjusted_tier']
        elif r['stale'] or r['incomplete']: group='Fix data';status='Fix data'
        elif any(flags[k] for k in ['monthend','cutoff','stock']): group='Hidden risk';status='Pattern check'
        elif better: group='Better than they look';status='Routine'
        elif opportunity: group='Room to grow';status='Routine'
        else: group='Stars';status='Routine'
        c=lambda k:r[k+'_contribution']
        # §11.1 first matching situation; approved A1 direct adjustment selection.
        if r['severe_unresolved']>0: situation='Severe unresolved complaint'
        elif r['stale'] and not r['urgent']: situation='Fix data'
        elif (flags['monthend'] or flags['cutoff']) and r['adjusted_tier']=='Routine': situation='Hidden risk (patterns)'
        elif r['disputed_amt']>0 and c('overdue')<cfg['dispute_contribution']: situation='Disputed invoices'
        elif c('overdue')>=cfg['joint_receivables'] and c('aged')>=cfg['joint_aged']: situation='Stock build-up with payment strain'
        elif c('overdue')>=cfg['payment_contribution']: situation='Payment strain'
        elif c('aged')>=cfg['aged_contribution']: situation='Ageing inventory'
        elif c('ontime')+c('complaints')>=cfg['service_contribution']: situation='Service erosion'
        elif r['market_adjustment']: situation='Market-driven shortfall'
        elif c('sales')+c('growth')>=cfg['sales_contribution']: situation='Sales opportunity gap'
        elif opportunity: situation='Room to grow'
        else: situation='No action'
        words=dict(sales='% of target',growth=' pp vs market',aged='% of stock aged 90+ days',overdue='% of payments 30+ days late',ontime='% of service jobs on time',complaints=' complaints per 100 jobs')
        keys=sorted([k for k in cfg['indicators'] if c(k)>=cfg['reason_min']],key=c,reverse=True)[:3]
        reason=' and '.join(f"{r[k]:.1f}{words[k]} (peers {r[k+'_peer']:.1f})" for k in keys) or 'Healthy on the available indicators'
        if r['sales']>=100 and keys: reason='Sales are on or above target, but '+reason
        if group=='Hidden risk': reason='; '.join(flags['evidence'])
        if group=='Fix data': reason=f"Payment data is {r['feed_age_days']:.0f} days old, so the score is incomplete"
        if group=='Better than they look': reason=f"Raw score {r['raw_index']:.1f}, but "+('; '.join(r['adjustments']) or 'Recovering: the adjusted score is falling')
        if r['severe_unresolved']>0: reason='A severe complaint is still unresolved'
        r.update(group=group,status=status,sort_rank=['Urgent','High','Elevated','Pattern check','Fix data','Routine'].index(status),flags=flags,reason=reason,situation=situation)
        result.append(r)
    return pd.DataFrame(result)


def snapshot(asof_week,cfg=None):
    cfg=cfg or defaults();a=adjusted_all(cfg);now=_snapshot(asof_week,cfg,a);old=_snapshot(asof_week-1,cfg,a).set_index('dealer_id')
    tags=[]
    for r in now.itertuples():
        prior=old.loc[r.dealer_id];active=r.sort_rank<5;was=prior.sort_rank<5
        tags.append('New' if active and not was else 'Worse' if r.sort_rank<prior.sort_rank else 'Better' if r.sort_rank>prior.sort_rank else 'Same')
    now['since_last_week']=tags
    from planner.playbooks import recommendation
    now['plan']=[recommendation(r,cfg) for r in now.to_dict('records')]
    return now.sort_values(['sort_rank','capital_at_risk','adjusted_index'],ascending=[True,False,False]).reset_index(drop=True)


def detection_report(asof_week=24):
    s=snapshot(asof_week);return s[['name','raw_index','adjusted_index','adjusted_change','status','group']]
