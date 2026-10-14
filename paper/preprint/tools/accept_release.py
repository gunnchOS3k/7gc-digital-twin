"""Read-only ZIP audit and clean extracted builds/reproduction; preserves release bytes."""
from pathlib import Path
import tempfile,zipfile,hashlib,subprocess,json,os,re,sys,shutil
P=Path(__file__).resolve().parents[1]/'v0.1';V=P/'verification';T=Path(tempfile.mkdtemp(prefix='paper-i-v01-acceptance-',dir='/private/tmp'));R=P.parents[2];py=sys.executable
record={'date':'2026-10-13','clean_directory':str(T),'preprint_source_sha':json.loads((P/'PROVENANCE.json').read_text())['preprint_source_sha'],'experimental_source_sha':'1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa','existing_dependencies_reused':True,'fresh_platform_installation':False,'commands':{},'archives':{},'human_scientific_approval':False,'publication_authorized':False}
def run(tag,cmd,cwd,env=None):
 x=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True);(V/(tag+'.txt')).write_text(x.stdout+x.stderr);record['commands'][tag]={'command':cmd,'cwd':str(cwd),'exit_code':x.returncode,'log':tag+'.txt'}
 assert x.returncode==0,(tag,(x.stdout+x.stderr)[-2000:]);return x
for kind in ['source','evidence']:
 z=P/f'paper-i-v0.1-{kind}.zip';d=T/kind;d.mkdir()
 with zipfile.ZipFile(z) as a:
  names=a.namelist();assert len(names)==len(set(names))
  expected={}
  for ln in a.read('SHA256SUMS').decode().splitlines():
   h,n=ln.split('  ',1);assert re.fullmatch(r'[0-9a-f]{64}',h) and n not in expected and not Path(n).is_absolute() and '..' not in Path(n).parts;expected[n]=h
   assert hashlib.sha256(a.read(n)).hexdigest()==h,n
  assert set(names)==set(expected)|{'SHA256SUMS'}
  for n in names:
   assert not Path(n).is_absolute() and '..' not in Path(n).parts;assert (a.getinfo(n).external_attr>>16)&0o170000!=0o120000
  a.extractall(d)
 record['archives'][kind]={'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'payload_count':len(expected),'every_member_checksum_valid':True,'exact_membership_valid':True,'manifest_covered_by_outer_zip_sha':True}
run('CLEAN_SOURCE_MANIFEST',[py,'VERIFY_MANIFEST.py'],T/'source')
env=os.environ.copy();env['PATH']='/Users/gunnchos/Library/TinyTeX/bin/universal-darwin:'+env['PATH']
run('CLEAN_SOURCE_BUILD',['sh','BUILD.sh'],T/'source',env)
log=(T/'source/preprint.log').read_text();assert not re.search(r'Overfull|undefined|LaTeX Error',log)
(T/'rendered').mkdir();run('CLEAN_RENDER',['pdftoppm','-scale-to','1700','-png',str(T/'source/preprint.pdf'),str(T/'rendered/page')],T)
old=list(sorted((V/'pages').glob('page-*.png')));new=list(sorted((T/'rendered').glob('page-*.png')));assert len(old)==len(new)==9
pairs=[]
for a,b in zip(old,new):
 h=hashlib.sha256(a.read_bytes()).hexdigest();assert h==hashlib.sha256(b.read_bytes()).hexdigest(),a.name;pairs.append({'page':a.name,'pixel_file_sha256':h,'identical':True})
record['clean_source_pdf_pages']=9;record['rendered_page_equality']=pairs;record['clean_build_pdf_sha256']=hashlib.sha256((T/'source/preprint.pdf').read_bytes()).hexdigest();record['accepted_release_pdf_sha256']=hashlib.sha256((P/'preprint.pdf').read_bytes()).hexdigest()
run('CLEAN_EVIDENCE_MANIFEST',[py,'scripts/verify_manifest.py'],T/'evidence')
# No accidental discovery of a containing Git checkout: frozen stamp must record unknown in this extraction.
x=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=T/'evidence/source',capture_output=True,text=True);assert x.returncode!=0
for script in ['reproduce.py','independent_audit.py','test_verifier.py','verify_claims.py','generate_figures.py']:
 e=env.copy();e['MPLCONFIGDIR']=str(T/'evidence/generated/.mpl-cache')
 run('CLEAN_'+script.removesuffix('.py').upper(),[py,'scripts/'+script],T/'evidence',e)
fresh=json.loads((T/'evidence/generated/current_verification.json').read_text())
assert fresh['scientific_payload_sha256']=='f8d15b0297088611b065f28ef2c65e1cb1aba86641adfd9da6ddb640e3c47772' and fresh['git_metadata_available']==False
assert all(v['producer']['commit']=='unknown' for k,v in fresh['fresh_provenance'].items() if k.endswith('/provenance'))
for n in ['current_verification.json','CLAIM_CHECK.json','verification/INDEPENDENT_SCIENTIFIC_AUDIT.json']:
 p=T/'evidence/generated'/n;dest=V/'clean_evidence'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
record['fresh_unknown_git_producer_explicitly_retained']=True;record['scientific_payload_sha256']=fresh['scientific_payload_sha256'];record['numerical_reproduction_pass']=True
# Figures can differ in SVG/PDF metadata, but accepted chart raster must match generated raster.
plot=[]
for a in (T/'evidence/figures').glob('*.png'):
 b=T/'evidence/generated/figures'/a.name;assert b.is_file() and hashlib.sha256(a.read_bytes()).hexdigest()==hashlib.sha256(b.read_bytes()).hexdigest(),a.name;plot.append(a.name)
record['fresh_raster_plots_equal']=plot
# Check claim links where evidence actually lives, including standalone extracted evidence documents.
link_results=[]
for base,files in [(P,[P/'CLAIM_TO_EVIDENCE.md',P/'CITATION_VERIFICATION.md']), (T/'evidence',[T/'evidence/CLAIM_TO_EVIDENCE.md',T/'evidence/CITATION_VERIFICATION.md'])]:
 for f in files:
  for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if target.startswith(('https:','http:','#')):continue
   assert (f.parent/target.split('#')[0]).is_file(),(f,target);link_results.append({'document':str(f.relative_to(base)),'target':target,'exists':True})
record['claim_and_citation_file_links']=link_results
# Confirm extracted source snapshot still equals Git bytes; no data changes were introduced by execution.
m=json.loads((T/'evidence/source/MANIFEST.json').read_text())
for n,h in m['sha256'].items():
 b=(T/'evidence/source'/n).read_bytes();g=subprocess.check_output(['git','show',record['experimental_source_sha']+':'+n],cwd=R);assert b==g and hashlib.sha256(b).hexdigest()==h,n
record['frozen_git_files_equal']=len(m['sha256'])
run('CLEAN_EVIDENCE_MANIFEST_AFTER_RUN',[py,'scripts/verify_manifest.py'],T/'evidence')
record['all_checks_passed']=True
(V/'CLEAN_EXTRACTION_ACCEPTANCE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'all_checks_passed':True,'source_payload_files':record['archives']['source']['payload_count'],'evidence_payload_files':record['archives']['evidence']['payload_count'],'pages':9,'raster_plots':plot,'scientific_payload_sha256':record['scientific_payload_sha256'],'frozen_git_files':len(m['sha256']),'directory':str(T)},indent=2))
