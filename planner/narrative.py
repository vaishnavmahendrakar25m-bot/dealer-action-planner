"""Deterministic templates only, CONTEXT §15/A11."""
def brief(row):
    if row['group']=='Better than they look':
        return f"What looks weak: raw score {row['raw_index']:.1f}.\nContext: {row['reason']}.\nConfirm: supporting records and next week's trend."
    return f"{row['reason']}.\nInspect: {row['plan']['evidence_refs']}.\nPlan: {row['plan']['action']} · {row['plan']['owner']} · due {row['plan']['due_date']}."
