"""Assemble local v0.1 archives; never contacts a repository or publication service."""
from pathlib import Path
import json,hashlib,zipfile,argparse,subprocess
P=Path(__file__).resolve().parents[1]/'v0.1';E=P/'evidence';R=P.parents[2]
a=argparse.ArgumentParser();a.add_argument('--source-sha',required=True);args=a.parse_args()
subprocess.run(['git','cat-file','-e',args.source_sha+'^{commit}'],cwd=R,check=True)
for p in [P/'PROVENANCE.json',E/'PROVENANCE.json']:
 v=json.loads(p.read_text());v['preprint_source_sha']=args.source_sha;v['source_anchor_state']='Exact committed manuscript, figures, portable scripts and evidence source; final archive/acceptance checkpoint recorded separately outside archives to avoid self-reference.';v['archive_git_producer_validation']='Clean non-Git run retains unknown; frozen source bytes independently hash-verified.'
 p.write_text(json.dumps(v,indent=2)+'\n')
for p in (P/'metadata').glob('*.json'):
 v=json.loads(p.read_text());v['experimental_source_sha']='1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa';v['preprint_source_sha']=args.source_sha;p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
source=[P/'preprint.tex',P/'preprint.pdf',P/'references.bib',P/'BUILD.sh',P/'VERIFY_MANIFEST.py',P/'PROVENANCE.json',P/'SOFTWARE_LICENSE_NOTICE.txt']
source += sorted((P/'sections').glob('*.tex'))+ sorted((P/'tables').glob('*.tex'))+sorted((P/'figures').glob('*'))+sorted((P/'metadata').glob('*.json'))
source += [P/n for n in ['README.md','REPRODUCIBILITY.md','SCIENTIFIC_REVIEW.md','NOVELTY_ASSESSMENT.md','CITATION_VERIFICATION.md','CITED_IDENTITIES.json','CLAIM_TO_EVIDENCE.md','CLAIMS.json','CROSS_PAPER_CONTRIBUTIONS.md','DATA_DICTIONARY.md','SUPPLEMENTAL_METHODS.md','LIMITATIONS.md','PLAIN_LANGUAGE_SUMMARY.md','RIGHTS_AND_DECLARATIONS.md','POLICY_CHECK.md','OWNER_REVIEW_WORKSHEET.md','AI_USE_DISCLOSURE.md','AUTHOR_METADATA.json','VERIFIER_EXCLUSIONS.md','PROSPECTIVE_VALIDATION_SPEC.md']]
evidence=sorted(p for p in E.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and not {'generated','__pycache__','.venv'}.intersection(p.relative_to(E).parts))
assert len(source)==len(set(source));assert all(p.is_file() and not p.is_symlink() for p in source+evidence)
inventory={}
for kind,base,files in [('source',P,source),('evidence',E,evidence)]:
 files=sorted(files);manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(base))+'\n' for p in files);(base/'SHA256SUMS').write_text(manifest)
 z=P/f'paper-i-v0.1-{kind}.zip'
 with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
  for p in files+[base/'SHA256SUMS']:
   info=zipfile.ZipInfo(str(p.relative_to(base)),date_time=(2026,10,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;out.writestr(info,p.read_bytes())
 inventory[kind]={'path':z.name,'payload_count':len(files),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((base/'SHA256SUMS').read_bytes()).hexdigest(),'payload':[str(p.relative_to(base)) for p in files]}
(P/'verification/ARCHIVE_INVENTORY.json').write_text(json.dumps(inventory,indent=2)+'\n')
print(json.dumps({k:{a:b for a,b in v.items() if a!='payload'} for k,v in inventory.items()},indent=2))
