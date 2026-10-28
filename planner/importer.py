"""Local weekly CSV checks and append, following CONTEXT §20."""

from datetime import datetime, timezone

import pandas as pd

from planner import db


def weekly_columns():
    with db.connect() as con:
        return [row[1] for row in con.execute('PRAGMA table_info(weekly)')]


def check_weekly(frame):
    """Return clean rows and a report of rejected rows; never change source values."""
    columns = weekly_columns()
    missing = [name for name in columns if name not in frame.columns]
    extra = [name for name in frame.columns if name not in columns]
    if missing or extra:
        raise ValueError(f'CSV columns must match weekly exactly. Missing: {missing}; extra: {extra}')

    data = frame[columns].copy()
    data['dealer_id'] = data['dealer_id'].astype('string').str.strip()
    numeric = [name for name in columns if name != 'dealer_id']
    for name in numeric:
        data[name] = pd.to_numeric(data[name], errors='coerce')

    existing = db.read('weekly')
    known = set(db.read('dealers').dealer_id)
    existing_keys = set(zip(existing.dealer_id, existing.week))
    latest = int(existing.week.max()) if not existing.empty else 0
    in_file_duplicates = data.duplicated(['dealer_id', 'week'], keep=False)
    errors = []
    for position, row in enumerate(data.itertuples(index=False, name=None)):
        values = dict(zip(columns, row))
        problems = []
        dealer = values['dealer_id']
        week = values['week']
        if pd.isna(dealer) or not str(dealer).strip():
            problems.append('missing dealer_id')
        elif dealer not in known:
            problems.append('unknown dealer_id')
        if any(pd.isna(values[name]) for name in numeric):
            problems.append('missing or nonnumeric required value')
        if any(pd.notna(values[name]) and values[name] < 0 for name in numeric):
            problems.append('negative value')
        if pd.notna(week):
            if week < 1 or week != int(week):
                problems.append('week must be a positive integer')
            elif week not in (latest, latest + 1):
                problems.append(f'week must be {latest} or {latest + 1}')
        already_present = pd.notna(dealer) and pd.notna(week) and (dealer, int(week)) in existing_keys
        if in_file_duplicates.iloc[position] or already_present:
            problems.append('duplicate dealer-week')
        pairs = [('overdue_30_amt', 'receivables_total'),
                 ('disputed_amt', 'overdue_30_amt'),
                 ('aged_stock_value', 'stock_value')]
        for part, total in pairs:
            if pd.notna(values[part]) and pd.notna(values[total]) and values[part] > values[total]:
                problems.append(f'{part} exceeds {total}')
        if pd.notna(values['payments_updated_week']) and pd.notna(week) and values['payments_updated_week'] > week:
            problems.append('payments_updated_week is after week')
        errors.append('; '.join(problems))

    report = data[['dealer_id', 'week']].copy()
    report.insert(0, 'csv_row', range(2, len(data) + 2))
    report['error'] = errors
    clean = data.loc[report.error == ''].copy()
    rejected = report.loc[report.error != ''].copy()
    if not clean.empty:
        clean['week'] = clean['week'].astype(int)
    return clean, rejected


def append_clean(frame, source_file):
    """Recheck and append accepted rows in one SQLite transaction (§20)."""
    clean, rejected = check_weekly(frame)
    if clean.empty:
        return 0, rejected
    columns = weekly_columns()
    markers = ','.join('?' for _ in columns)
    names = ','.join(columns)
    with db.connect() as con:
        con.executemany(
            f'INSERT INTO weekly ({names}) VALUES ({markers})',
            [tuple(value.item() if hasattr(value, 'item') else value for value in row)
             for row in clean.itertuples(index=False, name=None)],
        )
        con.execute('INSERT INTO imports (source_file, accepted_rows, imported_at) VALUES (?,?,?)',
                    (source_file, len(clean), datetime.now(timezone.utc).isoformat()))
    return len(clean), rejected
