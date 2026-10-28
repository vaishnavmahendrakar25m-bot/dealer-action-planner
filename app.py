"""Dealer Action Planner prototype. UI rules: CONTEXT §§4–6."""
import json
import base64
from copy import deepcopy
from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st
from planner import db,simulator,actions,importer
from planner.config import defaults,week_end,to_json
from planner.engine import snapshot,indicators_all
from planner.kpis import scorecard,money,insight_sentence
from planner.narrative import brief
from planner.transfers import transfer_candidates,transfer_economics

st.set_page_config(page_title='Dealer Action Planner',page_icon='🚗',layout='centered')
hero = base64.b64encode(Path(__file__).with_name('static').joinpath('dealer-hero.jpg').read_bytes()).decode()
st.markdown(f'''<style>
    .stApp {{background:#f5f8fa}}
    .block-container {{padding-top:1rem;max-width:900px}}
    button {{min-height:44px;border-radius:10px!important}}
    div[data-testid="stMetric"] {{background:#fff;border:1px solid #e3ebef;border-radius:14px;padding:10px 14px;box-shadow:0 4px 18px rgba(16,45,74,.05)}}
    section[data-testid="stSidebar"] {{background:#edf3f6;border-right:1px solid #dbe6eb}}
    .dealer-hero {{min-height:162px;margin-bottom:14px;border-radius:18px;padding:23px 28px;background:linear-gradient(90deg,rgba(10,37,62,.92) 0%,rgba(10,37,62,.63) 54%,rgba(10,37,62,.08) 100%),url(data:image/jpeg;base64,{hero}) center 56%/cover no-repeat;box-shadow:0 12px 28px rgba(16,45,74,.16);display:flex;flex-direction:column;justify-content:center}}
    .dealer-hero h1 {{color:white!important;font-size:2rem!important;line-height:1.08;margin:4px 0 10px}}
    .dealer-hero p {{color:#e9f3f5;margin:0;font-size:.95rem;max-width:560px;line-height:1.45}}
    .dealer-hero small {{color:#9bd9d9;font-weight:700;letter-spacing:.11em;font-size:.72rem}}
    @media(max-width:500px){{.block-container{{padding:.6rem .75rem}}.dealer-hero{{min-height:128px;padding:16px 18px;background-position:64% center}}.dealer-hero h1{{font-size:1.42rem!important}}.dealer-hero p{{font-size:.8rem}}div[data-testid="stMetric"]{{padding:5px 8px}}div[data-testid="stVerticalBlock"]{{gap:.45rem}}div[data-testid="stHorizontalBlock"]{{flex-wrap:nowrap}}div[data-testid="stColumn"]{{min-width:0!important;flex:1!important}}div[data-testid="stMetricValue"]{{font-size:1.2rem!important}}}}
    </style>''',unsafe_allow_html=True)
db.create_tables()
if db.read('weekly').empty: simulator.generate_history()
latest=int(db.read('weekly').week.max())
has_uploads=not db.read('imports').empty
if 'page' not in st.session_state: st.session_state.page='Home'
if 'cfg' not in st.session_state: st.session_state.cfg=defaults()
cfg=st.session_state.cfg

def go(page,dealer=None):
    st.session_state.page=page
    if dealer is not None: st.session_state.dealer=dealer

def number(value):
    return 'Unavailable' if value is None or pd.isna(value) else f'{value:.1f}'

def show_status(status):
    colors={'Urgent':'red','High':'orange','Elevated':'orange','Pattern check':'blue','Fix data':'violet','Routine':'green'}
    st.badge(status,color=colors.get(status,'gray'))

def refresh():
    st.cache_data.clear();st.rerun()

@st.cache_data(show_spinner=False)
def load(week,config_json,version,region):
    return scorecard(week,json.loads(config_json),region)

with st.sidebar:
    st.header('Weekly controls')
    week=st.selectbox('As-of week',list(range(8,latest+1)),index=latest-8)
    region=st.selectbox('Region',['All','Hyderabad','Bengaluru','Chennai'])
    st.divider()
    st.subheader('Your data')
    st.button('Load weekly data',use_container_width=True,on_click=go,args=('Load weekly data',))
    st.caption('The initial history is simulated. Upload a weekly CSV to add your own rows.')
    st.divider()
    if st.button('Advance one week',disabled=has_uploads):
        simulator.advance_week();refresh()
    if has_uploads: st.caption('Simulation advance is paused after a CSV upload.')
    if not has_uploads:
        with st.expander('Inject event'):
            dealers=db.read('dealers');name=st.selectbox('Dealer',dealers.name)
            kind=st.selectbox('Event',['stock_push','cash_strain','service_erosion','market_dip','weak_conversion'])
            intensity=st.slider('Intensity',.3,1.,.6)
            if st.button('Queue event'):
                simulator.inject_event(dealers.set_index('name').loc[name,'dealer_id'],kind,intensity);st.success('Queued for next week')
    else:
        st.caption('Simulator events are paused after a CSV upload.')
    with st.expander('Reset simulation'):
        seed=st.number_input('Seed',min_value=0,value=42)
        confirm=st.checkbox('Replace uploaded rows, clear saved actions and regenerate simulated history' if has_uploads else 'Clear saved actions and regenerate simulated history')
        if st.button('Reset',disabled=not confirm): simulator.reset(int(seed));refresh()
    st.caption('Demonstration assumptions. Defaults fixed to CONTEXT. No external AI.')

