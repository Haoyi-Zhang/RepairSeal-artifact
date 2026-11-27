"""Adversarial checks for the restricted exact order-type analysis."""
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1] / "experiments/deep-review/real-validation"
spec = importlib.util.spec_from_file_location("weak_order_profile", HERE / "order_types.py")
order = importlib.util.module_from_spec(spec)
spec.loader.exec_module(order)

SOURCE = b'''#include <stdio.h>
int main(void) {
  int a; int b; int r;
  scanf("%d%d", &a, &b);
  if (a < b) r = a; else r = b;
  printf("%d\\n", r);
  return 0;
}
'''


class WeakOrderValidation(unittest.TestCase):
    def test_all_weak_orders_include_ties_and_nonadjacent_equalities(self):
        self.assertEqual([len(order.patterns(n)) for n in range(1, 5)], [1, 3, 13, 75])
        for n in (3, 4):
            observed = {order.rank_pattern(p) for p in product((-9, -2, 0, 8, 19), repeat=n)}
            self.assertEqual(observed, set(order.patterns(n)))
        self.assertIn((1, 0, 1, 0), order.patterns(4))

    def test_all_boundary_embeddings_preserve_exact_order(self):
        for n in (3, 4):
            for p in order.patterns(n):
                for embedding in order.EMBEDDINGS:
                    concrete = order.embed(p, embedding)
                    self.assertEqual(order.rank_pattern(concrete), p)
                    self.assertTrue(all(order.INT_MIN <= x <= order.INT_MAX for x in concrete))

    def test_input_copy_output_and_equal_case_are_preserved(self):
        program = order.Program(SOURCE)
        for p in order.patterns(2):
            row = program.evaluate(p)
            self.assertTrue(row["defined"])
            self.assertEqual(row["output_rank"], min(p))
        self.assertEqual(program.evaluate((0, 0))["selected_input"], 1)

    def test_arithmetic_constants_and_hidden_bad_branches_are_rejected(self):
        mutations = [SOURCE.replace(b"r = a", b"r = a + b"),
                     SOURCE.replace(b"r = a", b"r = 0"),
                     SOURCE.replace(b"a < b", b"a < 3"),
                     SOURCE.replace(b"return 0;", b"if (a != a) r = a + b; return 0;")]
        for raw in mutations:
            with self.subTest(raw=raw):
                with self.assertRaises(order.OutsideProfile): order.Program(raw)

    def test_ignored_attributes_and_qualified_void_are_rejected(self):
        mutations = [SOURCE.replace(b"int a;", b"_Alignas(8) int a;"),
                     SOURCE.replace(b"int a;", b"volatile int a;"),
                     SOURCE.replace(b"int a;", b"static int a;"),
                     SOURCE.replace(b"main(void)", b"main(const void)"),
                     SOURCE.replace(b"int a;", b"_Atomic int a;")]
        for raw in mutations:
            with self.subTest(raw=raw):
                with self.assertRaises(order.OutsideProfile): order.Program(raw)

    def test_uninitialized_read_is_a_class_failure(self):
        program = order.Program(SOURCE.replace(b"else r = b;", b"else ;"))
        self.assertTrue(program.evaluate((0, 1))["defined"])
        failed = program.evaluate((1, 0))
        self.assertFalse(failed["defined"])
        self.assertIn("undefined read", failed["error"])

    def test_multi_output_and_missing_output_are_class_failures(self):
        raw = SOURCE.replace(b'printf("%d\\n", r);', b'printf("%d\\n", r); printf("%d\\n", r);')
        self.assertFalse(order.Program(raw).evaluate((0, 1))["defined"])
        raw = SOURCE.replace(b'printf("%d\\n", r);', b';')
        self.assertFalse(order.Program(raw).evaluate((0, 1))["defined"])

    def test_alias_input_nested_scope_and_early_return_are_rejected(self):
        mutations = [SOURCE.replace(b"&a, &b", b"&a, &a"),
                     SOURCE.replace(b"int r;", b"{ int r; }"),
                     SOURCE.replace(b"r = a;", b"return 0;")]
        for raw in mutations:
            with self.assertRaises(order.OutsideProfile): order.Program(raw)

    def test_unknown_io_or_computation_calls_are_rejected(self):
        mutations = [SOURCE.replace(b"r = a;", b"r = abs(a);"),
                     SOURCE.replace(b'printf("%d\\n", r)', b'puts("x")'),
                     SOURCE.replace(b'printf("%d\\n", r)', b'printf("value=%d\\n", r)')]
        for raw in mutations:
            with self.assertRaises(order.OutsideProfile): order.Program(raw)

    def test_out_of_range_bool_and_noncanonical_ranks_are_rejected(self):
        for point in [(True, 0), (2**31, 0), (-2**31-1, 0)]:
            with self.assertRaises(order.OutsideProfile): order.rank_pattern(point)
        with self.assertRaises(order.OutsideProfile): order.Program(SOURCE).evaluate((0, 2))

    def test_header_macros_and_implementation_reserved_identifiers_are_rejected(self):
        for name in (b"EOF", b"BUFSIZ", b"stdin", b"stdout", b"stderr", b"_private", b"__implementation"):
            raw = SOURCE.replace(b"int r;", b"int " + name + b";").replace(b"r =", name + b" =").replace(b'", r)', b'", ' + name + b')')
            with self.subTest(name=name):
                with self.assertRaises(order.OutsideProfile): order.Program(raw)

    def test_c_escape_spelling_is_not_decoded_as_a_python_literal(self):
        for old, new in ((b'"%d\\n"', b'"\\x25d\\n"'), (b'"%d%d"', b'"\\x25d%d"'),
                         (b'"%d\\n"', b'"%d\\012"')):
            with self.subTest(new=new):
                with self.assertRaises(order.OutsideProfile): order.Program(SOURCE.replace(old, new))


