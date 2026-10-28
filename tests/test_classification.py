from planner import db,simulator as sim
from planner.engine import snapshot, pattern_flags
from planner.config import defaults

def test_seeded_groups(tmp_path,monkeypatch):
    monkeypatch.setenv('DEALER_DB',str(tmp_path/'classification.db'));sim.generate_history()
    s=snapshot(24).set_index('name')
    expected={'Sri Venkateshwara Motors':('Clear problems','Urgent'),'Lakshmi Auto':('Clear problems','Urgent'),'Deccan Wheels':('Clear problems','Elevated'),'Marina Motors':('Clear problems','High'),'Coastal Cars':('Clear problems','High'),'Charminar Wheels':('Hidden risk','Pattern check'),'Nizam Auto':('Hidden risk','Pattern check'),'Godavari Autos':('Fix data','Fix data'),'Kaveri Cars':('Better than they look','Routine'),'Coimbatore Cars':('Better than they look','Routine'),'Pondy Wheels':('Better than they look','Routine'),'Hosur Road Autos':('Better than they look','Routine'),'Malnad Motors':('Room to grow','Routine')}
    for name,(group,status) in expected.items():
        assert (s.loc[name,'group'],s.loc[name,'status'])==(group,status),s[['group','status','raw_index','adjusted_index','adjusted_change']].to_string()
    healthy=db.read('dealers').query("sim_label=='healthy'").name
    assert not s.loc[healthy,'status'].isin(['Urgent','High']).any()
    assert (s.loc[healthy,'status']=='Elevated').sum()<=2
    assert s.loc['Sri Venkateshwara Motors','sales']>=100
    assert s.loc['Hosur Road Autos','adjusted_change']<=-8
    assert pattern_flags('D01',12,defaults())['evidence']==['Insufficient history']
    sim.advance_week();assert (snapshot(25).set_index('name').status.reindex(s.index) != s.status).any()
