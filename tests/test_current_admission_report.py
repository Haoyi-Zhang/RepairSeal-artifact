"""Current-runtime admission checks and explicit historical-receipt compatibility."""
import copy
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import report_admission_results as report

RETAINED_RESULTS = report.ROOT / "data/admission-journal"
EXPECTED_COUNTS = dict(requests=5, proof_direct_agreements=5,
                       approved=1, refuted=4, receiver_processes=28)


class HistoricalAdmissionReceiptCompatibility(unittest.TestCase):
    """Do not report a retained receipt as replayed under another receiver."""

    def test_retained_receipts_match_this_receiver_or_are_explicitly_skipped(self):
        try:
            counts = report.validate_current(RETAINED_RESULTS)
        except ValueError as error:
            if str(error) != "admission receiver implementation identity":
                raise
            self.skipTest(
                "retained admission receipts require their exact CPython 3.12.14 "
                "receiver identity; current-runtime controls run separately"
            )
        self.assertEqual(counts, EXPECTED_COUNTS)


class CurrentAdmissionEvidenceTests(unittest.TestCase):
    """Run every positive and negative check on evidence made by this runtime."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="repairseal-current-admission-tests-"
        )
        cls.results = Path(cls.temporary.name) / "evidence"
        command = [
            sys.executable,
            "-B",
            str(report.ROOT / "tests/admission_journal_study.py"),
            "--output",
            str(cls.results),
        ]
        completed = subprocess.run(
            command,
            cwd=report.ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if completed.returncode:
            raise RuntimeError(
                "fresh current-runtime admission study failed\n"
                + completed.stdout
                + completed.stderr
            )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_current_closed_journals_and_replayed_decisions(self):
        counts = report.validate_current(self.results)
        self.assertEqual(counts, EXPECTED_COUNTS)

    def test_source_change_cannot_relabel_old_evidence(self):
        original = Path.read_bytes
        changed = report.ROOT / "src/proof_dag_checker.py"
        with patch.object(
            Path,
            "read_bytes",
            lambda path: b"changed" if path == changed else original(path),
        ), self.assertRaisesRegex(ValueError, "stale admission source"):
            report.validate_current(self.results)

    def test_counts_are_derived_and_boolean_is_not_a_count(self):
        original = report.load
        summary = original(self.results / "summary.json")
        for value in (2, True):
            changed = copy.deepcopy(summary)
            changed["approved"] = value
            with self.subTest(value=value), patch.object(
                report,
                "load",
                lambda path: changed
                if path.name == "summary.json"
                else original(path),
            ), self.assertRaisesRegex(ValueError, "summary count"):
                report.validate_current(self.results)

    def test_wrong_receipt_identity_is_not_a_current_approval(self):
        original = report.load
        records = original(self.results / "records.json")
        changed = copy.deepcopy(records)
        changed["rows"][1]["proof"]["request_identity"] = "0" * 64
        with patch.object(
            report,
            "load",
            lambda path: changed if path.name == "records.json" else original(path),
        ), self.assertRaisesRegex(ValueError, "receipt identity"):
            report.validate_current(self.results)

    def test_old_receiver_identity_cannot_relabel_current_receipt(self):
        original = report.load
        records = original(self.results / "records.json")
        changed = copy.deepcopy(records)
        changed["rows"][1]["proof"]["receiver_identity"] = "0" * 64
        with patch.object(
            report,
            "load",
            lambda path: changed if path.name == "records.json" else original(path),
        ), self.assertRaisesRegex(ValueError, "receipt identity"):
            report.validate_current(self.results)

    def test_sql_approval_metadata_cannot_disagree_with_the_receipt_json(self):
        with tempfile.TemporaryDirectory(
            prefix="repairseal-journal-report-"
        ) as temporary:
            copied = Path(temporary) / "evidence"
            shutil.copytree(self.results, copied)
            database = sqlite3.connect(copied / "journals" / "original.sqlite")
            database.execute(
                "UPDATE receipts SET decision='ACCEPT' WHERE token='proof'"
            )
            database.commit()
            database.close()
            with self.assertRaisesRegex(ValueError, "journal metadata"):
                report.validate_current(copied)


if __name__ == "__main__":
    unittest.main()
