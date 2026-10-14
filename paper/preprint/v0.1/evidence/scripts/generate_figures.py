from pathlib import Path
import json,numpy as np
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];FIG=R/'generated/figures';TAB=R/'generated/tables';FIG.mkdir(parents=True,exist_ok=True);TAB.mkdir(parents=True,exist_ok=True)
data=json.loads((R/'reproduction/rq1_gary_flagship_profiles.json').read_text());stats=data['statistical_report'];rows=data['continuity_benchmark']['scenario_rows']
audit=json.loads((R/'reproduction/statistical_audit.json').read_text())
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
ax.set(xlabel='Recorded seed',ylabel='Fraction',ylim=(.25,.75));ax.legend(frameon=False,fontsize=8)
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