class RetainedOrderStudy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = HERE / "records"
        if not (cls.data / "summary.json").exists():
            raise unittest.SkipTest("fresh native records not yet produced")
        sys.path.insert(0, str(HERE))
        spec = importlib.util.spec_from_file_location("weak_order_run_verifier", HERE / "run.py")
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def mutated(self, filename, transform):
        directory = tempfile.TemporaryDirectory(prefix="verify-negative-", dir=HERE)
        self.addCleanup(directory.cleanup)
        target = Path(directory.name)
        for source in self.data.iterdir():
            if source.name != filename:
                (target/source.name).symlink_to(source, target_is_directory=source.is_dir())
        (target/filename).write_text(transform((self.data/filename).read_text()))
        return target

    def test_retained_campaign_recomputes_exactly(self):
        result = self.runner.verify(self.data)
        self.assertEqual(result["native_process_executions"], 10602)
        self.assertEqual(result["distinct_candidate_output_behaviors"], 2)

    def test_missing_process_is_rejected(self):
        target = self.mutated("native.jsonl", lambda text: text.split("\n", 1)[1])
        with self.assertRaisesRegex(ValueError, "execution closure"): self.runner.verify(target)

    def test_duplicate_process_is_rejected(self):
        target = self.mutated("native.jsonl", lambda text: text + text.splitlines()[0] + "\n")
        with self.assertRaisesRegex(ValueError, "coverage or duplicate"): self.runner.verify(target)

    def test_resealed_wrong_output_is_rejected(self):
        def transform(text):
            first, rest = text.split("\n", 1)
            row = json.loads(first)
            row["process"]["stdout"] = "123456\n"
            row["process"]["stdout_sha256"] = self.runner.digest(b"123456\n")
            row["expected_stdout"] = "123456\n"
            return json.dumps(row) + "\n" + rest
        target = self.mutated("native.jsonl", transform)
        with self.assertRaisesRegex(ValueError, "semantic/codec"): self.runner.verify(target)

    def test_relabelled_compiler_treatment_is_rejected(self):
        def transform(text):
            rows = json.loads(text)
            rows[0]["process"]["command"] = [x.replace("-O0", "-O3") for x in rows[0]["process"]["command"]]
            return json.dumps(rows)
        target = self.mutated("compilations.json", transform)
        with self.assertRaisesRegex(ValueError, "command treatment"): self.runner.verify(target)


if __name__ == "__main__": unittest.main()
