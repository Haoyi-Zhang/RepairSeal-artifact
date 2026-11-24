"""Contracts for the evaluator-facing artifact entry point."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(loaded)
    return loaded


verifier = module("repairseal_expected_verifier", ROOT / "verify_expected_results.py")
evaluator = module("repairseal_evaluator", ROOT / "evaluator.py")


class ExpectedResultAuditTests(unittest.TestCase):
    def test_exact_packaged_fields_pass(self):
        expected = verifier.load(ROOT / "expected-results.json")
        audit = verifier.Audit()
        verifier.verify_packaged(expected, audit)
        self.assertEqual(audit.failures, [])
        self.assertGreaterEqual(len(audit.records), 30)

    def test_a_wrong_field_is_a_failure_not_a_text_hit(self):
        audit = verifier.Audit()
        audit.check("synthetic", 4, 5, ROOT / "expected-results.json",
                    "synthetic", "test")
        self.assertEqual(len(audit.failures), 1)
        self.assertEqual(audit.failures[0]["actual"], 4)

    def test_expected_results_distinguish_provenance(self):
        expected = json.loads((ROOT / "expected-results.json").read_text())
        self.assertIn("fresh_current", expected)
        self.assertIn("retained_recomputed", expected)
        self.assertIn("external_only", expected)
        self.assertFalse(expected["external_only"]["upstream_vulkan"]["bundled"])


class EvaluatorContractTests(unittest.TestCase):
    def test_external_absence_starts_no_scientific_study(self):
        parser = evaluator.parser()
        args = parser.parse_args(["external"])
        result = evaluator.external_preconditions(args)
        self.assertEqual(result["status"], "FAILED_PRECONDITION")
        self.assertEqual(result["scientific_studies_started"], 0)

    def test_shell_entry_point_is_executable(self):
        path = ROOT / "evaluate.sh"
        self.assertTrue(path.is_file())
        self.assertTrue(path.stat().st_mode & 0o111)

    def test_new_output_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "new path"):
                evaluator.reserve(Path(directory))


if __name__ == "__main__":
    unittest.main()
