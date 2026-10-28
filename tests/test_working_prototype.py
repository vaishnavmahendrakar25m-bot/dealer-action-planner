import json
import pytest
from planner import db,simulator,actions
from planner.config import defaults
from planner.engine import snapshot
from planner.transfers import transfer_economics,transfer_candidates
from planner.kpis import scorecard
from planner.narrative import brief

@pytest.fixture
def live(tmp_path,monkeypatch):
    monkeypatch.setenv('DEALER_DB',str(tmp_path/'prototype.db'));simulator.generate_history();return snapshot(24)

def test_transfer_worked_example():
    a=transfer_economics(1000000,.12,60,15,8000)
    assert round(a['avoided'])==14795 and round(a['net'])==6795
    assert round(a['break_even_days'],1)==24.3
    assert round(transfer_economics(1000000,.12,60,40,8000)['net'])==-1425

def test_kpis_transfers_summary(live):
    k=scorecard(24);assert k['need_action']==(live.sort_rank<5).sum()
    assert k['need_action']+k['doing_well']==30
    assert k['capital']==pytest.approx(live[live.sort_rank<5].capital_at_risk.sum())
    row=live[live.name=='Sri Venkateshwara Motors'].iloc[0].to_dict()
    assert transfer_candidates(row['dealer_id'])
    assert transfer_candidates(row['dealer_id'],asof_week=23)==[]
    assert brief(row)==brief(row)
    assert not any(word in brief(row).lower() for word in ['cheat','fraud','trick','manipulate','because','caused'])

def test_actions(live):
    row=live[live.name=='Sri Venkateshwara Motors'].iloc[0].to_dict()
    with pytest.raises(ValueError): actions.save(row,'deferred')
    actions.save(row,'deferred','Waiting for records')
    assert len(db.read('actions'))==1
    assert row['dealer_id'] in set(actions.visible(live).dealer_id)  # A9 urgent cannot be hidden.
    with pytest.raises(ValueError): actions.save(row)
    assert actions.verdict(50,46)=='Improving'
    assert actions.verdict(50,54)=='Worse'
    assert actions.verdict(50,51)=='No change'
    row=live[live.name=='Deccan Wheels'].iloc[0].to_dict();actions.save(row,'deferred','Waiting for dealer')
    assert row['dealer_id'] not in set(actions.visible(live).dealer_id)
    changed=live.copy();changed.loc[changed.dealer_id==row['dealer_id'],'adjusted_index']+=5
    assert row['dealer_id'] in set(actions.visible(changed).dealer_id)

def test_partial_week_does_not_reuse_old_rows(live):
    row=simulator.make_week(db.read('dealers'),25,42,db.read('events')).iloc[:1]
    db.write('weekly',row)
    current=snapshot(25);missing=current[current.dealer_id!=row.iloc[0].dealer_id]
    assert len(missing)==29
    assert (missing.group=='Fix data').all()
    assert missing.adjusted_index.isna().all()
    assert missing.reason.str.contains('No data received for week 25').all()
