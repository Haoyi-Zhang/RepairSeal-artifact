"""Term-space pressure cannot let an invalid packet evict established facts."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
import proof_dag_checker as core
from proof_dag_producer import produce
from reusing_checker import ReceiverCache, check_reusing, direct_reusing


def request(seed, additions=256):
    source = 'unsigned f(unsigned x) { return x; }'
    body = 'unsigned y = x; ' + ' '.join(
        'y = y + '+str(seed*additions+i+1)+'u;' for i in range(additions))
    return dict(id='cache-transaction-'+str(seed),word_bits=32,inputs={'x':[1]},
                original=source, candidate='unsigned f(unsigned x) { '+body+' return y; }',
                reference=source, repair_guard='x == x')


def corrupt(packet):
    bad = copy.deepcopy(packet)
    bad['nodes'][-1]['vector'][-1] = not bad['nodes'][-1]['vector'][-1]
    body = {k:v for k,v in bad.items() if k!='certificate_sha256'}
    bad['certificate_sha256'] = hashlib.sha256(core.canonical_bytes(body)).hexdigest()
    return bad


class CacheAtomicityTests(unittest.TestCase):
    def test_invalid_new_terms_leave_both_stores_unchanged(self):
        cache = ReceiverCache()
        old = request(0, 2)
        check_reusing(old, produce(old), cache)
        before = copy.deepcopy((cache._terms, cache._cells))
        new = request(1, 2)
        with self.assertRaises(core.Invalid):
            check_reusing(new, corrupt(produce(new)), cache)
        self.assertEqual((cache._terms, cache._cells), before)
        warm = check_reusing(old, produce(old), cache)
        self.assertEqual(warm['recomputed_cells'], 0)

    def test_invalid_packet_under_term_pressure_cannot_evict(self):
        cache = ReceiverCache()
        # Populate through genuine, successful receiver calls. No forged cache
        # state or changed capacity is needed to reach the documented boundary.
        seed = 0
        while len(cache._terms) < 32000:
            old = request(seed)
            direct_reusing(old, cache)
            seed += 1
            self.assertLess(seed, 100)
        before = copy.deepcopy((cache._terms, cache._cells))
        new = request(seed)
        packet = produce(new)
        self.assertGreater(len(cache._terms)+len(packet['nodes']), 32768)
        with self.assertRaises(core.Invalid): check_reusing(new, corrupt(packet), cache)
        self.assertEqual((cache._terms, cache._cells), before)
        # A subsequent valid packet commits the same reset as a cold receiver,
        # with current roots, source bindings and all submitted cells checked.
        actual = check_reusing(new, packet, cache)
        cold = core.check(new, packet)
        self.assertEqual((actual['status'], actual['witness']), (cold['status'], cold['witness']))
        self.assertEqual(actual['reused_cells'], 0)
        self.assertEqual(actual['recomputed_cells'], cold['checked_cells'])
        self.assertLessEqual(len(cache._terms), 32768)
        self.assertLessEqual(len(cache._cells), cache.capacity)
        self.assertEqual(check_reusing(new, packet, cache)['recomputed_cells'], 0)


if __name__=='__main__': unittest.main()
