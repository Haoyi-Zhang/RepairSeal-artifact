#!/usr/bin/env python3
"""Offline verification of the published-patch campaign from retained records.

No network, compiler, sanitizer, or external archive is needed.  Hash checks,
exact patch application, test coverage, source-interpretation replay, native
correspondence, witnesses, and every summary count are checked independently of
the collection loop.  This is not a claim of human inter-annotator agreement.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import scalar_semantics as semantic
from patch_study import strict_patch, file_sha, sha, dump, points_for, FAMILIES


def load_lines(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def compute(root):
    errors=[]
    corpus=json.loads((root/'corpus.json').read_text());tests=json.loads((root/'given-tests.json').read_text())
    protocol=json.loads((root/'protocol.json').read_text());inventory=json.loads((root/'inventory.json').read_text())
    unique=json.loads((root/'all-unique-candidates.json').read_text())
    inventory_keys={(r['original_sha256'],r['candidate_sha256']) for r in inventory if r['status']=='exact-application'}
    unique_keys={(r['original_sha256'],r['candidate_sha256']) for r in unique}
    if inventory_keys!=unique_keys or len(unique)!=len(unique_keys):errors.append('deduplication inventory differs')
    groups=defaultdict(set)
    for a,b in unique_keys:groups[a].add(b)
    chosen={(a,b) for a,bs in groups.items() for b in sorted(bs)[:2]}
    if chosen!={(r['original_sha256'],r['candidate_sha256']) for r in corpus} or len(chosen)!=len(corpus):errors.append('outcome-blind sample differs from frozen rule')
    expected_inventory={'raw_patch_occurrences':len(inventory),'application_successes':sum(r['status']=='exact-application' for r in inventory),
                        'unique_applied_candidates':len(unique_keys),'unique_originals':len(groups),'selected':len(corpus)}
    if any(protocol.get(k)!=v for k,v in expected_inventory.items()):errors.append('sampling protocol counts differ from inventory')
    for test in tests:
        inp=(root/'tests-data'/test['source_input_member']).read_bytes()
        out=(root/'tests-data'/test['source_output_member']).read_bytes()
        expected=re.sub(r'[^-?0-9]', '', out.decode().split('>')[-1])+'\n'
        if sha(inp)!=test['input_sha256'] or sha(out)!=test['output_sha256'] or [int(v) for v in inp.split()]!=test['input_values'] or expected!=test['expected_stdout']:
            errors.append('given test bytes/oracle mismatch '+test['source_input_member'])
    points=json.loads((root/'points.json').read_text());point_map={p['point_id']:p for p in points}
    if points!=points_for(root):errors.append('explicit points differ from declared grid plus complete supplied tests')
    sem_list=load_lines(root/'records/semantics.jsonl');native_list=load_lines(root/'records/native.jsonl')
    sem={(r['source_sha256'],r['point_id']):r for r in sem_list}
    native={(r['source_sha256'],r['point_id'],r['compiler'],r['mode']):r for r in native_list}
    if len(sem)!=len(sem_list):errors.append('duplicate semantic receipt key')
    if len(native)!=len(native_list):errors.append('duplicate native receipt key')
    admission={r['source_sha256']:r for r in json.loads((root/'records/admission.json').read_text())}
    compile_rows=json.loads((root/'records/compiles.json').read_text())
    builds={(r['source_sha256'],r['compiler'],r['mode']):r for r in compile_rows}
    for r in native_list:
        if sha(r['stdout'].encode())!=r['stdout_sha256'] or sha(r['stderr'].encode())!=r['stderr_sha256']:
            errors.append('native stream hash mismatch: '+r['source_sha256']+':'+r['point_id'])
            break
    source_families={c[k+'_sha256']:c['family'] for c in corpus for k in ['original','candidate','reference']}
    source_admission={};source_correspondence={};semantic_replay_count=0;native_defined_checks=0
    for ident,family in sorted(source_families.items()):
        raw=(root/'sources'/f'{ident}.c').read_bytes()
        if sha(raw)!=ident:errors.append('source hash mismatch '+ident)
        try:
            program=semantic.parse(raw,FAMILIES[family]);source_admission[ident]=True
            if admission[ident]['status']!='admitted':errors.append('admission replay mismatch '+ident)
        except (semantic.Unsupported,UnicodeError) as exc:
            source_admission[ident]=False;source_correspondence[ident]=False
            if admission[ident]['status']!='unsupported':errors.append('unsupported replay mismatch '+ident)
            continue
        matches=True
        for point in [p for p in points if p['family']==family]:
            expected=semantic.evaluate(program,point['values']);key=(ident,point['point_id']);retained=sem.get(key)
            if retained is None or any(retained.get(k)!=v for k,v in expected.items()):
                errors.append('semantic replay mismatch '+ident+':'+point['point_id']);matches=False;continue
            semantic_replay_count+=1
            for compiler in ['gcc','clang']:
                for mode in ['plain','ubsan']:
                    build=builds.get((ident,compiler,mode));receipt=native.get((ident,point['point_id'],compiler,mode))
                    if not build or build['returncode']!=0 or receipt is None:
                        matches=False;continue
                    if expected['defined']:
                        native_defined_checks+=1
                        if receipt['timeout'] or receipt['returncode']!=expected['returncode'] or receipt['stdout']!=expected['stdout'] or ('runtime error:' in receipt['stderr']):
                            matches=False
        source_correspondence[ident]=matches
    labels=[]
    for case in corpus:
        ids={role:case[role+'_sha256'] for role in ['original','candidate','reference']}
        patch=(root/'patches'/f"{case['patch_sha256']}.patch").read_bytes()
        if sha(patch)!=case['patch_sha256'] or sha(strict_patch((root/'sources'/f"{ids['original']}.c").read_bytes(),patch))!=ids['candidate']:
            errors.append('candidate patch replay mismatch '+case['case_id'])
        family=case['family'];case_points=[p for p in points if p['family']==family]
        pass_tests=True;test_failures=[];test_runs=0
        for test in [t for t in tests if t['family']==family]:
            point=next(p for p in case_points if p['values']==test['input_values'])
            ref_observation=sem.get((ids['reference'],point['point_id']))
            if not ref_observation or not ref_observation['defined'] or len(ref_observation['numeric_values'])!=1 or str(ref_observation['numeric_values'][0])+'\n'!=test['expected_stdout']:
                errors.append('teacher reference disagrees with supplied test '+test['source_input_member'])
            for compiler in ['gcc','clang']:
                row=native.get((ids['candidate'],point['point_id'],compiler,'plain'));test_runs+=1
                passed=bool(row and not row['timeout'] and row['returncode']==0 and row['stdout']==test['expected_stdout'])
                if not passed:pass_tests=False;test_failures.append({'test':test['suite']+'/'+test['name'],'compiler':compiler,'point_id':point['point_id']})
        reasons=[]
        for role,ident in ids.items():
            if not source_admission.get(ident):reasons.append(role+': unsupported source profile')
            elif not source_correspondence.get(ident):reasons.append(role+': native/semantic correspondence or compilation incomplete')
        bad=defaultdict(list);repair_count=preserve_count=0
        if not reasons:
            for point in case_points:
                pid=point['point_id'];o,c,r=(sem[(ids[x],pid)] for x in ['original','candidate','reference'])
                if not r['defined'] or len(r['numeric_values'])!=1:
                    reasons.append('reference undefined or non-scalar at '+pid);continue
                expected=str(r['numeric_values'][0])+'\n'
                R=(not o['defined'] or o['stdout']!=expected or o['returncode']!=0)
                repair_count+=R;preserve_count+=not R
                if not c['defined']:
                    bad['definedness'].append(pid)
                elif c['stdout']!=expected or c['returncode']!=0:
                    bad['repair-region' if R else 'preservation'].append(pid)
        categories=[k for k in ['definedness','repair-region','preservation'] if bad[k]]
        primary='other' if reasons else categories[0] if categories else 'correct'
        if primary in ['correct','other']:categories=[primary]
        witness={}
        for category in ['definedness','repair-region','preservation']:
            if bad[category]:
                pid=bad[category][0]
                witness[category]={'point_id':pid,'input_values':point_map[pid]['values'],
                                   'original_semantic':sem[(ids['original'],pid)],'candidate_semantic':sem[(ids['candidate'],pid)],
                                   'reference_semantic':sem[(ids['reference'],pid)],
                                   'native_receipt_keys':[[ids['candidate'],pid,c,m] for c in ['gcc','clang'] for m in ['plain','ubsan']]}
        labels.append({'case_id':case['case_id'],'family':family,'subject':case['subject'],'source':case['source'],'repair_tool':case['repair_tool'],
                       'primary':primary,'labels':categories,'reasons':reasons,'all_given_tests_pass':pass_tests,'given_test_compiler_checks':test_runs,
                       'given_test_failures':test_failures,'tests_pass_but_wrong':pass_tests and primary not in ['correct','other'],
                       'declared_points':len(case_points),'repair_points':repair_count,'preservation_points':preserve_count,
                       'violation_counts':{k:len(bad[k]) for k in ['definedness','repair-region','preservation']},'witnesses':witness})
    primary=Counter(x['primary'] for x in labels);all_labels=Counter(y for x in labels for y in x['labels'])
    passing=sum(x['all_given_tests_pass'] for x in labels);wrong=sum(x['tests_pass_but_wrong'] for x in labels)
    grouped=[]
    for family in sorted(FAMILIES):
        group=[x for x in labels if x['family']==family]
        grouped.append({'source':'IntroClass / Zenodo 1012686','repair_tool':'Angelix (published patch inventory)','family':family,'patches':len(group),
                        'primary_counts':dict(sorted(Counter(x['primary'] for x in group).items())),
                        'nonexclusive_counts':dict(sorted(Counter(y for x in group for y in x['labels']).items())),
                        'all_given_tests_pass':sum(x['all_given_tests_pass'] for x in group),'tests_pass_but_wrong':sum(x['tests_pass_but_wrong'] for x in group)})
    summary={'schema':'repairseal-real-patches-summary-v1','selected_patches':len(labels),'unique_original_sources':len(set(c['original_sha256'] for c in corpus)),
             'unique_candidate_sources':len(set(c['candidate_sha256'] for c in corpus)),'primary_counts':dict(sorted(primary.items())),
             'nonexclusive_counts':dict(sorted(all_labels.items())),'all_given_tests_pass':passing,'tests_pass_but_wrong':wrong,
             'tests_pass_but_wrong_fraction_all_selected':{'numerator':wrong,'denominator':len(labels)},
             'tests_pass_but_wrong_fraction_all_test_passing':{'numerator':wrong,'denominator':passing},'by_source_tool_family':grouped,
             'all_given_test_passing_primary_counts':dict(sorted(Counter(x['primary'] for x in labels if x['all_given_tests_pass']).items())),
             'sampling_counts':expected_inventory,
             'strict_application_exclusion_reasons':dict(sorted(Counter(r['reason'] for r in inventory if r['status']!='exact-application').items())),
             'compiled_artifacts':len(compile_rows),'successful_compilations':sum(r['returncode']==0 for r in compile_rows),
             'native_executions':len(native_list),'semantic_observations':len(sem_list),'semantic_replayed':semantic_replay_count,
             'defined_native_correspondence_checks':native_defined_checks,'source_admission_counts':dict(Counter(r['status'] for r in admission.values())),
             'source_correspondence_pass':sum(source_correspondence.values()),'source_correspondence_total':len(source_correspondence),
             'given_test_cases':dict(Counter(t['family'] for t in tests)),
             'finite_input_points':dict(Counter(p['family'] for p in points)),
             'review':{'kind':'rule-based labels with independent replay; human agreement not measured','human_annotators':0,'human_agreement':None},
             'boundaries':['finite grid plus every supplied blackbox and whitebox input only',
                           'candidate source bytes are exact applications of published diffs to published instrumented sources',
                           'the release contains historical patches from several synthesis configurations; configurations are not inferred from the enclosing directory name',
                           'definedness is established by the closed int32 interpreter; sanitizer silence alone is never a definedness proof',
                           'the inference is about this deterministic sample of published scalar patches, not all C repairs or a random population sample']}
    return {'summary':summary,'labels':labels,'errors':errors}


def verify(root: Path | None=None, write=False):
    root=Path(root) if root is not None else HERE
    result=compute(root)
    errors=result['errors']
    if write:
        dump(root/'labels.json',result['labels']);dump(root/'summary.json',result['summary'])
        rows=[]
        for path in sorted(root.rglob('*')):
            if path.is_file() and path.name not in {'hash-inventory.json','verification.json','run.log'} and '__pycache__' not in path.parts:
                rows.append({'path':str(path.relative_to(root)),'bytes':path.stat().st_size,'sha256':file_sha(path)})
        for name in ['test_real_patch_study.py','test_real_patches_independent_review.py']:
            path=root.parent.parent/'tests'/name
            if path.is_file():rows.append({'path':'../../tests/'+name,'bytes':path.stat().st_size,'sha256':file_sha(path)})
        dump(root/'hash-inventory.json',rows)
    else:
        if json.loads((root/'summary.json').read_text())!=result['summary']:errors.append('summary differs from recomputation')
        if json.loads((root/'labels.json').read_text())!=result['labels']:errors.append('labels/witnesses differ from recomputation')
        for row in json.loads((root/'hash-inventory.json').read_text()):
            rel=Path(row['path'])
            if rel.is_absolute() or ('..' in rel.parts and row['path'] not in {'../../tests/test_real_patch_study.py','../../tests/test_real_patches_independent_review.py'}):
                errors.append('invalid manifest path');continue
            p=root/row['path']
            if not p.is_file() or p.stat().st_size!=row['bytes'] or file_sha(p)!=row['sha256']:errors.append('hash inventory mismatch '+row['path'])
    response={'status':'PASS_REAL_PATCH_RECORDS' if not errors else 'FAIL_REAL_PATCH_RECORDS','errors':errors,'recomputed':result['summary']}
    if write:dump(root/'verification.json',response)
    return response


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=HERE);a=p.parse_args()
    r=verify(a.root);print(json.dumps(r,indent=2));raise SystemExit(bool(r['errors']))
