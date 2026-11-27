"""The IntroClass adapter preserves a narrow shell and rejects substitutions."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("repairseal_intro_adapter", ROOT / "experiments/introclass-certificates/normalize.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class IntroClassAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "experiments/real-patches/sources/40a5a239d6478a964d11210129202ff413a64291e6290e8269048d2e4af8d4ec.c").read_bytes()

    def test_real_published_counterexample_survives_adaptation(self):
        normalized, mapping = adapter.normalize(self.raw, "median")
        admitted = adapter.bridge.admit_source(normalized.encode())
        result = adapter.bridge.evaluate(admitted, [-1, -1, -2])
        self.assertTrue(result.defined)
        self.assertEqual(result.value, "-2")
        self.assertEqual(mapping["argv_inputs"], [{"index": 1, "target": "a"}, {"index": 2, "target": "b"}, {"index": 3, "target": "c"}])

    def test_changed_macro_or_reordered_arguments_do_not_normalize(self):
        variants = [self.raw.replace(b"#define ANGELIX_OUTPUT(type, expr, id) expr", b"#define ANGELIX_OUTPUT(type, expr, id) 0"),
                    self.raw.replace(b"a = atoi(argv[1])", b"a = atoi(argv[2])"),
                    self.raw.replace(b"#include <stdio.h>", b"#include <stdio.h>\n#define a b")]
        for raw in variants:
            with self.subTest(raw=raw):
                with self.assertRaises(adapter.AdaptationError): adapter.normalize(raw, "median")

    def test_original_stdout_codec_does_not_ignore_added_or_missing_output(self):
        _normalized, mapping = adapter.normalize(self.raw, "median")
        self.assertEqual(adapter.decode_original(b"-2\n", mapping), "-2")
        for raw in [b"-2", b" -2\n", b"-2\nextra", b"-02\n", b"-0\n"]:
            with self.assertRaises(adapter.AdaptationError): adapter.decode_original(raw, mapping)

    def test_teacher_shell_is_exactly_bound(self):
        raw = (ROOT / "experiments/real-patches/sources/e805c04dbe96129bc40dcd1586aa6d9d70d4284544629202a47ce9eb51b4d50f.c").read_bytes()
        normalized, mapping = adapter.normalize(raw, "median", reference=True)
        original = b"Please enter 3 numbers separated by spaces > -1 is the median\n"
        self.assertEqual(adapter.decode_original(original, mapping), "-1")
        observed = adapter.bridge.evaluate(adapter.bridge.admit_source(normalized.encode()), [-1, -1, -2])
        self.assertEqual(observed.value, "-1")
        with self.assertRaises(adapter.AdaptationError):
            adapter.decode_original(original.replace(b"median", b"smallest"), mapping)

    def test_macro_expansion_preserves_the_unparenthesized_replacement(self):
        text, count = adapter._expand_output('2 * ANGELIX_OUTPUT(int, a + b, "stdout")')
        self.assertEqual(text, "2 * a + b")
        self.assertEqual(count, 1)

    def test_original_main_signature_is_not_silently_repaired(self):
        for raw in [self.raw.replace(b"int main", b"void main"),
                    self.raw.replace(b"int argc", b"float argc")]:
            with self.assertRaises(adapter.AdaptationError): adapter.normalize(raw, "median")


if __name__ == "__main__": unittest.main()
