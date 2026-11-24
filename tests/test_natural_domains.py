"""Independent domain and source-selection checks for the matched study."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import natural_domain_study as study
from proof_dag_checker import evaluate_topological


class NaturalDomainChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = json.loads(study.TEST_METADATA.read_text())
        study.validate_test_metadata(cls.metadata)
        cls.domains = {(row["case"], row["domain"]): row for row in study.domain_protocol(cls.metadata)}

    def test_real_heldout_omission_and_retained_repair_detection(self):
        heldout = self.domains[("4-A", "heldout-tests")]["axes"]
        repair = self.domains[("4-A", "repair-tests")]["axes"]
        expanded = self.domains[("4-A", "test-boundary-closure")]["axes"]
        self.assertEqual(len(heldout["w"]), 8)
        self.assertNotIn(2, heldout["w"])
        self.assertIn(2, repair["w"]); self.assertIn(2, expanded["w"])
        self.assertEqual(evaluate_topological(study.request("4-A", "original", heldout, 1))["status"], "ACCEPT")
        expected = {"obligation": "repair", "trace": [[0, 1]], "input": [2]}
        for domain in (repair, expanded):
            self.assertEqual(evaluate_topological(study.request("4-A", "original", domain, 1))["witness"], expected)
            self.assertEqual(evaluate_topological(study.request("4-A", "supplied", domain, 1))["status"], "ACCEPT")

    def test_complete_legal_range_is_disjoint_without_dropping_the_upper_tail(self):
        domain = self.domains[("4-A", "complete-legal")]
        parts = [part["w"] for part in domain["request_parts"]]
        self.assertEqual([len(part) for part in parts], [64, 36])
        self.assertEqual(parts[0] + parts[1], list(range(1, 101)))
        self.assertFalse(set(parts[0]) & set(parts[1]))
        self.assertTrue(domain["complete_legal_range"])
        self.assertFalse(any(row["complete_legal_range"] for key, row in self.domains.items() if key[0] == "84-A"))

    def test_test_slots_and_distinct_points_keep_different_denominators(self):
        slots = [row for row in self.metadata["rows"] if row["case"] == "84-A" and row["split"] == "repair"]
        self.assertEqual(len(slots), 3)
        self.assertEqual(sorted(row["scalar_input"] for row in slots), [2, 2, 4])
        self.assertEqual(self.domains[("84-A", "repair-tests")]["axes"], {"n": [2, 4]})
        boundary = self.domains[("84-A", "test-boundary-closure")]["axes"]["n"]
        self.assertTrue({2, 4, 99999998, 100000000}.issubset(boundary))
        self.assertTrue(all(value % 2 == 0 and 2 <= value <= 100000000 for value in boundary))

    def test_macro_boundary_budget_comes_from_legal_axis_extrema(self):
        low = self.domains[("CEIL_DIV", "low-range-grid")]["axes"]
        high = self.domains[("CEIL_DIV", "boundary-grid")]["axes"]
        self.assertEqual([len(axis) for axis in low.values()], [32, 32])
        self.assertEqual([len(axis) for axis in high.values()], [64, 64])
        self.assertEqual(high["m"][:32], list(range(32)))
        self.assertEqual(high["n"][:32], list(range(1, 33)))
        for axis in high.values(): self.assertEqual(axis[-32:], list(range(2**32 - 32, 2**32)))
        self.assertNotIn(0, high["n"])
        # A mathematical overflow boundary independent of any retained witness.
        point = {"m": [2**32 - 1], "n": [2]}
        self.assertEqual(evaluate_topological(study.request("CEIL_DIV", "original", point, 1))["status"], "REFUTED")
        self.assertEqual(evaluate_topological(study.request("CEIL_DIV", "supplied", point, 1))["status"], "ACCEPT")

    def test_metadata_rejects_wrong_source_or_expected_output_claim(self):
        changed = copy.deepcopy(self.metadata)
        changed["source_sha256"]["4-A"]["buggy"] = "0" * 64
        with self.assertRaises(ValueError): study.validate_test_metadata(changed)
        changed = copy.deepcopy(self.metadata)
        changed["rows"][0]["expected_matches_task_reference"] = False
        with self.assertRaises(ValueError): study.validate_test_metadata(changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