if cfg!=defaults():
    st.warning('Custom settings active')
    if st.button('Reset to default'): st.session_state.cfg=defaults();refresh()
k=load(week,to_json(cfg),db.version(),region);s=k['snapshot'];active=actions.visible(s);need=active[active.sort_rank<5];well=s[s.sort_rank==5]
source='Simulated data + uploaded weekly rows' if has_uploads else 'Simulated data'
st.caption(f'Week {week} · {region if region!="All" else "South region"} · Data as of {week_end(week):%d %b %Y} · {source}')
page=st.session_state.page
if page!='Home': st.button('← Home',on_click=go,args=('Home',))

if page=='Home':
    insight=insight_sentence(dict(k,need_action=len(need),capital=need.capital_at_risk.sum()))
    st.markdown(f'<div class="dealer-hero"><small>WEEKLY DEALER REVIEW</small><h1>Dealer Action Planner</h1><p>{insight}</p></div>',unsafe_allow_html=True)
    st.button(f'Needs action ({len(need)})',type='primary',use_container_width=True,on_click=go,args=('Needs action',))
    st.button(f'Doing well ({len(well)})',use_container_width=True,on_click=go,args=('Doing well',))
    st.caption(f"Month-to-date retail: {k['retail_pct']:.0f}% of target · all money in INR")
    st.metric('Revenue this month',money(k['revenue']),f"{k['revenue_pct']:.0f}% of target · {money(k['revenue_change'])} vs prior month")
    a,b=st.columns(2)
    a.metric('Retail units',f"{k['retail']:,.0f}",f"{k['retail']-k['previous_retail']:+.0f} vs prior month")
    b.metric('Overdue 30+ days',f"{k['overdue_pct']:.1f}%",f"{k['overdue_pct']-k['previous_overdue']:+.1f} pp vs last week",delta_color='inverse')
    a,b=st.columns(2);a.metric('Need action',len(need),f"{len(need)-k['previous_need']:+d} vs last week",delta_color='inverse');b.metric('Capital at risk',money(need.capital_at_risk.sum()),f"{money(need.capital_at_risk.sum()-k['previous_capital'])} vs last week",delta_color='inverse')
    st.button('My actions',on_click=go,args=('My actions',))
    with st.expander('More targets'):
        st.dataframe(s[['name','sales','aged','ontime','complaints','share','wholesale_ratio']].rename(columns={'name':'Dealer','sales':'Sales % target','aged':'Aged stock %','ontime':'On-time %','complaints':'Complaints per 100','share':'Market share','wholesale_ratio':'Wholesale / retail'}),hide_index=True)
    with st.expander('Weekly digest preview'):
        st.caption('Display only; nothing is sent')
        for r in need.head(5).to_dict('records'): st.write(f"{r['name']} ({r['status']}): {r['reason']} · {money(r['capital_at_risk'])} · {r['plan']['action']}, due {r['plan']['due_date']}")

