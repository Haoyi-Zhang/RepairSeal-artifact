import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from admission_journal import request_identity, receiver_identity, identity as payload_identity
from proof_dag_checker import check, evaluate_topological, exact_equal, load_json_strict

CURRENT_RESULTS=ROOT/'revision_audit/round2/admission-journal-final'
CASES=('original','supplied','regression','definedness','trace-overfit')
EXPECTED_BINDINGS=set(['src/admission_journal.py','src/proof_dag_checker.py',
    'tests/admission_journal_study.py','tests/report_admission_results.py']+[
    'results/upstream-ceil/'+name+suffix+'.json'
    for name in CASES for suffix in ('-request','-full')])

def load(path):return load_json_strict(path.read_text(encoding='utf-8'))

def validate_current(results):
    """Derive counts from current replay and inspect the closed receipt stores."""
    data=load(results/'summary.json');registration=load(results/'registration.json')
    records=load(results/'records.json')
    bindings=data.get('source_bindings')
    if type(bindings) is not dict or set(bindings)!=EXPECTED_BINDINGS:
        raise ValueError('admission source binding inventory')
    if not exact_equal(registration.get('source_bindings'),bindings):
        raise ValueError('admission registration bindings differ')
    for name,wanted in bindings.items():
        if type(wanted) is not str or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('stale admission source '+name)
    if registration.get('receiver_modules')!=['admission_journal.py','proof_dag_checker.py']:
        raise ValueError('admission receiver import boundary')
    current_receiver=receiver_identity()
    if data.get('receiver_identity')!=current_receiver or registration.get('receiver_identity')!=current_receiver:
        raise ValueError('admission receiver implementation identity')
    rows=records.get('rows')
    if type(rows) is not list or [row.get('case') for row in rows]!=list(CASES):
        raise ValueError('admission case inventory')
    approved=0
    for row in rows:
        name=row['case'];request=load(ROOT/'results/upstream-ceil'/str(name+'-request.json'))
        packet=load(ROOT/'results/upstream-ceil'/str(name+'-full.json'))
        expected=check(request,packet);direct=evaluate_topological(request)
        if not exact_equal(expected,direct):
            # The modes may carry different descriptive fields; their
            # semantic decision, witness and cell counts must still agree.
            for field in ('status','witness','checked_cells'):
                if not exact_equal(expected[field],direct[field]):raise ValueError('admission full/direct mismatch')
        for mode in ('proof','direct'):
            saved=row[mode]
            if (saved.get('request_identity')!=request_identity(request)
                    or saved.get('request_id')!=request['id']
                    or type(saved.get('revision')) is not int or saved['revision']!=1
                    or saved.get('mode')!=mode
                    or saved.get('packet_identity')!=payload_identity(packet if mode=='proof' else None)
                    or saved.get('receiver_identity')!=current_receiver):
                raise ValueError('admission receipt identity or revision')
            for field,source_field in (('semantic_status','status'),('witness','witness'),('checked_cells','checked_cells')):
                if not exact_equal(saved.get(field),expected[source_field]):raise ValueError('admission recorded decision differs')
            if type(saved.get('approved')) is not bool or saved['approved']!=(expected['status']=='ACCEPT'):
                raise ValueError('admission approval differs')
        approved+=row['proof']['approved']
        path=results/'journals'/str(name+'.sqlite')
        database=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
        try:
            stored=list(database.execute('SELECT token,request_id,revision,request_identity,mode,packet_identity,decision,receiver_identity,result FROM receipts ORDER BY token'))
            actual=[load_json_strict(r[-1]) for r in stored]
            expected_receipts=[{k:v for k,v in row[label].items() if k!='replayed_receipt'} for label in ('direct','proof')]
            if not exact_equal(actual,expected_receipts):raise ValueError('admission closed journal receipts differ')
            expected_columns=[[label,*[row[label][field] for field in
                ('request_id','revision','request_identity','mode','packet_identity','semantic_status','receiver_identity')]]
                for label in ('direct','proof')]
            if not exact_equal([list(record[:-1]) for record in stored],expected_columns):
                raise ValueError('admission closed journal metadata differs')
            current=list(database.execute('SELECT revision,identity,body FROM requests'))
            if len(current)!=1:raise ValueError('admission closed journal request inventory')
            revision,identity,body=current[0]
            expected_revision=2 if name=='supplied' else 1
            if revision!=expected_revision or request_identity(load_json_strict(body))!=identity:
                raise ValueError('admission closed journal current identity')
            if name=='supplied' and identity!=records['revised_request']['request_identity']:
                raise ValueError('admission revised identity differs')
        finally:database.close()
    expected_counts=dict(requests=len(rows),proof_direct_agreements=len(rows),approved=approved,
                         refuted=len(rows)-approved,receiver_processes=len(records['raw_processes']))
    if expected_counts['receiver_processes']!=28:
        raise ValueError('admission process inventory')
    for name,value in expected_counts.items():
        if type(data.get(name)) is not int or data[name]!=value:
            raise ValueError('admission summary count differs')
    if (data.get('status')!='PASS' or data.get('stale_approval_rejected') is not True
            or records['stale_approval'].get('approved') is not False
            or data.get('producer_module_in_receiver') is not False
            or data.get('performance_claim') is not False
            or data.get('scientific_sources_unchanged_during_run') is not True):
        raise ValueError('admission result scope differs')
    return expected_counts

def render(path,results=CURRENT_RESULTS):
    data=validate_current(results)
    fields={'AdmissionRequests':'requests','AdmissionProcesses':'receiver_processes','AdmissionApprovals':'approved','AdmissionRefutations':'refuted'}
    path.write_text(''.join('\\newcommand{\\'+key+'}{'+str(data[value])+'}\n' for key,value in fields.items()),encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--results',type=Path,default=CURRENT_RESULTS)
    args=p.parse_args();render(args.output,args.results)
