"""Regression cases from the second independent receiving-boundary audit.

Each receiver-version probe runs in a fresh Python process. The historical
checker and journal are exact retained source preimages, not mocks of a
particular return value. No test changes the active implementation on disk.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OLD_CORE = ROOT / 'tests/fixtures/lexical-checker.py'
OLD_JOURNAL = ROOT / 'tests/fixtures/unbound-journal.py'
CR_REQUEST = ROOT / 'tests/fixtures/carriage-return-request.json'

PROBE = r'''
import json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import admission_journal as journal
import proof_dag_checker as core
request = core.load_json_strict(pathlib.Path(sys.argv[3]).read_text())
owner = journal.AdmissionJournal(sys.argv[2])
results = []
try:
    for operation in json.loads(sys.argv[4]):
        try:
            action = operation['action']
            if action == 'register':
                value = owner.register(request)
            elif action == 'decide':
                value = owner.decide(request['id'], operation['token'], 'direct')
            elif action == 'approved':
                value = owner.approved(request['id'], journal.request_identity(request))
            elif action == 'evaluate':
                value = core.evaluate_topological(request)
            elif action == 'rows':
                value = [dict(zip([c[0] for c in cursor.description], row))
                         for cursor in [owner.db.execute('SELECT * FROM receipts ORDER BY token')]
                         for row in cursor]
            elif action == 'corrupt_body':
                changed = dict(request)
                changed['candidate'] = 'unsigned f(unsigned x) { return x + 1u; }'
                owner.db.execute('UPDATE requests SET body=? WHERE id=?',
                                 (json.dumps(changed), request['id']))
                value = None
            else:
                raise RuntimeError('unknown probe action')
            results.append({'action': action, 'value': value})
        except Exception as error:
            results.append({'action': operation['action'],
                            'error': type(error).__name__, 'message': str(error)})
    print(json.dumps({'receiver_identity': getattr(owner, 'receiver_identity', None),
                      'results': results}, sort_keys=True))
finally:
    owner.close()
'''


def probe(source_directory, database, request, operations):
    command = [sys.executable, '-B']
    if sys.flags.optimize:
        command.append('-' + 'O' * sys.flags.optimize)
    command += ['-c', PROBE, str(source_directory), str(database),
                str(request), json.dumps(operations)]
    result = subprocess.run(command, text=True, capture_output=True, timeout=20,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    if result.returncode:
        raise RuntimeError(f'receiver probe exited {result.returncode}: {result.stderr}')
    return json.loads(result.stdout)


def version_directory(destination, core_path, journal_path, *, core_suffix='', journal_suffix=''):
    destination.mkdir()
    (destination / 'proof_dag_checker.py').write_bytes(core_path.read_bytes() + core_suffix.encode())
    (destination / 'admission_journal.py').write_bytes(journal_path.read_bytes() + journal_suffix.encode())
    return destination


class ReceiverUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.base = Path(self.directory.name)
        self.database = self.base / 'journal.sqlite'
        self.valid = self.base / 'valid.json'
        self.valid.write_text(json.dumps({
            'id': 'owned-version-regression', 'word_bits': 32,
            'inputs': {'x': [0, 1, 4294967295]},
            'original': 'unsigned f(unsigned x) { return x; }',
            'candidate': 'unsigned f(unsigned x) { return x; }',
            'reference': 'unsigned f(unsigned x) { return x; }',
            'repair_guard': 'x == x',
        }))

    def tearDown(self):
        self.directory.cleanup()

    def seed(self, directory, request):
        result = probe(directory, self.database, request, [
            {'action': 'register'}, {'action': 'decide', 'token': 'old'},
            {'action': 'approved'},
        ])
        self.assertEqual(result['results'][1]['value']['semantic_status'], 'ACCEPT')
        self.assertIs(result['results'][2]['value'], True)
        return result

    def check_stale(self, directory, request):
        result = probe(directory, self.database, request, [
            {'action': 'approved'}, {'action': 'decide', 'token': 'old'},
            {'action': 'rows'},
        ])
        self.assertIs(result['results'][0]['value'], False)
        self.assertEqual(result['results'][1]['error'], 'ValueError')
        self.assertIn('receiver implementation', result['results'][1]['message'])
        self.assertEqual(len(result['results'][2]['value']), 1)
        return result

    def test_actual_pre_fix_false_acceptance_cannot_survive_upgrade(self):
        legacy = version_directory(self.base / 'legacy', OLD_CORE, OLD_JOURNAL)
        self.seed(legacy, CR_REQUEST)
        # The immediate pre-fix journal still repeats the old wrong decision
        # under the corrected core; this is the concrete historical failure.
        unbound = version_directory(self.base / 'unbound', ROOT / 'src/proof_dag_checker.py', OLD_JOURNAL)
        before = probe(unbound, self.database, CR_REQUEST, [
            {'action': 'evaluate'}, {'action': 'approved'},
            {'action': 'decide', 'token': 'old'},
        ])
        self.assertEqual(before['results'][0]['value']['status'], 'REFUTED')
        self.assertIs(before['results'][1]['value'], True)
        self.assertIs(before['results'][2]['value']['approved'], True)
        migrated = self.check_stale(ROOT / 'src', CR_REQUEST)
        self.assertIsNone(migrated['results'][2]['value'][0]['receiver_identity'])
        after = probe(ROOT / 'src', self.database, CR_REQUEST, [
            {'action': 'decide', 'token': 'new'}, {'action': 'approved'},
            {'action': 'rows'},
        ])
        receipt = after['results'][0]['value']
        self.assertEqual(receipt['semantic_status'], 'REFUTED')
        self.assertEqual(receipt['witness'], {'obligation': 'repair', 'trace': [], 'input': [0]})
        self.assertEqual(receipt['receiver_identity'], after['receiver_identity'])
        self.assertIs(after['results'][1]['value'], False)
        self.assertEqual(len(after['results'][2]['value']), 2)

    def test_unversioned_valid_receipt_requires_successful_rechecking(self):
        legacy = version_directory(self.base / 'legacy', OLD_CORE, OLD_JOURNAL)
        self.seed(legacy, self.valid)
        self.check_stale(ROOT / 'src', self.valid)
        after = probe(ROOT / 'src', self.database, self.valid, [
            {'action': 'decide', 'token': 'new'}, {'action': 'approved'},
            {'action': 'decide', 'token': 'new'},
        ])
        self.assertEqual(after['results'][0]['value']['semantic_status'], 'ACCEPT')
        self.assertIs(after['results'][1]['value'], True)
        self.assertIs(after['results'][2]['value']['replayed_receipt'], True)

    def test_unchanged_receiver_is_relocatable_and_reopens_idempotently(self):
        initial = self.seed(ROOT / 'src', self.valid)
        relocated = version_directory(self.base / 'relocated', ROOT / 'src/proof_dag_checker.py',
                                      ROOT / 'src/admission_journal.py')
        reopened = probe(relocated, self.database, self.valid, [
            {'action': 'approved'}, {'action': 'decide', 'token': 'old'},
        ])
        self.assertEqual(initial['receiver_identity'], reopened['receiver_identity'])
        self.assertIs(reopened['results'][0]['value'], True)
        self.assertIs(reopened['results'][1]['value']['replayed_receipt'], True)

    def test_versioned_core_change_requires_rechecking(self):
        initial = self.seed(ROOT / 'src', self.valid)
        changed = version_directory(self.base / 'changed', ROOT / 'src/proof_dag_checker.py',
                                    ROOT / 'src/admission_journal.py',
                                    core_suffix='\n# Conservative implementation identity regression.\n')
        stale = self.check_stale(changed, self.valid)
        self.assertNotEqual(initial['receiver_identity'], stale['receiver_identity'])
        renewed = probe(changed, self.database, self.valid, [
            {'action': 'decide', 'token': 'new'}, {'action': 'approved'},
        ])
        self.assertEqual(renewed['results'][0]['value']['semantic_status'], 'ACCEPT')
        self.assertIs(renewed['results'][1]['value'], True)

    def test_journal_implementation_also_belongs_to_identity(self):
        initial = self.seed(ROOT / 'src', self.valid)
        changed = version_directory(self.base / 'changed', ROOT / 'src/proof_dag_checker.py',
                                    ROOT / 'src/admission_journal.py',
                                    journal_suffix='\n# Conservative consumer identity regression.\n')
        stale = self.check_stale(changed, self.valid)
        self.assertNotEqual(initial['receiver_identity'], stale['receiver_identity'])

    def test_receipt_replay_and_approval_check_current_body_integrity(self):
        self.seed(ROOT / 'src', self.valid)
        result = probe(ROOT / 'src', self.database, self.valid, [
            {'action': 'corrupt_body'}, {'action': 'approved'},
            {'action': 'decide', 'token': 'old'}, {'action': 'decide', 'token': 'new'},
            {'action': 'rows'},
        ])
        for observed in result['results'][1:4]:
            self.assertEqual(observed['error'], 'ValueError')
            self.assertIn('authoritative request identity changed', observed['message'])
        self.assertEqual(len(result['results'][4]['value']), 1)


if __name__ == '__main__':
    unittest.main()
