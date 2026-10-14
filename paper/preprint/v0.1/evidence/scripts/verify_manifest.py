from pathlib import Path
import hashlib
r=Path(__file__).resolve().parents[1];listed=set()
for line in (r/'SHA256SUMS').read_text().splitlines():
 h,n=line.split('  ',1);p=r/n
 assert not p.is_symlink() and not Path(n).is_absolute() and '..' not in Path(n).parts
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n;listed.add(n)
actual={str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and not {'generated','__pycache__','.venv'}.intersection(p.relative_to(r).parts)}
assert actual==listed,'Unlisted or missing files'
print('PASS:',len(listed),'payload files')