elif page=='Load weekly data':
    # CONTEXT §20: local CSV rows are checked and appended; existing rows are not replaced.
    st.title('Load weekly data')
    st.write('Add your own dealer-week rows. The file must use the exact weekly columns. Existing rows stay unchanged.')
    st.caption(f'Current latest week: {latest}. Add missing dealers for week {latest}, or rows for week {latest+1}.')
    st.download_button('Download blank weekly CSV template',','.join(importer.weekly_columns())+'\n',file_name='weekly_template.csv',mime='text/csv')
    next_week=pd.DataFrame('',index=range(len(db.read('dealers'))),columns=importer.weekly_columns())
    next_week['dealer_id']=db.read('dealers').dealer_id.values
    next_week['week']=latest+1
    st.download_button(f'Download week {latest+1} sheet with dealer IDs',next_week.to_csv(index=False),file_name=f'week_{latest+1}_template.csv',mime='text/csv')
    st.caption('Fill all numeric columns for dealers you want to load; remove unused rows before uploading.')
    uploaded=st.file_uploader('Choose weekly CSV',type=['csv'])
    if 'import_notice' in st.session_state: st.success(st.session_state.pop('import_notice'))
    if uploaded is not None:
        try:
            frame=pd.read_csv(uploaded,dtype={'dealer_id':str})
            clean,rejected=importer.check_weekly(frame)
            st.write(f'{len(clean)} clean rows · {len(rejected)} rejected rows')
            if not rejected.empty:
                st.dataframe(rejected.head(20),hide_index=True)
                st.caption('Rejected rows are not saved. Correct them in the CSV and upload again.')
            if st.button(f'Add {len(clean)} clean rows',disabled=clean.empty,type='primary'):
                accepted,again=importer.append_clean(frame,uploaded.name)
                st.session_state.import_notice=f'Added {accepted} rows. {len(again)} rows were rejected. Scores and lists have refreshed.'
                refresh()
        except (ValueError,pd.errors.ParserError) as error:
            st.error(str(error))

elif page in ['Needs action','Doing well']:
    st.title(page)
    if page=='Needs action':
        chosen=st.radio('Filter',['All','Clear problems','Hidden risk','Fix data'],horizontal=True)
        shown=need if chosen=='All' else need[need.group==chosen]
    else:
        # CONTEXT §6.3: let the manager open each Doing well group directly.
        chosen=st.radio('Filter',['All','Better than they look','Room to grow','Stars'],horizontal=True)
        shown=well.assign(group_rank=well.group.map({'Better than they look':0,'Room to grow':1,'Stars':2})).sort_values(['group_rank','capital_at_risk'],ascending=[True,False])
        if chosen!='All': shown=shown[shown.group==chosen]
    if shown.empty: st.info('No dealers in this view')
    last_group=None
    for r in shown.to_dict('records'):
        if page=='Doing well' and r['group']!=last_group:
            st.subheader(r['group']);last_group=r['group']
        with st.container(border=True):
            st.subheader(r['name']);show_status(r['status']);st.write(f"{r['status']} · {r['group']} · {r['region']} · {r['since_last_week']}")
            if r['group']=='Better than they look': st.caption('Check context')
            if r['group']=='Room to grow': st.caption(r['plan']['action'])
            st.write(r['reason']);st.caption(f"{money(r['capital_at_risk'])} capital at risk · 4-week change: {r['adjusted_change']:+.1f}" if pd.notna(r['adjusted_change']) else f"{money(r['capital_at_risk'])} · 4-week change unavailable")
            st.button('Open case',key=r['dealer_id'],on_click=go,args=('Dealer case',r['dealer_id']))

