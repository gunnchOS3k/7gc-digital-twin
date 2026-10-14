from pathlib import Path
import json,re,hashlib
E=Path(__file__).resolve().parents[1];report=[]
for c in json.loads((E/'CLAIMS.json').read_text()):
 p=E/c['file'];assert p.is_file(),c['file'];x=json.loads(p.read_text())
 if 'length' in c:assert len(x)==c['length']
 else:
  for part in c['pointer'].split('/')[1:]:x=x[int(part)] if isinstance(x,list) else x[part.replace('~1','/').replace('~0','~')]
  if 'tolerance' in c:assert abs(x-c['expected'])<c['tolerance']
  else:assert x==c['expected'],c['id']
 report.append({'id':c['id'],'file':c['file'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'PASS'})
s=json.loads((E/'reproduction/rq1_gary_flagship_profiles.json').read_text())['statistical_report']
primary=(E/'tables/owner_primary.tex').read_text();classes=(E/'tables/owner_class.tex').read_text()
for v in s['primary'].values():
 for k in ('mean','std','ci_low','ci_high'):assert f"{v[k]:.4f}" in primary
for v in s['per_class'].values():
 for a in v.values():
  for k in ('mean','ci_low','ci_high'):assert f"{a[k]:.3f}" in classes
assert 'Recorded seed' in (E/'figures/owner_seed_outcomes.svg').read_text()
assert 'Predeclared seed' not in (E/'figures/owner_seed_outcomes.svg').read_text()
(E/'generated').mkdir(exist_ok=True);(E/'generated/CLAIM_CHECK.json').write_text(json.dumps({'claims':report,'numeric_table_cells_match':True,'seed_axis_label_correct':True,'human_review':False},indent=2)+'\n')
print('PASS:',len(report),'claim assertions, numeric table cells and seed axis label')
