"""Boundaries of the separately derived normalization reviewer."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "repairseal_independent_introclass_review",
    ROOT / "experiments/introclass-certificates/independent_review.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class IndependentNormalizationReviewTests(unittest.TestCase):
    def test_real_test_passing_candidate_has_independently_derived_counterexample(self):
        candidate = review.CASE_SOURCES["apr-043"][2]
        self.assertEqual(review.model(candidate, [-1, -1, -2]), ("-2", [[0, 0], [1, 0]]))
        self.assertEqual(review.model(review.REFERENCES["median"], [-1, -1, -2])[0], "-1")
        with self.assertRaisesRegex(ValueError, "no independently reviewed"):
            review.model("0" * 64, [-1, -1, -2])

    def test_ast_comparison_detects_computation_changes_and_input_permutations(self):
        raw = b'''int main(int argc, char *argv[]) {
          int a, b, c;
          a = atoi(argv[1]); b = atoi(argv[2]); c = atoi(argv[3]);
          if (a < b) printf("%d\\n", a); else printf("%d\\n", b);
          return 0;
        }'''
        normalized = b'''int main(void) {
          int a, b, c;
          scanf("%d", &a); scanf("%d", &b); scanf("%d", &c);
          if (a < b) printf("%d\\n", a); else printf("%d\\n", b);
          return 0;
        }'''
        original, _ = review.parse_for_review(raw)
        shape, _ = review.structural_signature(original, "median", True, False)
        admitted, _ = review.parse_for_review(normalized)
        target, _ = review.structural_signature(admitted, "median", False, False)
        self.assertTrue(review.exact(shape, target))
        for changed in (normalized.replace(b"a < b", b"b < a"),
                        normalized.replace(b'&a); scanf("%d", &b', b'&b); scanf("%d", &a')):
            tree, _ = review.parse_for_review(changed)
            altered, _ = review.structural_signature(tree, "median", False, False)
            self.assertFalse(review.exact(shape, altered))

    def test_generalized_macro_or_main_return_type_cannot_enter_fixed_review(self):
        bad_macro = b'''int main(void) { int a; printf("%d\\n", ANGELIX_OUTPUT(int, a+1, "stdout")); return 0; }'''
        with self.assertRaisesRegex(ValueError, "simple identity macro"):
            review.parse_for_review(bad_macro)
        with self.assertRaisesRegex(ValueError, "main return type"):
            review.parse_for_review(b"void main(void) { return; }")


if __name__ == "__main__":
    unittest.main()
