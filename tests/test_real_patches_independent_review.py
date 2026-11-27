"""Independent label reduction rejects malformed evidence and category drift."""
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments/real-patches/independent_review.py"
SPEC = importlib.util.spec_from_file_location("repairseal_independent_patch_review", PATH)
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class IndependentPatchReviewBoundaries(unittest.TestCase):
    def test_json_cannot_hide_duplicate_counts_or_nonfinite_values(self):
        for raw in ('{"count": 1, "count": 2}', '{"count": NaN}', '{"count": Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                review.decode(raw)

    def test_bool_and_float_values_cannot_impersonate_integer_counts(self):
        for replacement in (True, 1.0):
            self.assertFalse(review.exact_equal({"count": 1}, {"count": replacement}))
        self.assertTrue(review.exact_equal({"counts": [1, 2], "pass": True},
                                         {"counts": [1, 2], "pass": True}))

    def test_duplicate_execution_keys_are_not_silently_overwritten(self):
        with self.assertRaisesRegex(ValueError, "duplicate native key"):
            review.keyed([{"source": "a", "point": "p", "value": 0},
                          {"source": "a", "point": "p", "value": 1}],
                         ("source", "point"), "native")

    def test_wrong_outputs_on_previously_correct_inputs_are_preservation_failures(self):
        # u is undefined; r remains wrong where the original was wrong; p is a
        # regression; f is repaired. All three violation obligations must remain
        # visible even though one primary precedence label is displayed.
        result = review.reduction({"u", "r", "p", "f"}, {"p"},
                                  {"r", "p", "f"}, {"f"})
        self.assertEqual(result["labels"], ["definedness", "repair-region", "preservation"])
        self.assertEqual(result["violation_points"],
                         {"definedness": ["u"], "repair-region": ["r"], "preservation": ["p"]})
        self.assertEqual((result["repair_points"], result["preservation_points"]), (3, 1))
        with self.assertRaisesRegex(ValueError, "observation sets"):
            review.reduction({"p"}, set(), set(), {"p"})

    def test_reference_functions_cover_ties_order_and_signed_boundaries(self):
        self.assertEqual(review.mathematical_answer("median", [-(2**31), 2**31-1, 0]), 0)
        self.assertEqual(review.mathematical_answer("median", [2, 1, 2]), 2)
        self.assertEqual(review.mathematical_answer("smallest", [3, 2, -1, 0]), -1)
        with self.assertRaisesRegex(ValueError, "input contract"):
            review.mathematical_answer("median", [False, 1, 2])


if __name__ == "__main__":
    unittest.main()
