"""CSV import acceptance and rejection, CONTEXT §20."""

import pandas as pd

from planner import db, importer, simulator


def test_partial_week_accepts_missing_dealer_only(tmp_path, monkeypatch):
    monkeypatch.setenv('DEALER_DB', str(tmp_path / 'import.db'))
    db.create_tables()
    dealers = simulator.dealer_catalogue()
    db.write('dealers', dealers)
    rows = simulator.make_week(dealers.iloc[:2], 24, 42, db.read('events'))
    db.write('weekly', rows.iloc[:1])

    file_rows = pd.concat([rows.iloc[1:], rows.iloc[:1]], ignore_index=True)
    clean, rejected = importer.check_weekly(file_rows)
    assert clean.dealer_id.tolist() == [rows.iloc[1].dealer_id]
    assert len(rejected) == 1
    assert 'duplicate dealer-week' in rejected.iloc[0].error

    accepted, rejected = importer.append_clean(file_rows, 'weekly.csv')
    assert (accepted, len(rejected)) == (1, 1)
    assert len(db.read('weekly')) == 2
    assert db.read('imports').accepted_rows.tolist() == [1]
    assert importer.check_weekly(file_rows)[0].empty


def test_rejects_invalid_values_and_wrong_week(tmp_path, monkeypatch):
    monkeypatch.setenv('DEALER_DB', str(tmp_path / 'import.db'))
    db.create_tables()
    dealers = simulator.dealer_catalogue()
    db.write('dealers', dealers)
    row = simulator.make_week(dealers.iloc[:1], 24, 42, db.read('events'))
    db.write('weekly', row)
    bad = row.copy()
    bad.loc[0, 'dealer_id'] = 'D02'
    bad.loc[0, 'week'] = 26
    bad.loc[0, 'overdue_30_amt'] = bad.loc[0, 'receivables_total'] + 1
    bad.loc[0, 'payments_updated_week'] = 27
    clean, rejected = importer.check_weekly(bad)
    assert clean.empty
    assert 'week must be 24 or 25' in rejected.iloc[0].error
    assert 'overdue_30_amt exceeds receivables_total' in rejected.iloc[0].error
    assert 'payments_updated_week is after week' in rejected.iloc[0].error
