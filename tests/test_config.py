import pytest
from planner.config import defaults, to_json, from_json, week_end
from planner import db

def test_config_roundtrip():
    cfg=defaults()
    assert sum(v['weight'] for v in cfg['indicators'].values()) == 100
    assert all(v['b0'] != v['b100'] for v in cfg['indicators'].values())
    assert from_json(to_json(cfg)) == cfg
    assert str(week_end(24)) == '2026-10-25'
    cfg['indicators']['sales']['weight']=0
    with pytest.raises(ValueError): to_json(cfg)

def test_schema_and_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv('DEALER_DB',str(tmp_path/'test.db'))
    db.create_tables()
    assert db.read('weekly').empty
    assert {'evidence_refs','intended_result','review_date','approval_status'} <= set(db.read('actions').columns)
    assert db.version().startswith('0:0:0:')