elif page=='Dealer case':
    row=s[s.dealer_id==st.session_state.dealer]
    if row.empty: st.info('Select this dealer’s region or All to view its case')
    else:
        r=row.iloc[0].to_dict();plan=r['plan']
        st.title(r['name']);show_status(r['status']);st.write(f"{r['status']} · {r['group']} · {r['market_type']}");st.write(r['reason'])
        facts=[('aged','Aged stock %'),('overdue','Payments late %'),('sales','Sales % target')]
        for key,label in facts:
            if key in r: st.write(f"**{label}: {number(r[key])}** · peers {r.get(key+'_peer',float('nan')):.1f} · week {week}")
        st.caption('Auto-generated summary');st.text(brief(r))
        with st.container(border=True):
            st.subheader(plan['action']);st.write(f"{plan['owner']} · due {plan['due_date']} · {plan['effort_hrs']} hours")
            st.write('Evidence: '+plan['evidence_to_inspect']);st.caption(plan['intended_result'])
            if st.button('Accept plan',type='primary'):
                try: actions.save(r);st.success('Plan saved, due '+plan['due_date']);st.cache_data.clear()
                except ValueError as e: st.error(str(e))
            with st.expander('Change or record another decision'):
                decision=st.selectbox('Decision',['changed','deferred','escalated','data_fix','visit','remote_review'])
                owner=st.text_input('Owner',value=plan['owner']);effort=st.number_input('Effort hours',min_value=0.,value=float(plan['effort_hrs']))
                due=st.date_input('Due date',value=date.fromisoformat(plan['due_date']))
                reason=st.text_input('Reason (required)',placeholder='Already handled / Waiting for dealer / Disagree with the data')
                if st.button('Save decision'):
                    try: actions.save(r,decision,reason,owner,effort,due);st.success('Decision saved');st.cache_data.clear()
                    except ValueError as e: st.error(str(e))
        with st.expander('Evidence'):
            table=[]
            for key,spec in cfg['indicators'].items(): table.append(dict(Indicator=spec['label'],Value=r.get(key),Peer=r.get(key+'_peer'),Risk=r.get(key+'_risk'),Contribution=r.get(key+'_contribution')))
            st.dataframe(pd.DataFrame(table),hide_index=True)
            raw=db.read('weekly');raw=raw[(raw.dealer_id==r['dealer_id'])&(raw.week<=week)].sort_values('week')
            if st.checkbox('Show trend and retail charts'):
                import altair as alt
                trend=indicators_all(cfg);trend=trend[(trend.dealer_id==r['dealer_id'])&trend.week.between(week-11,week)]
                chart=alt.Chart(trend[['week','index']]).mark_line(point=True).encode(x='week:Q',y=alt.Y('index:Q',scale=alt.Scale(domain=[0,100])))
                lines=alt.Chart(pd.DataFrame({'threshold':[35,60]})).mark_rule(strokeDash=[4,4]).encode(y='threshold:Q')
                st.altair_chart(chart+lines,use_container_width=True)
                st.line_chart(raw.set_index('week')[['retail_units','retail_target']].tail(16))
            st.dataframe(raw.tail(8),hide_index=True)
        with st.expander('Context check'):
            st.write(f"Raw score {number(r['raw_index'])} · adjusted score {number(r['adjusted_index'])}")
            if r['incomplete']: st.warning('Score incomplete; missing components are not reweighted')
            for note in r['adjustments']: st.write(note)
        with st.expander('Pattern flags'):
            for note in r['flags'].get('evidence',[]): st.write(note)
            if not r['flags'].get('evidence'): st.write('No pattern flags in the evaluated window')
        with st.expander('What we do not know yet'):
            st.write('Verify source records. Scheme timing, seasonality, customer financing cycles, disputes and local operating constraints may explain observed patterns. These metrics do not establish causation.')
        if has_uploads: st.caption('Transfer option unavailable after a weekly CSV upload; vehicle and demand data are still simulated.')
        elif week!=latest: st.caption('Transfer option is shown for the latest week only')
        else:
            candidates=transfer_candidates(r['dealer_id'],cfg,week)
            if candidates:
                with st.expander('Stock transfer option'):
                    v=candidates[0];st.write(f"{v['model']} {v['variant']} → {v['destination']} · route {v['route_days']} days")
                    st.caption(v['pending'])
                    cost=st.number_input('Vehicle cost INR',min_value=1.,value=float(v['cost']))
                    rate=st.number_input('Annual carrying rate %',min_value=.1,value=12.)/100
                    held=st.number_input('Days to sell if held',min_value=0,value=60)
                    moved=st.slider('Days to sell if moved (including transit)',v['route_days'],120,15)
                    transport=st.number_input('Transport and handling INR',min_value=0.,value=float(v['transport']))
                    economics=transfer_economics(cost,rate,held,moved,transport)
                    st.write(f"Carrying cost avoided ₹{economics['avoided']:,.0f} · Net scenario ₹{economics['net']:,.0f} · Break-even {economics['break_even_days']:.1f} days")
                    st.caption('Scenarios under stated assumptions, not savings. Financing counted until final sale; pending fees are not included.')

elif page=='My actions':
    st.title('My actions');saved=db.read('actions')
    if saved.empty: st.info('No actions saved yet. Open a dealer case to accept a plan.')
    for a in saved.to_dict('records'):
        current=s[s.dealer_id==a['dealer_id']]
        if current.empty: continue
        r=current.iloc[0];baseline=json.loads(a['baseline_json']);overdue=a['due_date']<str(week_end(week)) and a['status']=='open'
        with st.container(border=True):
            st.subheader(r['name']);st.write(a['playbook']);st.write(f"{a['owner']} · due {a['due_date']} · {a['status']} · {a['decision']}")
            if overdue: st.warning('Overdue action')
            st.write(actions.verdict(baseline['adjusted_index'],r.adjusted_index))
            st.write(f"Baseline score {number(baseline['adjusted_index'])} → {r.adjusted_index:.1f}; overdue {number(baseline['overdue'])} → {r.get('overdue',float('nan')):.1f}%; aged {number(baseline['aged'])} → {r.get('aged',float('nan')):.1f}%")
            if a['override_reason']: st.caption(a['override_reason'])
            if a['decision']=='deferred': st.caption('Returns on +5 adjusted points or an urgent rule; urgent cases stay visible')
            if st.button('Mark complete',key='complete'+str(a['id'])): db.execute("UPDATE actions SET status='complete' WHERE id=?",(a['id'],));refresh()
