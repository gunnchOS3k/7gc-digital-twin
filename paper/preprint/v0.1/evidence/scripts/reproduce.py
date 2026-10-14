#!/usr/bin/env python3
"""Compare scientific values exactly; validate and retain variable provenance separately."""
from pathlib import Path
from datetime import datetime
import copy,sys,json,hashlib,statistics,subprocess,re
from scipy.stats import t
SUB=Path(__file__).resolve().parents[1]
ROOT=SUB/'source'
SOURCE_SHA='1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa'
INPUTS=['src/seven_gc_twin/rq1_statistical_report.py','src/seven_gc_twin/continuity_benchmark.py','src/seven_gc_twin/stats.py','src/seven_gc_twin/experiment_manifest.py','src/seven_gc_twin/provenance.py','configs/experiments/rq1_gary_flagship_profiles.yaml','paper/artifacts/experiment_protocol.yaml','fixtures/device_os/SERVICE_CONTINUITY_PROFILES.json']
def digest(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def partition(payload):
 """Only root output paths/result hash and typed provenance volatility are excluded."""
 p=copy.deepcopy(payload);retained={};excluded=[]
 if p['result_sha256']!=digest({k:v for k,v in p.items() if k not in ('result_sha256','wrote','statistical_artifacts')}):raise ValueError('Invalid result_sha256')
 retained['/result_sha256']=p.pop('result_sha256');excluded.append('/result_sha256 (validated whole-result digest)')
 for k in ('wrote','statistical_artifacts'):
  if k in p:
   values=[p[k]] if k=='wrote' else list(p[k].values())
   if not values or not all(isinstance(v,str) and v.strip() for v in values):raise ValueError('Invalid output paths')
   retained['/'+k]=p.pop(k);excluded.append('/'+k+' (nonempty output locations)')
 def walk(x,path=''):
  if isinstance(x,dict):
   if 'provenance' in x:
    v=x['provenance'];key=path+'/provenance';retained[key]=copy.deepcopy(v)
    if v['content_sha256']!=digest({k:a for k,a in v.items() if k!='content_sha256'}):raise ValueError('Invalid provenance digest: '+key)
    producer=v['producer']
    if producer['repository']!='7gc-digital-twin':raise ValueError('Wrong producer repository')
    commit=producer['commit']
    if commit not in (SOURCE_SHA,'951a91e9927354d5fcb7009819ea7bb16902c718','6523d11066d963d922433607462e5f5cd066b9f8','unknown') and commit != json.loads((SUB/'PROVENANCE.json').read_text())['preprint_source_sha']:raise ValueError('Malformed producer revision')
    # Clean archives have no Git metadata: unknown is retained, never replaced with a fabricated producer SHA.
    when=datetime.fromisoformat(producer['generated_at'].replace('Z','+00:00'))
    if when.tzinfo is None:raise ValueError('Timestamp lacks timezone')
    del v['content_sha256'];del producer['commit'];del producer['generated_at']
   for k,v in x.items():walk(v,path+'/'+k)
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,path+'/'+str(i))
 # No blanket recursive hash exclusion: scientific content digests remain compared.
 walk(p)
 excluded.extend(k+'/producer/{commit,generated_at}; '+k+'/content_sha256 (validated)' for k in retained if k.endswith('/provenance'))
 return p,retained,excluded

def compare(old,fresh):
 a,ap,ae=partition(old);b,bp,be=partition(fresh)
 if a!=b:raise ValueError('Scientific payload mismatch')
 return {'scientific_payload_equal':True,'scientific_payload_sha256':digest(a),'historical_provenance':ap,'fresh_provenance':bp,'exclusions':sorted(set(ae+be)),'provenance_validated':True}

def main():
 sys.path.insert(0,str(ROOT/'src'))
 from seven_gc_twin.experiment_manifest import run_experiment
 source={}
 for rel in INPUTS:
  raw=(ROOT/rel).read_bytes()
  manifest=json.loads((ROOT/'MANIFEST.json').read_text())
  if manifest['experimental_source_sha']!=SOURCE_SHA or hashlib.sha256(raw).hexdigest()!=manifest['sha256'][rel]:raise ValueError(rel+' fails frozen snapshot hash')
  source[rel]=hashlib.sha256(raw).hexdigest()
 fresh=run_experiment('rq1_gary_flagship_profiles',out_dir=SUB/'generated/fresh_verifier_v2')
 old=json.loads((SUB/'reproduction/rq1_gary_flagship_profiles.json').read_text())
 record=compare(old,fresh);checks={};stats=fresh['statistical_report']
 for key,ref in stats['primary'].items():
  a=[x['primary'][key] for x in stats['per_seed']];m=statistics.mean(a);sd=statistics.stdev(a);h=t.ppf(.975,len(a)-1)*sd/len(a)**.5
  if max(abs(m-ref['mean']),abs(m-h-ref['ci_low']),abs(m+h-ref['ci_high']))>1e-10:raise ValueError('Statistic mismatch '+key)
  checks[key]={'n':len(a),'mean':m,'sample_sd':sd,'ci95':[m-h,m+h]}
 record.update(source_sha=SOURCE_SHA,publication_execution_sha=json.loads((SUB/'PROVENANCE.json').read_text())['preprint_source_sha'],git_metadata_available=False,frozen_source_bytes_equal=True,source_sha256=source,independent_seed_statistics=checks,python=sys.version,evidence_class='SYNTHETIC_SIM',human_validation=False)
 (SUB/'generated/current_verification.json').write_text(json.dumps(record,indent=2)+'\n')
 print('PASS: exact scientific payload equality; provenance digests/timestamps/producer commits separately validated and retained.')
if __name__=='__main__':main()
