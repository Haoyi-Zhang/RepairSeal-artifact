"""Source-byte and physical-line conformance at the certificate boundary.

Only tiny owned, fully defined scalar functions are compiled. Certificates
continue to bind exact source bytes although the lexers recognize CR, LF and
CRLF as physical line ends. No third-party source or undefined C is executed.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import checker as literal
import proof_dag_checker as full
import producer
from proof_dag_producer import produce
from refutation_witness_checker import check as compact_check
from refutation_witness_producer import produce as compact_produce
from reusing_checker import ReceiverCache, check_reusing
from vector_stream import check_stream, encode_packet
from macro_bridge import translate, Unsupported as MacroUnsupported

BASE = 'unsigned f(unsigned x) { return x; }'
AXIS = [0, 1, 4294967295]


def source(line_end='\r', tail='\n'):
    return ('unsigned f(unsigned x) { unsigned y = x; // physical line'
            + line_end + ' y = x + 1u;' + tail + ' return y; }')


def request(candidate, guard='x == x'):
    return dict(id='physical-line-conformance', word_bits=32, inputs={'x': AXIS[:]},
                original=BASE, candidate=candidate, reference=BASE, repair_guard=guard)


def semantic(result):
    return {key: result[key] for key in ('status', 'witness')}


class SourceLexingTests(unittest.TestCase):
    def test_physical_line_ends_preserve_the_following_statement(self):
        for ending in ('\n', '\r\n', '\r'):
            for tail in ('\n', '\r\n', '\r', ' '):
                with self.subTest(line_end=repr(ending), tail=repr(tail)):
                    req = request(source(ending, tail))
                    session = literal.Session(req)
                    for x in AXIS:
                        self.assertEqual(session.run('candidate', {'x': x}),
                                         (True, (x + 1) % (2 ** 32), ()))
                    expected = {'status': 'REFUTED', 'witness': {
                        'obligation': 'repair', 'input': [0], 'trace': []}}
                    packet = produce(req)
                    results = [full.check(req, packet), full.evaluate_topological(req),
                               check_reusing(req, packet, ReceiverCache()),
                               check_stream(req, io.BytesIO(encode_packet(packet))),
                               compact_check(req, compact_produce(req, expected['witness']))]
                    for result in results:
                        self.assertEqual(semantic(result), expected)
                    replay = producer.Producer(req).certificate()
                    self.assertEqual(semantic(literal.check(req, replay)), expected)

    def test_guard_line_comment_cannot_enlarge_the_repair_region(self):
        for ending in ('\n', '\r\n', '\r'):
            with self.subTest(ending=repr(ending)):
                candidate = 'unsigned f(unsigned x) { return x + 1u; }'
                req = request(candidate, 'x == x // selector'+ending+' && x == 0u')
                req['reference'] = candidate
                expected = {'status': 'REFUTED', 'witness': {
                    'obligation': 'preserve', 'input': [1], 'trace': []}}
                self.assertEqual(semantic(full.check(req, produce(req))), expected)
                self.assertEqual(semantic(literal.check(req, producer.Producer(req).certificate())), expected)

    def test_lexical_normalization_keeps_exact_source_binding(self):
        first = request(source('\n'))
        second = request(source('\r\n'))
        a, b = produce(first), produce(second)
        self.assertEqual(a['nodes'], b['nodes'])
        self.assertNotEqual(a['source_sha256']['candidate'], b['source_sha256']['candidate'])
        self.assertEqual(b['source_sha256']['candidate'],
                         hashlib.sha256(second['candidate'].encode('utf-8')).hexdigest())
        with self.assertRaisesRegex(full.Invalid, 'source binding'):
            full.check(second, a)
        self.assertEqual(second['candidate'], source('\r\n'))

    def test_rebinding_an_old_erased_statement_packet_cannot_approve(self):
        req = request(source())
        fake = produce(dict(req, candidate=BASE))
        fake['source_sha256']['candidate'] = full.digest(req['candidate'])
        body = {k:v for k,v in fake.items() if k != 'certificate_sha256'}
        fake['certificate_sha256'] = hashlib.sha256(full.canonical_bytes(body)).hexdigest()
        cache = ReceiverCache()
        for run in (lambda: full.check(req, fake),
                    lambda: check_reusing(req, fake, cache),
                    lambda: check_stream(req, io.BytesIO(encode_packet(fake)))):
            with self.assertRaises(full.Invalid): run()
        self.assertEqual(cache._cells, {})

    def test_comment_termination_and_final_newline_are_consistent(self):
        for suffix in ('', '\n', '\r', '\r\n', ' // final comment', ' /* final comment */'):
            for ending in ('\n', '\r', '\r\n'):
                with self.subTest(suffix=repr(suffix), ending=repr(ending)):
                    req = request(source(ending, ending)+suffix)
                    self.assertEqual(full.check(req, produce(req))['status'], 'REFUTED')
        req = request(BASE+' /* unterminated')
        with self.assertRaises((full.Invalid, full.Unsupported)):
            full.evaluate_topological(req)
        with self.assertRaises(literal.Unsupported): literal.Session(req)
        with self.assertRaises(producer.ProducerError): producer.Producer(req)

    def test_horizontal_controls_do_not_terminate_line_comments(self):
        for horizontal in ('\t', '\v', '\f'):
            req = request('unsigned f(unsigned x) { unsigned y = x; // comment'
                          +horizontal+' y = x + 1u;\n return y; }')
            self.assertEqual(full.check(req, produce(req))['status'], 'ACCEPT')
            self.assertEqual(literal.Session(req).run('candidate', {'x': 1}), (True, 1, ()))

    def test_unsupported_translation_phase_surfaces_remain_rejected(self):
        for text in ('unsigned f(unsigned x) { // comment\\\n return x; }',
                     'unsigned f(unsigned x) { // ??/\n return x; }',
                     'unsigned f(unsigned x) { // non-ASCII \u00e9\n return x; }',
                     '#define VALUE 1u\n'+BASE,
                     'unsigned f(unsigned x) { return x; }\x00'):
            req = request(text)
            with self.subTest(source=repr(text)):
                with self.assertRaises((full.Invalid, full.Unsupported)):
                    full.evaluate_topological(req)
                with self.assertRaises(literal.Unsupported): literal.Session(req)
                with self.assertRaises(producer.ProducerError): producer.Producer(req)

    def test_selected_macro_must_fit_one_physical_line(self):
        for ending in ('\n', '\r', '\r\n'):
            for definition in ('#define F(X)'+ending+' ((X) + 1u)',
                               '#define F(X) ((X) + 1u)'+ending):
                with self.subTest(definition=repr(definition)), self.assertRaises(MacroUnsupported):
                    translate(definition, ['x'])
        self.assertIn('x + 1u', translate('#define F(X) ((X) + 1u)', ['x'])['source'])

    def test_native_compiler_observes_the_same_physical_lines(self):
        compilers = [path for name in ('gcc', 'clang') if (path := shutil.which(name))]
        if not compilers: self.skipTest('No native C compiler is available')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for compiler in compilers:
                for ending in ('\n', '\r', '\r\n'):
                    for final in ('', '\n', '\r', '\r\n', ' // final comment'):
                        with self.subTest(compiler=compiler, ending=repr(ending), final=repr(final)):
                            # Place main before f so the raw candidate may end at EOF.
                            program = ('#include <limits.h>\n#include <stdio.h>\n'
                                       '_Static_assert(UINT_MAX == 4294967295u, "unsigned width");\n'
                                       'unsigned f(unsigned x);\n'
                                       'int main(void) { printf("%u %u %u\\n", '
                                       'f(0u), f(1u), f(4294967295u)); return 0; }\n'
                                       + source(ending, ending) + final)
                            src, binary = root/'owned.c', root/'owned'
                            src.write_bytes(program.encode('ascii'))
                            build = subprocess.run([compiler, '-std=c11', '-O0', '-Wall', '-Wextra',
                                                    '-Werror', str(src), '-o', str(binary)],
                                                   capture_output=True, text=True, timeout=30)
                            self.assertEqual(build.returncode, 0, build.stderr)
                            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=5)
                            self.assertEqual((run.returncode, run.stdout), (0, '1 2 0\n'))


if __name__ == '__main__': unittest.main()
