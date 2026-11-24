#!/usr/bin/env python3
"""Audit the delivered artifact's paths, bindings, licenses, and generated assets."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

ARTIFACT = Path(__file__).resolve().parent
ROOT = ARTIFACT.parent
# The manuscript is an optional sibling (paper/); the artifact must also audit cleanly alone.
HAS_PAPER = (ROOT / 'paper' / 'main.tex').is_file()
SCAN = ROOT if HAS_PAPER else ARTIFACT
SKIP_PARTS = {'evaluation-output', '.git', '.venv', 'venv'}
FONT_SUFFIXES = {'.ttf', '.otf', '.woff', '.woff2'}
CACHE_NAMES = {'__pycache__', '.pytest_cache', '.mypy_cache'}


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def add(rows, check, ok, detail, path=None):
    rows.append({'check':check,'status':'PASS' if ok else 'FAIL','detail':detail,
                 **({'path':str(path.relative_to(ROOT)) if path and path.is_relative_to(ROOT) else str(path)} if path else {})})


def audit():
    rows=[]
    # Claim ledger paths are executable review links, not decorative prose.
    ledger=ARTIFACT/'claim_evidence_ledger.csv'
    with ledger.open(newline='',encoding='utf-8') as f:
        for record in csv.DictReader(f):
            for raw in record['evidence'].split(';'):
                if raw.strip().startswith('../paper/') and not HAS_PAPER:
                    rows.append({'check':'claim-evidence-path','status':'SKIPPED',
                                 'detail':f"{record['claim_id']}: {raw.strip()} (paper companion absent)"})
                    continue
                path=(ARTIFACT/raw.strip()).resolve()
                add(rows,'claim-evidence-path',path.exists(),f"{record['claim_id']}: {raw.strip()}",path)
    # Dependency files must agree on shared packages.
    def req(path):
        result={}
        for line in path.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#'): continue
            name,version=line.split('==',1); result[name.lower()]=version
        return result
    main, evaluator=req(ARTIFACT/'requirements.txt'), req(ARTIFACT/'requirements-evaluator.txt')
    for name in sorted(set(main)&set(evaluator)):
        add(rows,'dependency-pin-agreement',main[name]==evaluator[name],
            f"{name}: requirements={main[name]}, evaluator={evaluator[name]}")
    # Distribution hygiene: only the delivered trees (artifact/, paper/, top-level README.md),
    # not sibling venvs or evaluator output folders placed next to them.
    delivered=[ARTIFACT, ROOT/'paper'] if HAS_PAPER else [ARTIFACT]
    tops=[ROOT/'README.md'] if HAS_PAPER and (ROOT/'README.md').exists() else []
    for path in [*tops, *(p for top in delivered for p in top.rglob('*'))]:
        if SKIP_PARTS & set(path.relative_to(SCAN).parts): continue
        if path.is_symlink(): add(rows,'no-symlink',False,'symbolic link is not allowed',path)
        if path.is_file() and path.suffix.lower() in FONT_SUFFIXES:
            add(rows,'no-font-binary',False,'font binary must not be distributed',path)
        if path.name in CACHE_NAMES or path.suffix in {'.pyc','.pyo'}:
            add(rows,'no-cache',False,'cache must not be distributed',path)
    if not any(r['check']=='no-font-binary' and r['status']=='FAIL' for r in rows):
        add(rows,'no-font-binary',True,'no font binaries found')
    if not any(r['check']=='no-cache' and r['status']=='FAIL' for r in rows):
        add(rows,'no-cache',True,'no Python/tool caches found')
    if not any(r['check']=='no-symlink' and r['status']=='FAIL' for r in rows):
        add(rows,'no-symlink',True,'no symbolic links found')
    # Required notices and entry points.
    for path in [ARTIFACT/'LICENSE', ARTIFACT/'THIRD_PARTY_NOTICES.md', ARTIFACT/'external_resources.csv',
                 ARTIFACT/'evaluate.sh', ARTIFACT/'expected-results.json',
                 ARTIFACT/'external-inputs.json']:
        add(rows,'required-delivery-file',path.is_file(),path.name,path)
    # Generated figure manifest is binding when present.
    manifest_path=ROOT/'paper/figure-manifest.json'
    if manifest_path.is_file():
        manifest=json.loads(manifest_path.read_text())
        for fig in manifest.get('figures',[]):
            source=ROOT/fig['source_figure']
            add(rows,'figure-source',source.is_file(),fig['source_figure'],source)
            if source.is_file(): add(rows,'figure-source-hash',sha(source)==fig['source_figure_sha256'],fig['source_figure'],source)
            gen=fig.get('generator',{})
            for item in [{'path':gen.get('script'),'sha256':gen.get('sha256')}, *gen.get('dependencies',[]), *gen.get('data_inputs',[])]:
                if not item.get('path'): continue
                path=ROOT/item['path']
                add(rows,'figure-binding-path',path.is_file(),item['path'],path)
                if path.is_file() and item.get('sha256'):
                    add(rows,'figure-binding-hash',sha(path)==item['sha256'],item['path'],path)
            add(rows,'figure-font-distribution',not gen.get('font_environment',{}).get('binaries_distributed',True),
                f"figure {fig.get('number')} does not require bundled font binaries")
    failures=[r for r in rows if r['status']=='FAIL']
    return {'schema':'repairseal-delivery-audit-v1','status':'PASS_DELIVERY_AUDIT' if not failures else 'FAIL_DELIVERY_AUDIT',
            'checks':len(rows),'failures':failures,'records':rows}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    result=audit(); a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n')
    print(json.dumps({'status':result['status'],'checks':result['checks'],'failures':len(result['failures']),'output':str(a.output)}))
    return 1 if result['failures'] else 0
if __name__=='__main__': raise SystemExit(main())
