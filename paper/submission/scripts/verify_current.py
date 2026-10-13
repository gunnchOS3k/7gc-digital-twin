#!/usr/bin/env python3
"""Fresh RQ1 verification; write only derived author-review artifacts."""
from pathlib import Path
import sys,json,hashlib,statistics,subprocess
from scipy.stats import t
root=Path(__file__).resolve().parents[3];sub=root/'paper/submission'
sys.path.insert(0,str(root/'src'))
from seven_gc_twin.experiment_manifest import run_experiment
sha='1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa'
inputs=['src/seven_gc_twin/rq1_statistical_report.py','src/seven_gc_twin/continuity_benchmark.py','src/seven_gc_twin/stats.py','src/seven_gc_twin/experiment_manifest.py','configs/experiments/rq1_gary_flagship_profiles.yaml','paper/artifacts/experiment_protocol.yaml','fixtures/device_os/SERVICE_CONTINUITY_PROFILES.json']
source={}
for rel in inputs:
 raw=subprocess.check_output(['git','show',sha+':'+rel],cwd=root);current=(root/rel).read_bytes();assert raw==current,rel+' changed from experimental source';source[rel]=hashlib.sha256(raw).hexdigest()
fresh=run_experiment('rq1_gary_flagship_profiles',out_dir=sub/'reproduction/fresh_2026-10-13')
old=json.loads((sub/'reproduction/rq1_gary_flagship_profiles.json').read_text())
for x in (old,fresh):
 for k in ('wrote','statistical_artifacts'):x.pop(k,None)
assert old==fresh,'Frozen RQ1 payload mismatch'
checks={};stats=fresh['statistical_report']
for key in stats['primary']:
 a=[x['primary'][key] for x in stats['per_seed']];m=statistics.mean(a);sd=statistics.stdev(a);h=t.ppf(.975,len(a)-1)*sd/len(a)**.5
 ref=stats['primary'][key];assert abs(m-ref['mean'])<1e-12;assert abs(m-h-ref['ci_low'])<1e-10;assert abs(m+h-ref['ci_high'])<1e-10
 checks[key]={'n':len(a),'mean':m,'sample_sd':sd,'ci95':[m-h,m+h]}
record={'source_sha':sha,'frozen_source_bytes_equal':True,'source_sha256':source,'fresh_complete_payload_equal':True,'excluded_output_path_keys':['wrote','statistical_artifacts'],'independent_seed_statistics':checks,'python':sys.version,'evidence_class':'SYNTHETIC_SIM','human_validation':False}
(sub/'reproduction/current_verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
