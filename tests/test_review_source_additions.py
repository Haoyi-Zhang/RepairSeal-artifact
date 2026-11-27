"""A declared new receiver cannot open the old source gate to arbitrary files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import reproduce_all
from domain_transport import receiver_identity


class ReviewSourceAdditionTests(unittest.TestCase):
    def reconcile(self, edit=None):
        retained = ROOT / "data/contract-study"
        with tempfile.TemporaryDirectory(prefix="repairseal-review-source-gate-") as directory:
            root = Path(directory)
            for folder in ("src", "tests", "current"):
                (root / folder).mkdir()
            for path in (ROOT / "src").glob("*.py"):
                shutil.copyfile(path, root / "src" / path.name)
            for name in ("contract_comparison.py", "scientific_driver.py"):
                shutil.copyfile(ROOT / "tests" / name, root / "tests" / name)
            if edit:
                edit(root)
            current = root / "current"
            for name in ("protocol.json", "corpus-bindings.json", "decisions.json", "transport.json", "summary.json"):
                shutil.copyfile(retained / name, current / name)
            protocol = json.loads((current / "protocol.json").read_text())
            paths = [*sorted((root / "src").glob("*.py")), root / "tests/contract_comparison.py", root / "tests/scientific_driver.py"]
            protocol["source_bindings"] = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            (current / "protocol.json").write_text(json.dumps(protocol, sort_keys=True) + "\n")
            transport = json.loads((current / "transport.json").read_text())
            for row in transport:
                row["receipt"]["receiver_identity"] = receiver_identity()
            (current / "transport.json").write_text(json.dumps(transport, sort_keys=True) + "\n")
            summary = json.loads((current / "summary.json").read_text())
            for name in summary["records"]:
                summary["records"][name] = hashlib.sha256((current / name).read_bytes()).hexdigest()
            (current / "summary.json").write_text(json.dumps(summary, sort_keys=True) + "\n")
            return reproduce_all.compare_contract_study(root, retained, current)

    def test_exact_declared_new_module_preserves_old_scientific_fields(self):
        result = self.reconcile()
        self.assertTrue(result["historical_bindings_unchanged"])
        self.assertTrue(result["all_other_protocol_records_and_summary_fields_exact"])
        self.assertEqual(result["added_source_bindings"]["src/int32_refutation.py"],
                         reproduce_all.REVIEW_SOURCE_ADDITIONS["src/int32_refutation.py"])

    def test_unknown_added_module_is_rejected_after_all_receipts_are_rehashed(self):
        with self.assertRaisesRegex(AssertionError, "declared round-3 and review source additions"):
            self.reconcile(lambda root: (root / "src/unregistered_module.py").write_text("x = 1\n"))

    def test_changed_declared_module_is_rejected_after_all_receipts_are_rehashed(self):
        with self.assertRaisesRegex(AssertionError, "exact review source addition"):
            self.reconcile(lambda root: (root / "src/int32_refutation.py").write_text("# altered receiver\n"))

    def test_changed_historical_module_is_still_rejected(self):
        with self.assertRaisesRegex(AssertionError, "unchanged historical source"):
            self.reconcile(lambda root: (root / "src/proof_dag_checker.py").write_text("# changed historical source\n"))


if __name__ == "__main__":
    unittest.main()
