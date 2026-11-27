"""Negative controls for the separate O0 witness path executor."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "repairseal_independent_definedness",
    ROOT / "experiments/real-patches/independent_definedness.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class IndependentDefinednessWitnessTests(unittest.TestCase):
    def source(self, declaration="int m;", extra=""):
        return ("int main(int argc, char *argv[]) { int a, b; " + declaration +
                'a = atoi(argv[1]); b = atoi(argv[2]); if (a > b) m = a; ' + extra +
                'printf("%d\\n", m); return 0; }').encode()

    def test_missing_assignment_and_taken_assignment_have_different_outcomes(self):
        fault = review.execute_witness(self.source(), [0, 1])
        self.assertTrue(fault["uninitialized_read"])
        self.assertEqual(fault["variable"], "m")
        self.assertFalse(fault["branches"][0]["taken"])
        self.assertNotIn("m", fault["assigned_values_before_fault"])
        self.assertFalse(review.execute_witness(self.source(), [2, 1])["uninitialized_read"])

    def test_explicit_initialization_invalidates_an_uninitialized_read_claim(self):
        self.assertFalse(review.execute_witness(self.source("int m = 0;"), [0, 1])["uninitialized_read"])

    def test_unreachable_unsupported_constructs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unreviewed control flow"):
            review.execute_witness(self.source(extra="if (0) { while (a) { a = 0; } } "), [0, 1])

    def test_bool_inputs_and_unmodeled_arithmetic_cannot_create_proofs(self):
        with self.assertRaisesRegex(ValueError, "int32 witness input"):
            review.execute_witness(self.source(), [False, 1])
        with self.assertRaisesRegex(ValueError, "unsupported witness operator"):
            review.execute_witness(self.source(extra="m = a / b; "), [0, 1])


if __name__ == "__main__":
    unittest.main()
