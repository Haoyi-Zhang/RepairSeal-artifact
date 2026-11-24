"""Retained native records must support their advertised populations and values."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

import verify_natural_domain_evidence as evidence

RESULTS = Path(__file__).resolve().parents[1] / "data/natural-domains"


class NativeEvidenceChecks(unittest.TestCase):
    def test_current_native_observations_reconcile(self):
        result = evidence.verify(RESULTS)
        self.assertEqual(result["codeflaws_rows"], 448)
        self.assertEqual(result["macro_rows"], 8192)
        self.assertFalse(result["external_sources_executed_by_this_check"])

    def test_wrong_native_value_is_not_hidden_by_agreement_flag(self):
        original = evidence.load
        rows = original(RESULTS / "codeflaws-native-observations.json")
        changed = copy.deepcopy(rows); changed[0]["observed"] += 1
        with patch.object(evidence, "load", lambda path: changed if path.name == "codeflaws-native-observations.json" else original(path)), \
                self.assertRaisesRegex(ValueError, "observation differs"):
            evidence.verify(RESULTS)

    def test_missing_or_duplicate_observation_changes_the_population(self):
        original = evidence.load
        rows = original(RESULTS / "macro-native-observations.json")
        for changed in (rows[:-1], rows[:-1] + [rows[0]]):
            with self.subTest(kind="missing" if len(changed) < len(rows) else "duplicate"), \
                    patch.object(evidence, "load", lambda path: changed if path.name == "macro-native-observations.json" else original(path)), \
                    self.assertRaisesRegex(ValueError, "observations|coverage"):
                evidence.verify(RESULTS)

    def test_summary_counts_and_native_flags_keep_json_types(self):
        original = evidence.load
        summary = original(RESULTS / "summary.json")
        for key, value in (("compilers", 2.0), ("native_branch_traces_measured", 0)):
            changed = copy.deepcopy(summary); changed["native"][key] = value
            with self.subTest(key=key), \
                    patch.object(evidence, "load", lambda path: changed if path.name == "summary.json" else original(path)), \
                    self.assertRaisesRegex(ValueError, "summary count"):
                evidence.verify(RESULTS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
