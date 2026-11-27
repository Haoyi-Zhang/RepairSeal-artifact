#!/usr/bin/env python3
"""Collect and re-execute a fixed sample of published Angelix C patches.

Preparation reads only the pinned external archive.  Execution is a new native
campaign, not a replay of the published outcomes.  Source bytes are unchanged;
the missing standard atoi declaration is supplied by -include stdlib.h.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import hashlib
import io
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scalar_semantics as semantic

OUTER_SHA256 = '65814e170d5887074b04cbb0dee958f078b12e5da49671364a6f7f2a6f7f7c7e'
OUTER_BYTES = 1088378260
INNER = 'esemdata/CVC4/instrumented_IntroClass_0.5_4.zip'
FAMILIES = {'median': 3, 'smallest': 4}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True)+'\n')


def strict_patch(original: bytes, patch: bytes) -> bytes:
    """Apply unified diff with exact old positions, full context, no fuzz/offset."""
    src = original.decode('utf-8').splitlines(keepends=True)
    lines = patch.decode('utf-8').splitlines(keepends=True)
    if len(lines) < 3 or not lines[0].startswith('--- ') or not lines[1].startswith('+++ '):
        raise ValueError('not a single-file unified diff')
    out, cursor, i, hunks = [], 0, 2, 0
    while i < len(lines):
        m = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n?', lines[i])
        if not m:
            raise ValueError('invalid hunk header')
        pos = int(m[1])-1
        oldn = int(m[2]) if m[2] is not None else 1
        newn = int(m[4]) if m[4] is not None else 1
        if not cursor <= pos <= len(src):
            raise ValueError('hunk position')
        out.extend(src[cursor:pos]); cursor = pos; i += 1
        oldseen = newseen = 0
        while i < len(lines) and not lines[i].startswith('@@ '):
            l = lines[i]
            if l.startswith('\\ No newline'):
                raise ValueError('no-newline patch marker unsupported')
            if not l or l[0] not in ' +-':
                raise ValueError('invalid hunk line')
            if l[0] in ' -':
                if cursor >= len(src) or src[cursor] != l[1:]:
                    raise ValueError('exact old context mismatch')
                cursor += 1; oldseen += 1
            if l[0] in ' +':
                out.append(l[1:]); newseen += 1
            i += 1
        if (oldseen, newseen) != (oldn, newn):
            raise ValueError('hunk count mismatch')
        hunks += 1
    if not hunks:
        raise ValueError('no hunks')
    out.extend(src[cursor:])
    return ''.join(out).encode('utf-8')


def prepare(archive, root=HERE):
    archive = Path(archive)
    if archive.stat().st_size != OUTER_BYTES or file_sha(archive) != OUTER_SHA256:
        raise ValueError('external archive does not match pinned identity')
    if (root/'corpus.json').exists():
        raise FileExistsError('corpus already prepared; choose a fresh output directory')
    with zipfile.ZipFile(archive) as outer:
        raw = outer.read(INNER)
    inventory, candidates, subjects = [], {}, {}
    source_payloads = {}
    test_payloads = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as inner:
        names = inner.namelist()
        tests = []
        for family, arity in FAMILIES.items():
            refpath = family+'/tests/'+family+'.c'
            ref = inner.read(refpath); refhash = sha(ref); source_payloads[refhash] = ref
            for path in sorted(n for n in names if n.startswith(family+'/tests/') and n.endswith('.in')):
                inp, outp = inner.read(path), inner.read(path[:-3]+'.out')
                vals = [int(v) for v in inp.split()]
                if len(vals) != arity:
                    raise ValueError('unexpected supplied-test arity')
                # The retained oracle extracts the integer after the prompt.
                suffix = outp.decode().split('>')[-1]
                answer = re.sub(r'[^-?0-9]', '', suffix)
                if not re.fullmatch(r'-?\d+', answer):
                    raise ValueError('noninteger supplied expected output')
                tests.append({'family':family,'suite':path.split('/')[-2], 'name':path.split('/')[-1],
                              'input_values':vals,'source_input_member':path,'source_output_member':path[:-3]+'.out',
                              'input_sha256':sha(inp),'output_sha256':sha(outp),'expected_stdout':answer+'\n',
                              'reference_sha256':refhash,'reference_member':refpath})
                test_payloads[path] = inp; test_payloads[path[:-3]+'.out'] = outp
        for path in sorted(n for n in names if n.split('/')[0] in FAMILIES and '/src/' in n and n.endswith('.patch')):
            subject = path.split('/src/')[0]
            family = subject.split('/')[0]
            source_member = subject+'/src/'+family+'.c'
            original, patch = inner.read(source_member), inner.read(path)
            row = {'member':path,'subject':subject,'family':family,'original_member':source_member,
                   'original_sha256':sha(original),'patch_sha256':sha(patch)}
            try:
                candidate = strict_patch(original,patch)
                row['candidate_sha256'] = sha(candidate)
                row['status'] = 'exact-application'
                key = (sha(original),sha(candidate))
                if key not in candidates:
                    candidates[key] = {'subject':subject,'family':family,'original_member':source_member,
                                       'original_sha256':key[0],'candidate_sha256':key[1],
                                       'patch_sha256':sha(patch),'patch_member':path,'occurrences':[]}
                    source_payloads[key[0]] = original; source_payloads[key[1]] = candidate
                candidates[key]['occurrences'].append(path)
                subjects.setdefault(key[0], []).append(key)
            except (ValueError, UnicodeError) as exc:
                row['status'] = 'excluded-exact-application'; row['reason'] = str(exc)
            inventory.append(row)
        selected = []
        for original_id in sorted(subjects):
            keys = sorted(set(subjects[original_id]), key=lambda k:k[1])
            # Fixed before execution; no tests or outcome information is used.
            selected.extend(candidates[k] for k in keys[:2])
        selected.sort(key=lambda x:(x['family'],x['subject'],x['candidate_sha256']))
        for index, row in enumerate(selected):
            row['case_id'] = f'apr-{index:03d}'
            row['reference_sha256'] = next(t['reference_sha256'] for t in tests if t['family']==row['family'])
            row['source'] = 'IntroClass / Zenodo 1012686'
            row['repair_tool'] = 'Angelix (published patch inventory)'
            row['synthesis_configuration'] = 'not attributed per patch; retained src directories mix historical runs'
            (root/'patches').mkdir(parents=True,exist_ok=True)
            (root/'patches'/f"{row['patch_sha256']}.patch").write_bytes(inner.read(row['patch_member']))
            for member in [row['subject']+'/oracle_all', row['subject']+'/oracle_bb', row['subject']+'/oracle_wb']:
                if member in names:
                    target=root/'upstream-oracles'/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(inner.read(member))
        needed = {row[k] for row in selected for k in ['original_sha256','candidate_sha256','reference_sha256']}
        for ident in needed:
            target=root/'sources'/f'{ident}.c';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source_payloads[ident])
        for member, data in test_payloads.items():
            target=root/'tests-data'/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    protocol = {'schema':'repairseal-real-patches-v1','outer_archive_sha256':OUTER_SHA256,'outer_archive_bytes':OUTER_BYTES,
                'outer_md5':'8347801dc54761bbbf1a9f8dc156e3f2','inner_member':INNER,'inner_sha256':sha(raw),'inner_bytes':len(raw),
                'selection':'all exact-application src/*.patch in median and smallest; deduplicate (original SHA256, applied-candidate SHA256); first two candidate SHA256 values per original SHA256; order by family, subject, candidate hash',
                'outcome_blind_selection':True,'raw_patch_occurrences':len(inventory),'application_successes':sum(x['status']=='exact-application' for x in inventory),
                'unique_applied_candidates':len(candidates),'unique_originals':len(subjects),'selected':len(selected),
                'correct_scope':'entire explicitly enumerated finite input set only; no global correctness assertion',
                'test_policy':'all original blackbox and whitebox cases, unfiltered; exact candidate stdout against the published numeric Angelix oracle and exit code zero',
                'domain':{'median':{'values':[-2,-1,0,1,2],'arity':3},'smallest':{'values':[-1,0,1,2],'arity':4}},
                'domain_union_policy':'The exact finite declared set is the Cartesian grid union all given blackbox and whitebox input vectors, retained in points.json.',
                'guard':'R(x) iff original is undefined, has nonzero exit status, or original stdout differs from the numeric reference stdout; K is its complement where original and reference are defined',
                'labels':'nonexclusive O0/O1/O2; O1/O2 count defined wrong outputs only; primary precedence definedness, repair-region, preservation, correct; unresolved reference/compilation/profile/correspondence -> other',
                'repairs_were_not_regenerated':True,'patches_are_published_tool_outputs':True,
                'independence':'no human inter-annotator agreement claim; independent label reduction and native executions are reported separately'}
    dump(root/'protocol.json',protocol);dump(root/'inventory.json',inventory);dump(root/'corpus.json',selected);dump(root/'given-tests.json',tests)
    dump(root/'all-unique-candidates.json',list(candidates.values()))
    print(json.dumps({'prepared':len(selected),'protocol':protocol}))


def points_for(root):
    protocol=json.loads((root/'protocol.json').read_text());tests=json.loads((root/'given-tests.json').read_text())
    values=defaultdict(set)
    domain_values={}
    for family,decl in protocol['domain'].items():
        domain_values[family]=set(itertools.product(decl['values'],repeat=decl['arity']))
        values[family].update(domain_values[family])
    for t in tests:values[t['family']].add(tuple(t['input_values']))
    rows=[]
    for family in sorted(values):
        for i,val in enumerate(sorted(values[family])):
            rows.append({'point_id':f'{family}-{i:04d}','family':family,'values':list(val),'in_domain':val in domain_values[family],
                         'given_tests':[t['suite']+'/'+t['name'] for t in tests if t['family']==family and tuple(t['input_values'])==val]})
    return rows


def tool_identity(name):
    path=Path(shutil.which(name) or name).resolve()
    p=subprocess.run([str(path),'--version'],text=True,capture_output=True,check=True)
    return {'executable':str(path),'sha256':file_sha(path),'version':p.stdout,'stderr':p.stderr}


def native_run(exe, point, role, timeout=2):
    argv=[str(exe)] + ([] if role=='reference' else [str(v) for v in point['values']])
    stdin=(' '.join(map(str,point['values']))+'\n') if role=='reference' else ''
    env=dict(os.environ);env['LC_ALL']='C';env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=0'
    try:
        p=subprocess.run(argv,input=stdin,text=True,capture_output=True,timeout=timeout,env=env)
        row={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timeout':False}
    except subprocess.TimeoutExpired as exc:
        row={'returncode':None,'stdout':(exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout,bytes) else exc.stdout or '',
             'stderr':(exc.stderr or b'').decode(errors='replace') if isinstance(exc.stderr,bytes) else exc.stderr or '', 'timeout':True}
    row['stdout_sha256']=sha(row['stdout'].encode());row['stderr_sha256']=sha(row['stderr'].encode())
    return row


def execute(root=HERE, jobs=4, gcc='gcc', clang='clang'):
    corpus=json.loads((root/'corpus.json').read_text());points=points_for(root)
    results=root/'records'
    if results.exists():raise FileExistsError('execution records already exist; use a fresh directory')
    results.mkdir();dump(root/'points.json',points)
    tools={name:tool_identity(binary) for name,binary in [('gcc',gcc),('clang',clang)]}
    dump(results/'environment.json',{'python':sys.version,'platform':platform.platform(),'tools':tools,
                                  'flags':['-std=c99','-include','stdlib.h','-O0'],'ubsan_flags':['-fsanitize=undefined','-fno-sanitize-recover=all'],
                                  'argv_policy':'published instrumented candidate/original: argv decimal integers; teacher reference: stdin original format',
                                  'source_bytes_modified_for_native_build':False})
    source_info={}
    for case in corpus:
        for role in ['original','candidate','reference']:
            key=case[role+'_sha256'];source_info[key]={'family':case['family'],'role':'reference' if role=='reference' else 'instrumented'}
    compile_rows=[];admission=[];sem_rows=[]
    with tempfile.TemporaryDirectory(prefix='repairseal-apr-') as work:
        work=Path(work)
        def one_source(item):
            ident,info=item;source=root/'sources'/f'{ident}.c';related=[p for p in points if p['family']==info['family']]
            try:
                parsed=semantic.parse(source.read_bytes(),FAMILIES[info['family']]);admit={'source_sha256':ident,'status':'admitted'}
                semantic_rows=[dict(source_sha256=ident,point_id=p['point_id'],**semantic.evaluate(parsed,p['values'])) for p in related]
            except (semantic.Unsupported,UnicodeError) as exc:
                admit={'source_sha256':ident,'status':'unsupported','reason':str(exc)};semantic_rows=[]
            compiles=[];native=[]
            for compiler,t in tools.items():
                for mode in ['plain','ubsan']:
                    exe=work/(ident+'-'+compiler+'-'+mode)
                    flags=['-std=c99','-include','stdlib.h','-O0']+(['-fsanitize=undefined','-fno-sanitize-recover=all'] if mode=='ubsan' else [])
                    cmd=[t['executable'],*flags,str(source),'-o',str(exe)]
                    build=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
                    compiles.append({'source_sha256':ident,'compiler':compiler,'mode':mode,'argv':[compiler,*flags,'sources/'+ident+'.c','-o','<temporary-executable>'],
                                     'returncode':build.returncode,'stdout':build.stdout,'stderr':build.stderr.replace(str(root),'<study-root>'),
                                     'binary_sha256':file_sha(exe) if build.returncode==0 else None})
                    if build.returncode:continue
                    # Unsupported programs are still tested on the supplied inputs,
                    # but do not receive finite-domain acceptance labels.
                    for p in related if admit['status']=='admitted' else [p for p in related if p['given_tests']]:
                        native.append(dict(source_sha256=ident,point_id=p['point_id'],compiler=compiler,mode=mode,
                                           **native_run(exe,p,info['role'])))
            return admit,semantic_rows,compiles,native
        total=len(source_info)
        with (results/'native.jsonl').open('w') as nf,(results/'semantics.jsonl').open('w') as sf:
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                for done,f in enumerate(as_completed([pool.submit(one_source,item) for item in sorted(source_info.items())]),1):
                    a,s,c,n=f.result();admission.append(a);compile_rows.extend(c)
                    for row in s:sf.write(json.dumps(row,sort_keys=True)+'\n')
                    for row in n:nf.write(json.dumps(row,sort_keys=True)+'\n')
                    nf.flush();sf.flush()
                    if done%10==0 or done==total:print(json.dumps({'sources_done':done,'sources_total':total}),flush=True)
    dump(results/'admission.json',sorted(admission,key=lambda x:x['source_sha256']))
    dump(results/'compiles.json',sorted(compile_rows,key=lambda x:(x['source_sha256'],x['compiler'],x['mode'])))
    spec=importlib.util.spec_from_file_location('real_patch_verifier',HERE/'verify.py')
    verifier=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=verifier
    spec.loader.exec_module(verifier)
    result=verifier.verify(root,write=True)
    print(json.dumps(result))


def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='action',required=True)
    q=sp.add_parser('prepare');q.add_argument('--archive',required=True,type=Path);q.add_argument('--output',type=Path,default=HERE)
    q=sp.add_parser('run');q.add_argument('--root',type=Path,default=HERE);q.add_argument('--jobs',type=int,default=4);q.add_argument('--gcc',default='gcc');q.add_argument('--clang',default='clang')
    a=p.parse_args()
    if a.action=='prepare':prepare(a.archive,a.output)
    else:execute(a.root,a.jobs,a.gcc,a.clang)


if __name__=='__main__':main()
