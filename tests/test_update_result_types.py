"""Result contracts must not silently accept bool-valued counts."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "repairseal_review_result_types", Path(__file__).resolve().parents[1] / "verify_expected_results.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class UpdateResultTypes(unittest.TestCase):
    def test_boolean_does_not_satisfy_an_integer_count(self):
        self.assertFalse(verifier.equal(True, 1))
        self.assertFalse(verifier.equal(False, 0))
        self.assertFalse(verifier.equal(1, True))
        self.assertFalse(verifier.equal(0, False))
        self.assertFalse(verifier.equal(True, 1.0))

    def test_nested_expected_statistics_preserve_json_types(self):
        self.assertFalse(verifier.equal({"counts": [True]}, {"counts": [1]}))
        self.assertFalse(verifier.equal({"counts": [1.0]}, {"counts": [1]}))
        self.assertTrue(verifier.equal({"counts": [1], "pass": True}, {"counts": [1], "pass": True}))

    def test_existing_timing_tolerance_remains_available(self):
        self.assertTrue(verifier.equal(1.0 + 1e-13, 1.0))
        self.assertFalse(verifier.equal(1.1, 1.0))
        self.assertFalse(verifier.equal(float("nan"), 1.0))


if __name__ == "__main__":
    unittest.main()
