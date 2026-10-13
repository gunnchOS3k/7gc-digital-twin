#!/usr/bin/env python3
"""Derived reporting only: never changes frozen protocols or simulator code."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import os

os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[2]/'results'/'matplotlib-cache'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'paper'
SUB = PAPER / 'submission'
FIG = PAPER / 'figures'
TAB = PAPER / 'tables'
SOURCE_SHA = '1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa'
for p in (SUB, FIG, TAB, SUB/'reproduction', SUB/'figures', SUB/'tables'):
    p.mkdir(parents=True, exist_ok=True)

data = json.loads((ROOT/'results/experiments/rq1_gary_flagship_profiles.json').read_text())
stats = data['statistical_report']
rows = data['continuity_benchmark']['scenario_rows']
assert stats['seeds'] == list(range(1, 31))
assert data['findings']['digest_match'] and data['findings']['level_rederive_all_match']
expected = json.loads(subprocess.check_output(['git','show',SOURCE_SHA+':paper/artifacts/rq1_statistical_report.json'],cwd=ROOT))
for field in ('per_seed','primary','secondary','per_class'):
    assert stats[field] == expected[field], f'reproduction mismatch: {field}'

audit = {'source_sha': SOURCE_SHA, 'status': 'OWNER_REVIEW_DRAFT', 'evidence_class':'SYNTHETIC_SIM',
         'seed_count':30, 'steps_per_seed':48, 'frozen_report_numerical_parity':True,
         'python':sys.version, 'platform':platform.platform(), 'primary_independent_scipy_check':{},
         'post_hoc_analytic_expectations':{}}
for metric in stats['primary']:
    series = np.array([r['primary'][metric] for r in stats['per_seed']])
    mean, sd = float(series.mean()), float(series.std(ddof=1))
    half = float(t.ppf(.975,29)*sd/np.sqrt(30))
    ref = stats['primary'][metric]
    assert abs(mean-ref['mean']) < 1e-12
    assert abs(mean-half-ref['ci_low']) < 1e-10
    assert abs(mean+half-ref['ci_high']) < 1e-10
    audit['primary_independent_scipy_check'][metric]={'mean':mean,'std':sd,'t_critical':float(t.ppf(.975,29)),'ci_low':mean-half,'ci_high':mean+half,'pass':True}
sys.path.insert(0,str(ROOT/'src'))
from seven_gc_twin.rq1_statistical_report import CLASS_BASE
for cls, prior in CLASS_BASE.items():
    a, q, b = prior['min_useful_base'], prior['task_base'], .35*prior['stress_sens']
    audit['post_hoc_analytic_expectations'][cls]={'time_above_minimum_useful':a*(1-b/2), 'task_completion_ratio':a*q*(1-(b+.2)/2+.2*b/3)}
audit['post_hoc_semantic_comparator']={'description':'classify all offline snapshots as failed; no policy execution', 'offline_supported_rows':sum(r['orchestrator_state']=='offline' and r['offline_covers_workload'] for r in rows), 'offline_unsupported_rows':sum(r['orchestrator_state']=='offline' and not r['offline_covers_workload'] for r in rows)}
audit['metric_semantics']={'recovery_event_count':'outage-entry count; does not count completed recoveries', 'secondary_duplicates':['reliability = time_above_minimum_useful','outage_fraction = qoe_violation_fraction = packet_loss_proxy = 1 - time_above_minimum_useful'], 'proxies':['throughput_proxy_mbps = 5*time_above_minimum_useful','compute_completion_time_proxy = steps*(1.2 - 0.4*task_completion_ratio)']}
(SUB/'reproduction/statistical_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
for name in ('rq1_gary_flagship_profiles.json','rq1_statistical_report.json','rq1_statistical_report.csv','rq1_statistical_report.md'):
    shutil.copy2(ROOT/'results/experiments'/name,SUB/'reproduction'/name)
shutil.copy2(ROOT/'results/reproduce/REPRODUCE_RECORD.json',SUB/'reproduction/REPRODUCE_RECORD.json')

def tex_table(name, caption, label, header, body, cols):
    content='\\begin{table}[t]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\small\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(x+' \\\\' for x in body)+'\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    (TAB/name).write_text(content)

tex_table('owner_primary.tex','Frozen seeded timeline outcomes; 95\\% Student-$t$ intervals over 30 seed means.','tab:primary','Outcome & Mean & SD & 95\\% CI',[
    ('Completion $C$' if k=='task_completion_ratio' else 'Useful time $\\tau$')+f" & {v['mean']:.4f} & {v['std']:.4f} & [{v['ci_low']:.4f}, {v['ci_high']:.4f}]" for k,v in stats['primary'].items()], 'lrrl')
body=[]
for cls,p in stats['per_class'].items():
    c,u=p['task_completion_ratio'],p['time_above_minimum_useful']
    body.append(cls.replace('_','\\_')+f" & {c['mean']:.3f} & [{c['ci_low']:.3f}, {c['ci_high']:.3f}] & {u['mean']:.3f} & [{u['ci_low']:.3f}, {u['ci_high']:.3f}]")
tex_table('owner_class.tex','Timeline classes have synthetic resilience priors; intervals describe the generator, not measured hardware.','tab:classes','Class & $C$ & 95\\% CI & $\\tau$ & 95\\% CI',body,'lrlrl')
profiles=data['continuity_benchmark']['level_counts_by_class']
body=[c.replace('-','/').replace('_','\\_')+f" & {x.get('target',0)} & {x.get('degraded',0)} & {x.get('min_useful',0)} & {x.get('failed',0)}" for c,x in profiles.items()]
tex_table('owner_fixture.tex','Exhaustive counts in the 21 stored profile snapshots. No degraded or transitioning state is exercised.','tab:fixture','Profile & Target & Degraded & Useful & Failed',body,'lrrrr')

plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
classes=list(profiles)
scenarios=['wifi_nominal','dock_ethernet','degraded_wifi','jam_wifi_offline_fallback','force_offline','force_offline_coding_unsupported']
lookup={(r['research_class'],r['scenario_id']):r for r in rows}
mapping={'failed':0,'min_useful':1,'degraded':2,'target':3}
matrix=np.full((4,6),np.nan)
for i,cls in enumerate(classes):
    for j,scene in enumerate(scenarios):
        if (cls,scene) in lookup: matrix[i,j]=mapping[lookup[cls,scene]['continuity_level_derived']]
fig,ax=plt.subplots(figsize=(7.2,2.9),layout='constrained')
from matplotlib.colors import ListedColormap, BoundaryNorm
cmap=ListedColormap(['#b84343','#ecd9a0','#94a9c1','#317b85']);cmap.set_bad('#f3f4f6')
ax.imshow(matrix,cmap=cmap,norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5],4),aspect='auto')
ax.set_xticks(range(6),['Wi-Fi\nnominal','Dock\nlabel','Degraded\nWi-Fi label','Jam /\noffline','Forced\noffline','Unsupported\ncoding'])
ax.set_yticks(range(4),['Desk','Mobile/docked','Local creation','Wearable'])
for i in range(4):
    for j in range(6):
        value=matrix[i,j]; txt='Absent' if np.isnan(value) else ['Failed','Min. useful','Degraded','Target'][int(value)]
        ax.text(j,i,txt,ha='center',va='center',fontsize=8,color='white' if value in (0,3) else '#202731')
ax.tick_params(length=0)
for ext in ('pdf','svg','png'): fig.savefig(FIG/f'owner_fixture_matrix.{ext}',dpi=300)
plt.close(fig)

fig,ax=plt.subplots(figsize=(3.5,2.8),layout='constrained')
x=np.arange(30)
for k,color,label,offset in [('task_completion_ratio','#246b81','Completion',-.12),('time_above_minimum_useful','#a56527','Useful time',.12)]:
    vals=np.array([r['primary'][k] for r in stats['per_seed']]);ax.plot(x+1+offset,vals,'o',ms=3,color=color,label=label)
    v=stats['primary'][k];ax.axhline(v['mean'],color=color,lw=.8);ax.axhspan(v['ci_low'],v['ci_high'],color=color,alpha=.12)
ax.set(xlabel='Predeclared seed',ylabel='Fraction',ylim=(.25,.75));ax.legend(frameon=False,fontsize=8)
for ext in ('pdf','svg','png'):fig.savefig(FIG/f'owner_seed_outcomes.{ext}',dpi=300)
plt.close(fig)

fig,ax=plt.subplots(figsize=(3.5,2.8),layout='constrained')
names=list(stats['per_class']);xx=np.arange(4)
for k,color,label,offset in [('task_completion_ratio','#246b81','Completion',-.12),('time_above_minimum_useful','#a56527','Useful time',.12)]:
    ss=[stats['per_class'][c][k] for c in names];mu=np.array([r['mean'] for r in ss]);err=np.array([[r['mean']-r['ci_low'] for r in ss],[r['ci_high']-r['mean'] for r in ss]])
    ax.errorbar(xx+offset,mu,yerr=err,fmt='o',ms=4,capsize=3,color=color,label=label)
    expected_mu=[audit['post_hoc_analytic_expectations'][c][k] for c in names];ax.plot(xx+offset,expected_mu,'x',color=color,ms=7)
ax.set_xticks(xx,['Wearable','Phone','Laptop','Edge node']);ax.set(ylabel='Fraction',ylim=(0,.9));ax.legend(frameon=False,fontsize=8)
for ext in ('pdf','svg','png'):fig.savefig(FIG/f'owner_class_outcomes.{ext}',dpi=300)
plt.close(fig)
for p in FIG.glob('owner_*'):shutil.copy2(p,SUB/'figures'/p.name)
for p in TAB.glob('owner_*'):shutil.copy2(p,SUB/'tables'/p.name)
shutil.copy2(__file__,SUB/'figures/build_owner_review.py')
sha_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'configs/experiments/rq1_gary_flagship_profiles.yaml',PAPER/'artifacts/experiment_protocol.yaml',ROOT/'fixtures/device_os/SERVICE_CONTINUITY_PROFILES.json',ROOT/'src/seven_gc_twin/rq1_statistical_report.py',ROOT/'src/seven_gc_twin/continuity_benchmark.py',ROOT/'src/seven_gc_twin/stats.py',*FIG.glob('owner_*.pdf')]}
(SUB/'reproduction/input_output_sha256.json').write_text(json.dumps(sha_files,indent=2)+'\n')
(SUB/'reproduction/requirements-lock.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
print(json.dumps({'parity':'PASS','ci_scipy':'PASS','snapshots':len(rows),'figures':3,'source_sha':SOURCE_SHA},indent=2))
