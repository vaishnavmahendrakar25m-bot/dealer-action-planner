"""SQLite persistence, CONTEXT §7.2. Connections are short-lived."""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
import pandas as pd

SCHEMA = {'dealers': 'dealer_id TEXT PRIMARY KEY, name TEXT, region TEXT, market_type TEXT, manager TEXT, outlet_open_week INTEGER, base_retail REAL, avg_cost REAL, avg_price REAL, market_share_base REAL, sim_label TEXT', 'weekly': 'dealer_id TEXT, week INTEGER, retail_units REAL, wholesale_units REAL, retail_target REAL, py_retail REAL, market_units REAL, py_market REAL, stock_value REAL, aged_stock_value REAL, receivables_total REAL, overdue_30_amt REAL, disputed_amt REAL, payments_updated_week REAL, service_jobs REAL, ontime_jobs REAL, repeat_repairs REAL, complaints REAL, severe_unresolved REAL, PRIMARY KEY (dealer_id, week)', 'vehicles': 'vehicle_id TEXT PRIMARY KEY, dealer_id TEXT, model TEXT, variant TEXT, age_days INTEGER, cost REAL', 'demand': 'dealer_id TEXT, model TEXT, variant TEXT, qty INTEGER, required_by_days INTEGER, confirmed INTEGER', 'events': 'dealer_id TEXT, kind TEXT, onset_week INTEGER, ramp_weeks INTEGER, intensity REAL', 'actions': 'id INTEGER PRIMARY KEY, dealer_id TEXT, week_created INTEGER, group_label TEXT, issue TEXT, playbook TEXT, owner TEXT, due_date TEXT, effort_hrs REAL, baseline_json TEXT, status TEXT, decision TEXT, override_reason TEXT, created_at TEXT, evidence_refs TEXT, intended_result TEXT, review_date TEXT, approval_status TEXT', 'sim_meta': 'seed INTEGER, history_weeks INTEGER', 'imports': 'id INTEGER PRIMARY KEY, source_file TEXT, accepted_rows INTEGER, imported_at TEXT'}

@contextmanager
def connect():
    path = Path(os.environ.get('DEALER_DB', 'data/dealer_planner.db'))
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        with con:
            yield con
    finally:
        con.close()

def create_tables():
    with connect() as con:
        for name, columns in SCHEMA.items():
            con.execute(f'CREATE TABLE IF NOT EXISTS {name} ({columns})')

def read(table):
    if table not in SCHEMA:
        raise ValueError('Unknown table')
    with connect() as con:
        return pd.read_sql_query(f'SELECT * FROM {table}', con)

def write(table, frame):
    if table not in SCHEMA:
        raise ValueError('Unknown table')
    with connect() as con:
        frame.to_sql(table, con, if_exists='append', index=False)

def execute(sql, parameters=()):
    with connect() as con:
        cursor = con.execute(sql, parameters)
        return cursor.fetchall()

def version():
    # §19: include row counts and SQLite file changes to invalidate same-week imports/actions.
    with connect() as con:
        week, rows = con.execute('SELECT COALESCE(MAX(week),0), COUNT(*) FROM weekly').fetchone()
        events = con.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    path = Path(os.environ.get('DEALER_DB', 'data/dealer_planner.db'))
    return f'{week}:{rows}:{events}:{path.stat().st_mtime_ns}'
