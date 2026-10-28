import pandas as pd
import pytest
from planner import db, simulator as sim

@pytest.fixture
def history(tmp_path,monkeypatch):
    monkeypatch.setenv('DEALER_DB',str(tmp_path/'sim.db'));sim.generate_history();return db.read('weekly')

def test_reproducibility(history):
    original=history.copy();sim.reset(42);pd.testing.assert_frame_equal(original,db.read('weekly'))
    sim.reset(43);assert not original.equals(db.read('weekly'))
    assert len(original)==720 and original.dealer_id.nunique()==30
    assert (original.aged_stock_value<=original.stock_value).all()
    assert (original.overdue_30_amt<=original.receivables_total).all()
    assert (original.disputed_amt<=original.overdue_30_amt).all()
    assert (original.select_dtypes('number')>=0).all().all()

def test_advance_events(history):
    sim.inject_event('D06','stock_push',1)
    pd.testing.assert_frame_equal(history,db.read('weekly'))
    assert sim.advance_week()==25
    actual=db.read('weekly');pd.testing.assert_frame_equal(history,actual[actual.week<=24].reset_index(drop=True))
    assert len(actual)==750
    base=sim.make_week(db.read('dealers'),25,42,db.read('events').iloc[:0])
    assert actual[(actual.week==25)&(actual.dealer_id=='D06')].iloc[0].stock_value>base[base.dealer_id=='D06'].iloc[0].stock_value
