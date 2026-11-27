#!/usr/bin/env python3
"""Run offline reproduction and write its summary."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from scientific_driver import new_output_directory, require_assertions
from reproduce_all_core import compare_exact
from verify_natural_domain_evidence import verify as verify_native_evidence

# The review update adds exactly this module. The historical unsigned contract
# campaign does not import it. Bind its bytes as well as its name; this is not
# a wildcard exception for later source additions or altered historical code.
REVIEW_SOURCE_ADDITIONS = {
    'src/int32_refutation.py': 'f5eb16eea7f3e337524d33c67a2faecf154ba694b5cf23d42ef1dd773a51a133',
}


def source_bindings(root):
    """Bind the complete local Python implementation and driver inventory."""
    paths = [*sorted((root / 'src').glob('*.py')), *sorted((root / 'tests').glob('*.py'))]
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def run_check(root, command, timeout):
    if '-p' in command:
        pattern = command[command.index('-p') + 1]
        if not any((root / 'tests').glob(pattern)):
            raise RuntimeError('required conformance test is missing: ' + pattern)
    return subprocess.run(command, cwd=root, capture_output=True, text=True,
                          env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, timeout=timeout)


def compare_contract_study(root, retained, current):
    """Reconcile bounded source-inventory and receiver-identity transitions.

    The unchanged study driver binds every top-level source module, including
    three round-3 modules and the one hash-pinned review-update module that it
    does not import. Domain-transport receipts
    also bind the Python implementation and version, so an otherwise identical
    fresh run has a new receiver identity. Validate both transitions explicitly
    before comparing every scientific field. This is not permission for
    arbitrary future modules, identities, or changed historical evidence.
    """
    record_names = ('protocol.json', 'corpus-bindings.json', 'decisions.json', 'transport.json')
    permitted_additions = {
        'src/codeflaws_int32_bridge.py', 'src/demand_evaluator.py', 'src/int32_circuit.py',
    } | set(REVIEW_SOURCE_ADDITIONS)
    documents = {}
    actual_records = {}
    for side, directory in (('retained', retained), ('current', current)):
        documents[side] = {name: json.loads((directory / name).read_text())
                           for name in (*record_names, 'summary.json')}
        actual_records[side] = {
            name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in record_names
        }
        compare_exact(actual_records[side], documents[side]['summary.json']['records'],
                      'contract comparison ' + side + ' actual record hashes')

    paths = [*sorted((root / 'src').glob('*.py')),
             root / 'tests/contract_comparison.py', root / 'tests/scientific_driver.py']
    current_inventory = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in paths}
    historical_bindings = documents['retained']['protocol.json']['source_bindings']
    current_bindings = documents['current']['protocol.json']['source_bindings']
    if type(historical_bindings) is not dict or type(current_bindings) is not dict:
        raise AssertionError('contract comparison source bindings must be objects')
    compare_exact(current_inventory, current_bindings,
                  'contract comparison complete current source inventory')
    missing = set(historical_bindings) - set(current_inventory)
    if missing:
        raise AssertionError('contract comparison missing historical source: ' + ', '.join(sorted(missing)))
    for name, digest in historical_bindings.items():
        compare_exact(digest, current_inventory[name], 'contract comparison unchanged historical source ' + name)
    additions = set(current_inventory) - set(historical_bindings)
    compare_exact(sorted(permitted_additions), sorted(additions),
                  'contract comparison declared round-3 and review source additions')
    for name, digest in REVIEW_SOURCE_ADDITIONS.items():
        compare_exact(digest, current_inventory[name],
                      'contract comparison exact review source addition ' + name)

    compare_exact(
        {key: value for key, value in documents['retained']['protocol.json'].items() if key != 'source_bindings'},
        {key: value for key, value in documents['current']['protocol.json'].items() if key != 'source_bindings'},
        'contract comparison protocol scientific fields')
    for name in ('corpus-bindings.json', 'decisions.json'):
        compare_exact(documents['retained'][name], documents['current'][name],
                      'contract comparison ' + name)

    def normalized_transport(rows, side):
        if type(rows) is not list or not rows:
            raise AssertionError('contract comparison ' + side + ' transport inventory')
        normalized = copy.deepcopy(rows)
        identities = set()
        for index, row in enumerate(normalized):
            receipt = row.get('receipt') if type(row) is dict else None
            identity = receipt.get('receiver_identity') if type(receipt) is dict else None
            if type(identity) is not str or len(identity) != 64:
                raise AssertionError('contract comparison ' + side + ' receiver identity at row ' + str(index))
            try:
                int(identity, 16)
            except ValueError as error:
                raise AssertionError('contract comparison ' + side + ' receiver identity encoding') from error
            identities.add(identity)
            receipt['receiver_identity'] = '<verified-receiver-identity>'
        if len(identities) != 1:
            raise AssertionError('contract comparison ' + side + ' mixed receiver identities')
        return normalized, identities.pop()

    retained_transport, retained_receiver = normalized_transport(
        documents['retained']['transport.json'], 'retained')
    current_transport, current_receiver = normalized_transport(
        documents['current']['transport.json'], 'current')
    compare_exact(retained_transport, current_transport,
                  'contract comparison transport scientific fields')

    source_path = str(root / 'src')
    inserted = source_path not in sys.path
    if inserted:
        sys.path.insert(0, source_path)
    try:
        from domain_transport import receiver_identity
        compare_exact(receiver_identity(), current_receiver,
                      'contract comparison current receiver identity')
    finally:
        if inserted:
            sys.path.remove(source_path)

    # Protocol source inventory and transport receiver identity are the only
    # verified transitions. Both sides' record hashes were checked against
    # their own files; every other record and summary field stays exact.
    normalized_summary = dict(documents['retained']['summary.json'])
    normalized_summary['records'] = dict(actual_records['retained'])
    for name in ('protocol.json', 'transport.json'):
        normalized_summary['records'][name] = actual_records['current'][name]
    compare_exact(normalized_summary, documents['current']['summary.json'],
                  'contract comparison summary after verified identity transitions')
    return {
        'schema': 'contract-comparison-source-reconciliation-v2',
        'outcome': 'PASS_DECLARED_SOURCE_AND_RECEIVER_TRANSITIONS',
        'historical_source_bindings': historical_bindings,
        'current_source_bindings': current_bindings,
        'added_source_bindings': {name: current_inventory[name] for name in sorted(additions)},
        'historical_bindings_unchanged': True,
        'current_inventory_exact': True,
        'historical_receiver_identity': retained_receiver,
        'current_receiver_identity': current_receiver,
        'current_receiver_identity_exact': True,
        'transport_scientific_fields_exact': True,
        'actual_record_hashes': actual_records,
        'normalized_summary_record_hashes': ['protocol.json', 'transport.json'],
        'all_other_protocol_records_and_summary_fields_exact': True,
    }


def compare_natural_study(retained, current):
    # Only the optional external acquisition/execution switches differ. The
    # domain construction, source identities and all scalar evidence stay exact.
    for name in ('request-results.json', 'domain-results.json', 'requests.json',
                 'test-slot-results.json', 'source-binding-check.json'):
        compare_exact(json.loads((retained / name).read_text()), json.loads((current / name).read_text()), name)
    protocol = json.loads((retained / 'protocol.json').read_text())
    protocol.update(archive_reverified=False, native_requested=False)
    compare_exact(protocol, json.loads((current / 'protocol.json').read_text()), 'natural domain protocol')
    summary = json.loads((retained / 'summary.json').read_text())
    summary.update(archive_reverified=False, native=None)
    compare_exact(summary, json.loads((current / 'summary.json').read_text()), 'natural domain summary')
    for row in json.loads((retained / 'request-results.json').read_text()):
        before = retained / row['record']; after = current / row['record']
        compare_exact(sorted(path.name for path in before.iterdir()), sorted(path.name for path in after.iterdir()), 'natural request files')
        for path in before.iterdir():
            if path.read_bytes() != (after / path.name).read_bytes():
                raise AssertionError('natural request payload differs: ' + row['record'] + '/' + path.name)
    # Reconciliation checks the separately retained native observations and
    # their populations; the default gate does not execute the external C units.
    return verify_native_evidence(retained)


def _run(args) -> None:
    root=Path(__file__).resolve().parents[1]
    implementation_bindings=source_bindings(root)
    core = Path(__file__).with_name("reproduce_all_core.py")
    core_command = [sys.executable, str(core), "--output", str(args.output)]
    if args.child_timeout is not None:
        core_command += ["--child-timeout", str(args.child_timeout)]
    proc = subprocess.run(
        core_command,
        text=True,
        capture_output=True,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
    )
    (args.output / 'core-reproduction.log').write_text(proc.stdout + proc.stderr, encoding='utf-8')
    if proc.returncode:
        if proc.stdout:
            print(proc.stdout, end="", file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        raise SystemExit(proc.returncode)
    result_path = args.output / "complete-reproduction.json"
    result = json.loads(result_path.read_text())
    result['core_outcome'] = result['outcome']
    result['outcome'] = 'RUNNING_EXTENDED_REPRODUCTION'
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    stream_commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_vector_stream.py','-v'],
        [sys.executable,'-O','-B','-m','unittest','discover','-s','tests','-p','test_vector_stream.py','-v'],
        [sys.executable,'-B',str(root/'tests/check_vector_stream_replay.py'),'--output',
         str(args.output.resolve()/'vector-stream.json'),'--compare',str(root/'results/vector-stream.json')],
    ]
    for index,command in enumerate(stream_commands):
        check=run_check(root,command,args.child_timeout if args.child_timeout is not None else 120)
        (args.output/('vector-stream-check-'+str(index)+'.txt')).write_text(
            check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:
            raise SystemExit('bounded vector stream reproduction failed: '+str(index))
    stream_packet=json.loads((args.output/'vector-stream.json').read_text(encoding='utf-8'))
    stream_result=stream_packet['current_logical_replay']
    result['vector_stream_agreement']={
        'requests':stream_result['requests'],'semantic_cells_per_arm':stream_result['totals']['checked_cells_per_arm'],
        'ordinary_and_optimized_conformance':True,
        'allocation_measurement':'retained separate runtime-specific study; not rerun by deterministic gate',
        'retained_source_comparison':stream_packet['retained_comparison'],
    }
    macro_commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_macro_bridge.py','-v'],
        [sys.executable,'-O','-B','-m','unittest','discover','-s','tests','-p','test_macro_bridge.py','-v'],
        [sys.executable,'-B',str(root/'tests/macro_transfer_study.py'),'--native','--output',
         str(args.output.resolve()/'macro-transfer')],
    ]
    for index,command in enumerate(macro_commands):
        check=run_check(root,command,args.child_timeout if args.child_timeout is not None else 120)
        (args.output/('macro-transfer-check-'+str(index)+'.txt')).write_text(
            check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise SystemExit('typed macro transfer reproduction failed: '+str(index))
    macro=json.loads((args.output/'macro-transfer/summary.json').read_text(encoding='utf-8'))
    result['typed_macro_transfer']={k:macro[k] for k in
        ('upstream_changes','inputs','repair_inputs','preserved_inputs','status',
         'cells_per_full_or_direct_arm','native_input_rows','native_scalar_observations',
         'upstream_application_executed')}
    descriptor_commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_descriptor_consumer.py','-v'],
        [sys.executable,'-O','-B','-m','unittest','discover','-s','tests','-p','test_descriptor_consumer.py','-v'],
        [sys.executable,'-B',str(root/'tests/descriptor_consumer_study.py'),'--native','--output',
         str(args.output.resolve()/'descriptor-consumer'),'--compare',str(root/'data/descriptor-consumer')],
    ]
    for index,command in enumerate(descriptor_commands):
        check=run_check(root,command,args.child_timeout if args.child_timeout is not None else 120)
        (args.output/('descriptor-consumer-check-'+str(index)+'.txt')).write_text(check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise SystemExit('descriptor consumer reproduction failed: '+str(index))
    descriptor=json.loads((args.output/'descriptor-consumer/summary.json').read_text(encoding='utf-8'))
    result['descriptor_consumer']={k:descriptor[k] for k in
        ('input_pairs','native_loop_admitted_pairs','excluded_pairs','old_under_reserved_pairs',
         'new_consumer_success_pairs','native_role_rows','upstream_application_or_gpu_executed')}
    # The revision closes a source-lexing soundness defect and makes failed
    # receiver-cache operations atomic.  Exercise both modes in the public
    # gate, then reproduce the newly added finite-domain boundary study.
    revision_commands=[]
    for pattern in ('test_source_lexing.py','test_cache_atomicity.py'):
        for optimized in (False,True):
            revision_commands.append([sys.executable,*(['-O'] if optimized else []),'-B',
                '-m','unittest','discover','-s','tests','-p',pattern,'-v'])
    revision_commands.extend([
        [sys.executable,'-B',str(root/'tests/receiver_reuse_study.py'),'--output',
         str(args.output.resolve()/'receiver-reuse.json'),'--compare',str(root/'results/receiver-reuse.json')],
        [sys.executable,'-B',str(root/'tests/domain_adequacy_study.py'),'--output',
         str(args.output.resolve()/'domain-adequacy')],
        [sys.executable,'-B',str(root/'tests/admission_journal_study.py'),'--output',
         str(args.output.resolve()/'admission-journal')],
        [sys.executable,'-B',str(root/'tests/report_admission_results.py'),'--output',
         str(args.output.resolve()/'admission-results.tex'),'--results',
         str(args.output.resolve()/'admission-journal')],
    ])
    for index,command in enumerate(revision_commands):
        check=run_check(root,command,args.child_timeout if args.child_timeout is not None else 120)
        (args.output/('revision-check-'+str(index)+'.txt')).write_text(check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise SystemExit('revision reproduction failed: '+str(index))
    domain=json.loads((args.output/'domain-adequacy/summary.json').read_text(encoding='utf-8'))
    retained_domain=root/'data/domain-study'
    for name in ('protocol.json','outcomes.json','domain-replays.json','summary.json'):
        now=json.loads((args.output/'domain-adequacy'/name).read_text(encoding='utf-8'))
        old=json.loads((retained_domain/name).read_text(encoding='utf-8'))
        if json.dumps(now,sort_keys=True,allow_nan=False) != json.dumps(old,sort_keys=True,allow_nan=False):
            raise SystemExit('domain-adequacy scientific replay differs: '+name)
    result['revision_contract_checks']={'ordinary_and_optimized_source_lexing':True,
        'ordinary_and_optimized_cache_atomicity':True,
        'reuse_requests':380,
        'domain_requests':domain['requests'],
        'domain_full_direct_literal_agreements':domain['full_direct_literal_agreements'],
        'domain_candidate_point_observations':domain['candidate_point_observations'],
        'domain_old_packets_rejected':domain['old_domain_packets_rejected'],
        'domain_stale_approval_rejected':domain['journal_domain_change']['stale_approval_rejected']}
    admission=json.loads((args.output/'admission-journal/summary.json').read_text(encoding='utf-8'))
    result['current_admission_journal']={k:admission[k] for k in
        ('requests','approved','refuted','receiver_processes','proof_direct_agreements','stale_approval_rejected','receiver_identity')}
    round2_commands=[]
    for pattern in ('test_domain_transport.py','test_receiving_boundaries.py'):
        for optimized in (False,True):
            round2_commands.append([sys.executable,*(['-O'] if optimized else []),'-B',
                '-m','unittest','discover','-s','tests','-p',pattern,'-v'])
    for pattern in ('test_driver_contracts.py','test_natural_domains.py','test_current_admission_report.py',
                    'test_natural_domain_evidence.py'):
        round2_commands.append([sys.executable,'-B','-m','unittest','discover','-s','tests','-p',pattern,'-v'])
    round2_commands.extend([
        [sys.executable,'-B',str(root/'tests/contract_comparison.py'),'--output',str(args.output/'contract-comparison')],
        [sys.executable,'-B',str(root/'tests/natural_domain_study.py'),'--output',str(args.output/'natural-domains')],
    ])
    for index,command in enumerate(round2_commands):
        check=run_check(root,command,args.child_timeout if args.child_timeout is not None else 300)
        (args.output/('round2-check-'+str(index)+'.txt')).write_text(check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise SystemExit('round2 reproduction failed: '+str(index))
    retained_comparison=root/'data/contract-study'
    result['same_contract_source_reconciliation']=compare_contract_study(
        root, retained_comparison, args.output/'contract-comparison')
    comparison=json.loads((args.output/'contract-comparison/summary.json').read_text())
    result['same_contract_comparison']={key:comparison[key] for key in
        ('same_canonical_results','guarded_reference_point_agreements','corpora','transport')}
    native_reconciled=compare_natural_study(root/'data/natural-domains',args.output/'natural-domains')
    natural=json.loads((args.output/'natural-domains/summary.json').read_text())
    result['natural_domain_study']={key:natural[key] for key in
        ('source_pairs','natural_candidate_versions','authored_candidates','domains','domain_verdicts',
         'requests','accepted_requests','refuted_requests','candidate_point_observations',
         'full_direct_semantic_cells','compact_refutations','full_direct_literal_disagreements')}
    result['retained_natural_native_reconciliation']=native_reconciled
    result['round2_driver_checks']={'optimized_scientific_runs_rejected':True,
        'typed_scientific_comparison':True,'retained_output_preserved':True,
        'receiver_version_binding_normal_and_optimized':True,'support_transport_normal_and_optimized':True}
    candidates = list(args.output.rglob("structured-study.json"))
    if len(candidates) != 1:
        raise SystemExit(f"expected one structured-study.json, found {len(candidates)}")
    study = json.loads(candidates[0].read_text())
    result.update(
        {
            "structured_requests": study["total_requests"],
            "oracle_agreements": study["oracle_agreements"],
            "full_vector_tamper_controls": study["tamper_attempts"],
            "full_vector_tamper_rejections": study["tamper_rejections"],
            "refutation_witnesses": study["refutation_witnesses"],
            "refutation_witness_agreements": study["refutation_witness_agreements"],
            "refutation_tamper_controls": study["refutation_tamper_attempts"],
            "refutation_tamper_rejections": study["refutation_tamper_rejections"],
            "acceptance_misuse_controls": study["acceptance_misuse_attempts"],
            "acceptance_misuse_rejections": study["acceptance_misuse_rejections"],
            "total_certificate_negative_controls": (
                study["tamper_attempts"]
                + study["refutation_tamper_attempts"]
                + study["acceptance_misuse_attempts"]
            ),
            "full_vector_work_equivalence": study["work_equivalence"],
            "compact_refutation_work": study["refutation_work"],
            "scope_note": (
                "Codeflaws evidence is a pinned archival index audit; public sources "
                "are not executed. Generated stress requests are not Codeflaws."
            ),
        }
    )
    compare_exact(implementation_bindings,source_bindings(root),'scientific implementation changed during reproduction')
    result['implementation_bindings']=implementation_bindings
    result['implementation_unchanged_during_reproduction']=True
    result['outcome']='PASS_COMPLETE_REPRODUCTION'
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--child-timeout', type=float,
                        help='finite positive wall limit propagated to each scientific child')
    args = parser.parse_args()
    if args.child_timeout is not None and (not math.isfinite(args.child_timeout) or args.child_timeout <= 0):
        parser.error('child-timeout must be finite and positive')
    # This check happens before the failure-record path so a refused existing
    # destination is never modified while reporting that refusal.
    args.output = new_output_directory(args.output)
    try:
        _run(args)
    except BaseException as error:
        path = args.output / 'complete-reproduction.json'
        try:
            result = json.loads(path.read_text()) if path.exists() else {}
        except (OSError, ValueError):
            result = {}
        result.update(outcome='FAILED_COMPLETE_REPRODUCTION',
                      failure_type=type(error).__name__, failure=str(error))
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        raise


if __name__ == "__main__":
    main()
