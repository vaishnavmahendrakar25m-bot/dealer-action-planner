import math
import pytest
from planner.engine import risk,score_values,tier,indicators_all
from planner.config import defaults
from planner import simulator as sim

def test_worked_example():
    cfg=defaults();v=dict(sales=108,growth=-6,aged=32,overdue=20,ontime=88,complaints=4)
    a=score_values(v,cfg)
    assert round(a['index'],1)==56.9
    assert [round(a['risks'][k],1) for k in v]==[0,40,73.3,100,28,60]
    assert tier(a['index'],0,True,cfg)=='Urgent'
    assert risk(200,100,70)==0 and risk(60,100,70)==100
    assert risk(-1,2,20)==0 and risk(30,2,20)==100
    assert math.isnan(risk(float('nan'),2,20))

def test_stale_and_peers(tmp_path,monkeypatch):
    monkeypatch.setenv('DEALER_DB',str(tmp_path/'e.db'));sim.generate_history()
    a=indicators_all();s=a[(a.name=='Godavari Autos')&(a.week==24)].iloc[0]
    assert s.incomplete and math.isnan(s.overdue_contribution) and math.isnan(s.deterioration)
    assert s['index']==pytest.approx(sum(s[k+'_contribution'] for k in defaults()['indicators'] if k!='overdue'))
    cfg=defaults();cfg['peer_min']=11
    assert indicators_all(cfg).sales_peer.isna().all()
