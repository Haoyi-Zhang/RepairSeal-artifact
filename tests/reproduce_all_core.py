"""One-command clean reproduction of baseline, proof-DAG, and archive-audit evidence."""
from __future__ import annotations
import argparse, copy, json, math, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from scientific_driver import require_assertions, new_output_directory

ROOT=Path(__file__).resolve().parents[1]

def run(command, timeout=240):
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('child timeout must be finite and positive')
    completed=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=timeout,check=False,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT/'src')+os.pathsep+str(ROOT/'tests')})
    if completed.returncode:
        raise RuntimeError('command failed: '+' '.join(map(str,command))+'\n'+completed.stdout+'\n'+completed.stderr)
    return completed.stdout

def scientific_summary(obj):
    """Project only documented measurement paths in known record schemas."""
    volatile = {
        'structured-study-v2': (
            ('generated_at_utc',), ('peak_rss_kib',), ('timing_ms',)),
        'edge-case-regression-v1': (('left_deep_ast', 'isolated_wall_seconds'),),
        'disk-replay-audit-v1': (('peak_rss_kib',), ('wall_seconds',)),
        'holdout-differential-v3': (('peak_rss_kib',), ('wall_seconds',)),
    }
    result = copy.deepcopy(obj)
    for path in volatile.get(result.get('schema'), ()):
        current = result
        for key in path[:-1]:
            if not isinstance(current, dict) or key not in current:
                break
            current = current[key]
        else:
            if isinstance(current, dict):
                current.pop(path[-1], None)
    return result

def compare_exact(expected, current, label):
    # Python equality aliases True/1 and 0/0.0. Receipt evidence preserves
    # JSON types, including counts and diagnostic coordinates.
    if json.dumps(expected, sort_keys=True, allow_nan=False) != json.dumps(current, sort_keys=True, allow_nan=False):
        raise AssertionError(label + ': scientific evidence differs')

def compare_summary(expected, current, label):
    compare_exact(scientific_summary(expected), scientific_summary(current), label)

def reduced_cases(path):
    rows=json.loads(path.read_text())
    keep=('id','case','variant','status','witness','nodes','points','certificate_bytes')
    return [{k:r.get(k) for k in keep if k in r} for r in rows]

def compare_security_evidence(retained, current):
    """Keep the security receipt strict except for one historical diagnostic.

    The v2 malformed-JSON control used to report ``JSON syntax``. The receiver
    now maps decoder exceptions to ``JSON decoding``; explicit duplicate-key
    and non-finite-number diagnostics still propagate unchanged. Project only
    that exact retained row, without rewriting either on-disk report.
    """
    expected = copy.deepcopy(retained)
    historical = {"case": "malformed-json", "status": "REJECTED", "reason": "JSON syntax"}
    if expected.get("schema") == "proof-dag-security-regression-v2":
        rows = expected.get("json_text_rejections", [])
        matches = [row for row in rows if row == historical]
        if len(matches) == 1:
            matches[0]["reason"] = "JSON decoding"
    # Canonical JSON also distinguishes Boolean/integer and integer/float
    # receipt fields; plain Python equality does not.
    if json.dumps(expected, sort_keys=True, allow_nan=False) != json.dumps(current, sort_keys=True, allow_nan=False):
        raise AssertionError("security regression differs beyond the historical JSON diagnostic label")

