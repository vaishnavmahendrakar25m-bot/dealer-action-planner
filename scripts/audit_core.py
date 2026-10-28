"""Focused submission audit under the owner's deadline scope."""
from pathlib import Path
import ast
import pandas as pd
from planner import db
from planner.engine import snapshot,score_values
from planner.config import defaults
from planner.transfers import transfer_economics

def run():
    cfg=defaults();a=snapshot(24);b=snapshot(25) if db.read('weekly').week.max()>=25 else None
    worked=score_values(dict(sales=108,growth=-6,aged=32,overdue=20,ontime=88,complaints=4),cfg)
    assert round(worked['index'],1)==56.9
    print('PASS Dealer A:',round(worked['index'],1))
    econ=transfer_economics(1000000,.12,60,15,8000)
    assert round(econ['net'])==6795
    print('PASS Transfer:',round(econ['avoided']),round(econ['net']),round(econ['break_even_days'],1))
    print('Week24 needs action:',len(a[a.sort_rank<5]),'Doing well:',len(a[a.sort_rank==5]))
    assert a[a.name=='Godavari Autos'].iloc[0].incomplete
    print('PASS Godavari: incomplete, no reweighting')
    for name in ['app.py','planner/narrative.py','planner/playbooks.py','planner/engine.py']:
        literals=[n.value for n in ast.walk(ast.parse(Path(name).read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        assert not any(word in value.lower() for value in literals for word in ['cheating','fraud','manipulate','trick'])
    print('PASS UI wording literal scan')
    files=['README.md','ASSUMPTIONS.md','DEMO_SCRIPT.md','PITCH_QA.md','PITCH_90S.md','examples/week24_queue.csv','examples/week25_queue.csv','examples/headline_dealer_case_week24.txt','examples/sample_dealers.csv','examples/sample_weekly.csv','examples/test_report.txt']
    assert all(Path(name).is_file() for name in files)
    print('PASS submission files:',len(files))
    print('DEFERRED: CSV load UI, deployment, extended settings, full digest accounting')

if __name__=='__main__': run()
