"""Demonstration assumptions; CONTEXT §§8–14. No industry benchmarks."""
import json
from copy import deepcopy
from datetime import date, timedelta

INDICATORS = {
    'sales': (15, 100, 70, 'Sales vs target', '%'),
    'growth': (10, 0, -15, 'Growth vs market', 'pp'),
    'aged': (20, 10, 40, 'Stock aged 90+ days', '%'),
    'overdue': (25, 2, 20, 'Payments 30+ days late', '%'),
    'ontime': (15, 95, 70, 'Service jobs on time', '%'),
    'complaints': (15, 1, 6, 'Complaints per 100 jobs', 'per 100'),
}
# CONTEXT §§8–11: all scoring and selection thresholds are configurable assumptions.
DEFAULT_CONFIG = {
    'indicators': {k: dict(weight=w, b0=a, b100=b, label=l, unit=u)
                   for k, (w,a,b,l,u) in INDICATORS.items()},
    'high': 60, 'elevated': 35, 'deterioration': 8, 'urgent_overdue': 20,
    'trend_weeks': 4, 'stale_weeks': 1, 'peer_min': 5,
    'monthend_gap': 15, 'cutoff_ratio': .6, 'pattern_blocks': 4, 'pattern_hits': 3,
    'stock_ratio': 1.15, 'aged_increase': 3, 'stock_sales': 100,
    'market_down': -8, 'market_gap': -4, 'new_outlet_weeks': 26,
    'recovering_drop': 8, 'opportunity_share': .7, 'opportunity_growth': 0,
    'reason_min': 3, 'reason_max': 3, 'dispute_contribution': 8,
    'joint_receivables': 8, 'joint_aged': 8, 'payment_contribution': 12,
    'aged_contribution': 10, 'service_contribution': 8, 'sales_contribution': 8,
    'deferral_return': 5, 'verdict_change': 3,
    'transfer': dict(rate=.12, same_region=8000, cross_region=15000,
                     days_held=60, days_transferred=15, same_days=2, cross_days=4),
    'kpis': ['Revenue this month', 'Retail units', 'Overdue 30+ days',
             'Need action', 'Capital at risk'],
    'playbooks': {'Stock build-up with payment strain': {'action': 'Joint finance and inventory review; check transfer option', 'owner': 'Regional finance lead + inventory manager', 'effort_hrs': 3.0, 'due_days': 7}, 'Payment strain': {'action': 'Finance-led collection review', 'owner': 'Regional finance lead', 'effort_hrs': 2.0, 'due_days': 7}, 'Ageing inventory': {'action': 'Inventory intervention: pricing, merchandising, transfers', 'owner': 'Regional inventory manager', 'effort_hrs': 2.0, 'due_days': 7}, 'Service erosion': {'action': 'Identify the bottleneck; target staffing, parts or process support', 'owner': 'Regional service manager', 'effort_hrs': 4.0, 'due_days': 10}, 'Severe unresolved complaint': {'action': 'Escalate and visit', 'owner': 'Service head', 'effort_hrs': 1.5, 'due_days': 2}, 'Sales opportunity gap': {'action': 'Targeted sales coaching and stock support', 'owner': 'Regional sales manager', 'effort_hrs': 3.0, 'due_days': 10}, 'Market-driven shortfall': {'action': 'Review target realism against the market', 'owner': 'Regional manager', 'effort_hrs': 1.0, 'due_days': 10}, 'Hidden risk (patterns)': {'action': 'Verify records: check daily sales and payment data, ask the dealer to explain, review scheme timing', 'owner': 'Regional analyst', 'effort_hrs': 2.0, 'due_days': 7}, 'Fix data': {'action': 'Correct the data feed before drawing conclusions', 'owner': 'Data owner', 'effort_hrs': 0.5, 'due_days': 3}, 'Room to grow': {'action': 'Plan market-share growth support', 'owner': 'Sales development manager', 'effort_hrs': 2.0, 'due_days': 14}, 'Disputed invoices': {'action': "Resolve disputed invoices with the manufacturer's finance team", 'owner': 'Regional finance lead', 'effort_hrs': 2.0, 'due_days': 10}},
}

def validate(cfg):
    if abs(sum(v['weight'] for v in cfg['indicators'].values()) - 100) > 1e-8:
        raise ValueError('Weights must sum to 100')
    for item in cfg['indicators'].values():
        if item['weight'] < 0 or item['b0'] == item['b100']:
            raise ValueError('Invalid weight or equal risk boundaries')
    if cfg['elevated'] >= cfg['high']:
        raise ValueError('Elevated must be below High')
    return cfg

def to_json(cfg):
    return json.dumps(validate(cfg), sort_keys=True)

def from_json(value):
    return validate(json.loads(value))

def defaults():
    return deepcopy(DEFAULT_CONFIG)

def week_end(week):
    # CONTEXT §7.1 and amendment A9: synthetic weeks, never wall-clock dates.
    return date(2026, 5, 11) + timedelta(weeks=int(week)-1, days=6)
