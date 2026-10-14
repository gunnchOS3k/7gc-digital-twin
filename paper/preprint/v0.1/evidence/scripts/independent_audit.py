"""Independent RQ1 reconstruction and mathematical audit; no frozen file mutations."""
from pathlib import Path
import json,random,statistics,hashlib,subprocess,sys
from collections import Counter
from scipy.stats import t
from scipy.integrate import quad
E=Path(__file__).resolve().parents[1];R=E/'source';P=E/'generated';(P/'verification').mkdir(parents=True,exist_ok=True)
raw=json.loads((E/'reproduction/rq1_gary_flagship_profiles.json').read_text());st=raw['statistical_report'];bundle=json.loads((R/'fixtures/device_os/SERVICE_CONTINUITY_PROFILES.json').read_text())
assert st['seeds']==list(range(1,31)) and st['steps_per_seed']==48 and st['paired_vs_baseline'] is None and st['effect_sizes'] is None
priors={'wearable':(.45,.55,1.35),'smartphone':(.72,.78,1.),'laptop':(.8,.85,.85),'edge_node':(.88,.9,.7)}
max_round=0.;identities=0;replayed=0
for seed in st['per_seed']:
 rng=random.Random(seed['seed']);C=[];U=[];unroundedC=[];unroundedU=[]
 for cls,(a,q,h) in priors.items():
  good=done=entries=0;out=False
  for _ in range(48):
   stress=rng.random();demand=1+49*rng.random();m=rng.random()<a*(1-.35*h*stress);y=m and rng.random()<q*(1-.2*stress)
   good+=int(m);done+=int(y);entries+=int(not m and not out);out=not m
  r=seed['per_class'][cls];c=round(done/48,6);u=round(good/48,6)
  assert (c,u,entries)==(r['task_completion_ratio'],r['time_above_minimum_useful'],r['recovery_event_count']);assert c<=u
  assert r['reliability']==u and r['outage_fraction']==r['qoe_violation_fraction']==r['packet_loss_proxy']
  assert abs(r['packet_loss_proxy']-(1-u))<=1.000001e-6
  assert abs(r['throughput_proxy_mbps']-5*good/48)<.000051
  assert abs(r['compute_completion_time_proxy']-48*(1.2-.4*done/48))<.000051
  identities+=6;replayed+=1;C.append(c);U.append(u);unroundedC.append(done/48);unroundedU.append(good/48)
 for k,vals,unrounded in [('task_completion_ratio',C,unroundedC),('time_above_minimum_useful',U,unroundedU)]:
  assert round(sum(vals)/4,6)==seed['primary'][k];max_round=max(max_round,abs(seed['primary'][k]-sum(unrounded)/4))
def check(a,ref):
 m=statistics.fmean(a);sd=statistics.stdev(a);half=float(t.ppf(.975,len(a)-1))*sd/len(a)**.5
 assert max(abs(m-ref['mean']),abs(sd-ref['std']),abs(m-half-ref['ci_low']),abs(m+half-ref['ci_high']))<1e-10
 return {'n':len(a),'mean':m,'sample_sd':sd,'ci95':[m-half,m+half]}
checks={k:check([s['primary'][k] for s in st['per_seed']],ref) for k,ref in st['primary'].items()}
class_checks={c:{k:check([s['per_class'][c][k] for s in st['per_seed']],v) for k,v in ref.items()} for c,ref in st['per_class'].items()}
expected={}
for c,(a,q,h) in priors.items():
 b=.35*h;u=a*(1-b/2);z=a*q*(1-(b+.2)/2+.2*b/3)
 assert abs(quad(lambda x:a*(1-b*x),0,1)[0]-u)<1e-12 and abs(quad(lambda x:a*q*(1-b*x)*(1-.2*x),0,1)[0]-z)<1e-12
 expected[c]={'useful':u,'completion':z,'completion_expectation_in_descriptive_ci':class_checks[c]['task_completion_ratio']['ci95'][0]<=z<=class_checks[c]['task_completion_ratio']['ci95'][1]}
counts=Counter();offline=Counter();matches=0;degraded_names=0
for cls,prof in bundle['profiles'].items():
 for s in prof['benchmark_scenarios']:
  state=s['orchestrator_state'];F=bool(s['offline_covers_workload']);label='target' if state=='connected' else 'degraded' if state in ['degraded','transitioning'] else 'min_useful' if state=='offline' and F else 'failed'
  assert s['continuity_level']==label;counts[label]+=1;matches+=1
  if state=='offline':offline[label]+=1
  if s['scenario_id']=='degraded_wifi':assert state=='connected' and label=='target';degraded_names+=1
assert dict(counts)=={'target':12,'min_useful':8,'failed':1} and matches==21 and degraded_names==4
# Explicit provenance semantics audit: these two recorded digest strings are compared by engine, not rehashed content.
fixture_prov=json.loads((R/'fixtures/device_os/PROVENANCE.json').read_text());assert hashlib.sha256((R/'fixtures/device_os/SERVICE_CONTINUITY_PROFILES.json').read_bytes()).hexdigest()==fixture_prov['file_sha256']
source='1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa';oldrecord=json.loads((E/'reproduction/current_verification.json').read_text())
for rel,h in oldrecord['source_sha256'].items():
 a=(R/rel).read_bytes();assert hashlib.sha256(a).hexdigest()==h and hashlib.sha256(a).hexdigest()==json.loads((R/'MANIFEST.json').read_text())['sha256'][rel]
report={'experimental_source_sha':source,'publication_source_sha':json.loads((E/'PROVENANCE.json').read_text())['preprint_source_sha'],'independent_replay_seed_class_rows':replayed,'seed_count':30,'steps_per_class':48,'primary':checks,'per_class':class_checks,'numerical_quadrature_and_closed_form':expected,'maximum_observed_primary_rounding_error':max_round,'secondary_identity_checks':identities,'corpus_counts':dict(counts),'offline_counts':dict(offline),'overlay_rows':len(raw['continuity_benchmark']['gary_overlay']),'paired_contrast_and_effect_size':'not applicable: no executed baseline; null fields preserved','fixture_file_sha256_valid':True,'content_digest_limit':'engine compares recorded identifiers; does not independently recompute bundle semantic digest','previous_verifier_source_hashes_valid':True,'historical_verification_record_sha256':hashlib.sha256((E/'reproduction/current_verification.json').read_bytes()).hexdigest(),'python':sys.version,'human_scientific_approval':False,'scope':'independent AI-assisted implementation/calculation audit; no external human peer review'}
(P/'verification/INDEPENDENT_SCIENTIFIC_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'replay_rows':replayed,'primary':checks,'corpus':dict(counts),'digest_semantics_qualified':True},indent=2))
