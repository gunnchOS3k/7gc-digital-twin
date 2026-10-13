#!/usr/bin/env python3
"""Sync canonical authoring into a self-contained local author-review package."""
from pathlib import Path
import shutil,hashlib,json
p=Path(__file__).resolve().parents[1];sub=p/'submission';sub.mkdir(exist_ok=True)
for name in ('manuscript.tex','bibliography.bib'):shutil.copy2(p/name,sub/name)
for folder in ('sections','tables','figures'):
 (sub/folder).mkdir(exist_ok=True)
 for f in (p/folder).iterdir():
  if f.is_file() and (folder=='sections' or f.name.startswith('owner_')):shutil.copy2(f,sub/folder/f.name)
for f in p.iterdir():
 if f.is_file() and (f.suffix in ('.cls','.bst','.sty','.tfm','.pfb','.map','.fd') or f.name in ('logo.png','notaglinelogo.png','bullet.png')):shutil.copy2(f,sub/f.name)
(sub/'official_template').mkdir(exist_ok=True);shutil.copy2(p/'official_template/access.tex',sub/'official_template/access.tex')
source={str(f.relative_to(sub)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sub.rglob('*') if f.is_file() and f.suffix in ('.tex','.bib','.cls','.bst','.pdf','.svg','.png') and f.name!='manuscript.pdf'}
(sub/'SOURCE_ASSET_SHA256.json').write_text(json.dumps(source,indent=2)+'\n')
print('Self-contained author-review package synchronized from canonical paper/.')
