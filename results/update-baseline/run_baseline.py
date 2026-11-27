#!/usr/bin/env python3
"""Record the unchanged evaluator gates on an isolated companion-paper copy.

Use --artifact to name a disposable, complete project copy. The evaluator has no
--paper-dir option and paper/core rebuild paper files, so never point this runner
at the delivery tree. The original paper/ bytes are checked separately.
"""
import argparse, datetime, hashlib, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--artifact', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--label', required=True)
    a=ap.parse_args()
    source=a.artifact.resolve(); out=a.output.resolve()
    if source == Path(__file__).resolve().parents[2]:
        raise SystemExit('Use a disposable project copy; core/paper rebuild the companion manuscript.')
    if out.exists(): raise SystemExit('output must be new')
    out.mkdir(parents=True)
    env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONHASHSEED':'0'}
    commands=[(mode, ['sh','evaluate.sh',mode,'--output',str(out/mode)]) for mode in ('preflight','smoke')]
    commands += [('verify', [sys.executable,'-B','verify_expected_results.py','--output',str(out/'verify')])]
    commands += [(mode, ['sh','evaluate.sh',mode,'--output',str(out/mode)]) for mode in ('core','paper')]
    commands += [('audit-data-integrity',[sys.executable,'-B','audit_data_integrity.py'])]
    record={'schema':'repairseal-update-baseline-v1','label':a.label,'artifact':str(source),'python':sys.version,'platform':platform.platform(),'steps':[]}
    for name,cmd in commands:
        started=time.time()
        with (out/(name+'.stdout.log')).open('wb') as stdout, (out/(name+'.stderr.log')).open('wb') as stderr:
            c=subprocess.run(cmd,cwd=source,env=env,stdout=stdout,stderr=stderr)
        row={'name':name,'command':cmd,'cwd':str(source),'started_utc':datetime.datetime.fromtimestamp(started,datetime.timezone.utc).isoformat(),'elapsed_seconds':time.time()-started,'returncode':c.returncode,'stdout':name+'.stdout.log','stderr':name+'.stderr.log'}
        record['steps'].append(row)
        (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(row),flush=True)
    return int(any(row['returncode'] for row in record['steps']))

if __name__ == '__main__': raise SystemExit(main())
