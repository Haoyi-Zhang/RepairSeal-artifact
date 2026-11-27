"""Negative controls for the new result gate, separate from study semantics."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("review_update_gate_tests", ROOT / "verify_expected_results.py")
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
UPDATE_SPEC = importlib.util.spec_from_file_location("review_update_driver_tests", ROOT / "verify_update_results.py")
UPDATE = importlib.util.module_from_spec(UPDATE_SPEC)
UPDATE_SPEC.loader.exec_module(UPDATE)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReviewUpdateGateTests(unittest.TestCase):
    def gate(self, mutation=None, result_status="PASS"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            driver = root / "verify_update_results.py"
            driver.write_text("STUDIES = {'fixture': 'verifier.py'}\n"
                              "def recompute_study(name, root):\n"
                              f"    return {{'status': {result_status!r}, 'errors': [], 'recomputed': {{'patches': 3}}}}\n")
            for name in ("summary.json", "manifest.json", "verifier.py"):
                (root / name).write_text("{}\n")
            entry = {"summary_file": "summary.json", "summary_sha256": digest(root / "summary.json"),
                     "inventory_file": "manifest.json", "inventory_sha256": digest(root / "manifest.json"),
                     "verifier_file": "verifier.py", "verifier_sha256": digest(root / "verifier.py"),
                     "fields": {"patches": 3}}
            expected = {"review_update_driver_sha256": digest(driver), "review_update": {"fixture": entry}}
            if mutation:
                mutation(root, expected)
            audit = GATE.Audit()
            with mock.patch.object(GATE, "ARTIFACT", root), mock.patch.object(GATE, "EXPECTED_PATH", root / "expected-results.json"):
                GATE.verify_update(expected, audit)
            return audit.failures

    def test_consistent_result_and_bindings_pass(self):
        self.assertEqual(self.gate(), [])

    def test_altered_receipt_is_rejected_even_when_numbers_match(self):
        failed = self.gate(lambda root, _expected: (root / "manifest.json").write_text('{"edited": true}\n'))
        self.assertIn("update:fixture:inventory-hash", {row["name"] for row in failed})

    def test_forged_summary_number_cannot_replace_recomputation(self):
        def change(_root, expected):
            expected["review_update"]["fixture"]["fields"]["patches"] = 4
        failed = self.gate(change)
        self.assertIn("update:fixture:patches", {row["name"] for row in failed})

    def test_failed_study_and_missing_study_are_rejected(self):
        failed = self.gate(result_status="FAIL")
        self.assertIn("update:fixture:offline-replay", {row["name"] for row in failed})
        failed = self.gate(lambda _root, expected: expected["review_update"].clear())
        self.assertIn("update:study-coverage", {row["name"] for row in failed})

    def test_empty_study_selection_is_not_success(self):
        with mock.patch.object(UPDATE, "load_module") as loader:
            result = UPDATE.verify(studies=[])
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["errors"])
        loader.assert_not_called()

    def test_explicit_scale_failure_is_not_discarded(self):
        failed_module = SimpleNamespace(verify=lambda _path: {"outcome": "FAIL", "errors": ["probe failure"]},
                                        compute=lambda **_kwargs: {"summary.json": b"{}"})
        with mock.patch.object(UPDATE, "load_module", return_value=failed_module):
            result = UPDATE.verify(studies=["domain_scale"])
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["studies"]["domain_scale"]["status"], "FAIL")
        self.assertIn("probe failure", result["studies"]["domain_scale"]["errors"][0])


if __name__ == "__main__":
    unittest.main()