def main():
    require_assertions()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--child-timeout',type=float,default=240,
                        help='finite positive wall limit for each scientific child')
    args=parser.parse_args()
    if not math.isfinite(args.child_timeout) or args.child_timeout <= 0:
        parser.error('child-timeout must be finite and positive')
    out=args.output.resolve()
    out = new_output_directory(out); started=time.monotonic()
    run([sys.executable,str(ROOT/'tests'/'test_boundary_selection.py')],args.child_timeout)
    baseline=out/'baseline'; structured=out/'structured'; holdout=out/'holdout-differential'
    # The three independent scientific campaigns run concurrently.  This uses at
    # most three local Python workers, stays below the documented four-core
    # budget, and avoids treating wall-clock serialization as scientific work.
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'reproduce.py'),'--output',str(baseline)],args.child_timeout),
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'structured_study.py'),'--output',str(structured)],args.child_timeout),
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'holdout_differential.py'),'--output',str(holdout),'--cases','400'],args.child_timeout),
        ]
        for future in futures:
            future.result()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'proof_dag_security.py'),'--output',str(structured/'security-regression.json')],args.child_timeout),
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'public_archive_audit.py'),'--output',str(structured/'codeflaws-archive-audit.json')],args.child_timeout),
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'edge_case_regression.py'),'--output',str(structured/'edge-case-regression.json')],args.child_timeout),
        ]
        for future in futures:
            future.result()
    # These gates consume requests from disk.  Authoritative coordinate order is
    # recovered from the deterministic fixture/stress generators and grammar
    # seeds, never from a certificate field.
    retained=ROOT/'proof-data'
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'disk_replay.py'),
                             '--proof-data',str(structured),'--grammar-data',str(holdout),
                             '--output',str(structured/'disk-replay-audit.json')],args.child_timeout),
            pool.submit(run,[sys.executable,str(ROOT/'tests'/'disk_replay.py'),
                             '--proof-data',str(retained),
                             '--output',str(out/'retained-disk-replay-audit.json')],args.child_timeout),
        ]
        for future in futures:
            future.result()
    base_status=json.loads((baseline/'reproduction.json').read_text()); assert base_status['outcome']=='PASS_CLEAN_REPRODUCTION'
    baseline_study=json.loads((baseline/'study.json').read_text())
    study=json.loads((structured/'structured-study.json').read_text())
    audit=json.loads((structured/'codeflaws-archive-audit.json').read_text())
    security=json.loads((structured/'security-regression.json').read_text())
    edge=json.loads((structured/'edge-case-regression.json').read_text())
    disk_audit=json.loads((structured/'disk-replay-audit.json').read_text())
    retained_disk_audit=json.loads((out/'retained-disk-replay-audit.json').read_text())
    holdout_summary=json.loads((holdout/'summary.json').read_text())
    compare_summary(json.loads((retained/'structured-study.json').read_text()), study, 'structured study')
    compare_exact(reduced_cases(retained/'fixture-cases.json'), reduced_cases(structured/'fixture-cases.json'), 'fixture cases')
    compare_exact(reduced_cases(retained/'stress-cases.json'), reduced_cases(structured/'stress-cases.json'), 'stress cases')
    compare_exact(json.loads((retained/'codeflaws-archive-audit.json').read_text()), audit, 'archive audit')
    compare_security_evidence(json.loads((retained/'security-regression.json').read_text()), security)
    compare_summary(json.loads((retained/'edge-case-regression.json').read_text()), edge, 'edge cases')
    compare_summary(json.loads((retained/'disk-replay-audit.json').read_text()), disk_audit, 'disk replay')
    compare_summary(retained_disk_audit, disk_audit, 'retained disk replay')
    retained_holdout=retained/'holdout-differential'
    compare_summary(json.loads((retained_holdout/'summary.json').read_text()), holdout_summary, 'grammar holdout')
    assert (holdout/'cases.json').read_bytes()==(retained_holdout/'cases.json').read_bytes()
    assert sorted(p.name for p in (holdout/'inputs').iterdir())==sorted(p.name for p in (retained_holdout/'inputs').iterdir())
    for path in (retained_holdout/'inputs').iterdir():
        assert path.read_bytes()==(holdout/'inputs'/path.name).read_bytes(),path.name
    compared=0
    for dirname in ('fixture-inputs','fixture-certificates','stress-certificates','stress-inputs','controls','refutation-witnesses','refutation-controls'):
        before=retained/dirname; after=structured/dirname
        assert sorted(p.name for p in before.iterdir())==sorted(p.name for p in after.iterdir())
        for path in before.iterdir():
            assert path.read_bytes()==(after/path.name).read_bytes(),path.name; compared+=1
    result={'outcome':'PASS_COMPLETE_REPRODUCTION','baseline_compared_files':base_status['compared_files'],'proof_dag_byte_compared_files':compared,
            'structured_requests':study['total_requests'],'public_archive_records':audit['summary']['record_count'],
            'tamper_controls':study['tamper_attempts'],
            'native_defined_evaluations_per_compiler':baseline_study['native']['unique_defined_evaluations'],
            'native_compilers':baseline_study['native']['compilers'],
            'security_request_rejections':security['request_rejection_cases'],
            'security_certificate_type_rejections':security['certificate_type_rejection_cases'],
            'security_json_text_rejections':security['json_text_rejection_cases'],
            'operator_probes':security['operator_probes'],
            'disk_requests_reloaded':disk_audit['request_files_reloaded'],
            'disk_full_certificates_validated':disk_audit['full_vector_certificates_validated'],
            'disk_compact_certificates_validated':disk_audit['compact_refutation_certificates_validated'],
            'disk_grammar_results_validated':disk_audit['grammar_results_validated'],
            'producer_complexity_regression':edge['producer_complexity'],
            'left_deep_ast_regression':edge['left_deep_ast'],
            'selector_admission_regression':edge['selector_admission'],
            'holdout_differential_cases':holdout_summary['cases'],
            'holdout_oracle_agreements':holdout_summary['oracle_agreements'],
            'holdout_compact_refutations':holdout_summary['compact_refutations_verified'],
            'holdout_forged_refutations_rejected':holdout_summary['forged_refutations_rejected'],
            'wall_seconds':time.monotonic()-started,
            'scope_note':'Codeflaws evidence is an archival index audit; public sources are not executed by this command.'}
    (out/'complete-reproduction.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
