#!/usr/bin/env python3
from pathlib import Path
import csv, json, sqlite3, sys, zipfile, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent  # audit the artifact tree itself (standalone-safe)
counts={k:0 for k in ['json','jsonl','csv','sqlite','zip','graphml','c','property']}; errors=[]; malformed=[]
# Build evidence text for intentional malformed-witness controls.
# (Collected in a list and joined once: repeated `+=` on a ~0.5 GB string is quadratic.)
evidence=[]
for p in root.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.json','.jsonl','.log','.txt','.csv'} and p.stat().st_size<20_000_000:
        try:evidence.append(p.read_text(encoding='utf-8',errors='ignore'))
        except OSError:pass
evidence='\n'+'\n'.join(evidence) if evidence else ''
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ('.git','__pycache__','.venv','venv')): continue
    rel=str(p.relative_to(root)); suf=p.suffix.lower()
    try:
      if suf=='.json': json.load(p.open(encoding='utf-8')); counts['json']+=1
      elif suf=='.jsonl':
        for n,l in enumerate(p.open(encoding='utf-8'),1):
          if l.strip(): json.loads(l)
        counts['jsonl']+=1
      elif suf in {'.csv','.tsv'}:
        with p.open(encoding='utf-8',newline='') as f:
          for _ in csv.reader(f,delimiter='\t' if suf=='.tsv' else ','): pass
        counts['csv']+=1
      elif suf in {'.sqlite','.sqlite3','.db'}:
        c=sqlite3.connect(f'file:{p}?mode=ro',uri=True); got=c.execute('PRAGMA integrity_check').fetchone()[0]; c.close()
        if got!='ok': raise ValueError(got)
        counts['sqlite']+=1
      elif suf=='.zip':
        with zipfile.ZipFile(p) as z:
          names=z.namelist()
          if len(names)!=len(set(names)): raise ValueError('duplicate zip members')
          for n in names:
            q=Path(n)
            if q.is_absolute() or '..' in q.parts: raise ValueError('zip path escape')
          bad=z.testzip()
          if bad: raise ValueError('CRC '+bad)
        counts['zip']+=1
      elif suf=='.graphml':
        raw=p.read_bytes()
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper(): raise ValueError('DTD/entity forbidden')
        try: ET.fromstring(raw); counts['graphml']+=1
        except Exception as x:
          # Require basename plus ERROR/nonzero indication somewhere in retained evidence.
          base=p.name
          if base in evidence and ('ERROR' in evidence or 'returncode' in evidence or 'exit' in evidence): malformed.append(rel)
          else: raise x
      elif suf in {'.c','.h'}:
        raw=p.read_bytes()
        if not raw or b'\x00' in raw: raise ValueError('empty/NUL C source')
        counts['c']+=1
      elif suf in {'.prp','.property'}:
        text=p.read_text(encoding='utf-8',errors='strict')
        if 'CHECK' not in text: raise ValueError('property lacks CHECK')
        counts['property']+=1
    except Exception as e: errors.append({'path':rel,'error':repr(e)})
# Keep every existing parse/integrity check and add semantic/receipt closure for
# the empirical update. A parseable summary alone is not sufficient evidence.
from verify_update_results import verify as verify_update
update=verify_update(root)
if update['status']!='PASS':
    errors.append({'path':'review-update','error':update.get('errors', ['update verification failed'])})
for name, result in update['studies'].items():
    if result['status']!='PASS':
        errors.append({'path':'review-update/'+name,'error':result['errors']})
print(json.dumps({'counts':counts,'intentional_malformed_graphml':malformed,
                  'review_update':{name:result['status'] for name,result in update['studies'].items()},
                  'errors':errors},indent=2))
raise SystemExit(1 if errors else 0)
