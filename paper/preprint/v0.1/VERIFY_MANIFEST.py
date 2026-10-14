from pathlib import Path
import hashlib
r=Path(__file__).resolve().parent;listed=set()
for line in (r/'SHA256SUMS').read_text().splitlines():
 h,n=line.split('  ',1);p=r/n
 assert not p.is_symlink() and not Path(n).is_absolute() and '..' not in Path(n).parts and n not in listed
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n;listed.add(n)
actual={str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and p.suffix not in ('.aux','.log','.bbl','.blg','.out','.pdf') and '__pycache__' not in p.parts}
# Exported figure PDFs and the release PDF are payload, not LaTeX byproducts.
actual|={str(p.relative_to(r)) for p in r.rglob('*.pdf')}
assert actual==listed,'Unlisted or missing payload files'
print('PASS:',len(listed),'source payload files')
