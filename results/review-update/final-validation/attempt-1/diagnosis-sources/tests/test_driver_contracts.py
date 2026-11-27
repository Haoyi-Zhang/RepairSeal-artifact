"""Protect scientific comparisons and retained evidence at driver boundaries."""
from pathlib import Path
import hashlib
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from reproduce_all_core import compare_summary, compare_exact, scientific_summary
from scientific_driver import new_output_directory, new_output_file
import reproduce_all

DRIVERS = (
    "reproduce_all", "reproduce_all_core", "reproduce", "study", "structured_study", "regression",
    "null_control", "report", "pilot", "proof_dag_security", "holdout_differential",
)
DIRECTORY_DRIVERS = {"reproduce_all", "reproduce_all_core", "reproduce", "study", "structured_study",
                     "report", "holdout_differential"}


class ScientificDriverBoundaries(unittest.TestCase):
    def test_all_assertion_campaigns_refuse_both_optimized_modes_before_output(self):
        with tempfile.TemporaryDirectory(prefix="repairseal-round2-driver-") as temporary:
            for name in DRIVERS:
                for option in ("-O", "-OO"):
                    with self.subTest(driver=name, option=option):
                        output = Path(temporary) / (name + option)
                        process = subprocess.run(
                            [sys.executable, option, "-B", str(ROOT / "tests" / (name + ".py")),
                             "--output", str(output)], cwd=ROOT, capture_output=True,
                            text=True, timeout=15,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                        )
                        self.assertNotEqual(process.returncode, 0)
                        self.assertIn("requires enabled assertions", process.stderr)
                        self.assertFalse(output.exists())

    def test_cli_preserves_existing_evidence_before_starting_a_campaign(self):
        with tempfile.TemporaryDirectory(prefix="repairseal-round2-existing-") as temporary:
            for name in DRIVERS:
                with self.subTest(driver=name):
                    output = Path(temporary) / name
                    if name in DIRECTORY_DRIVERS:
                        output.mkdir(); sentinel = output / "receipt.json"
                    else:
                        sentinel = output
                    sentinel.write_bytes(b'{"outcome":"retained"}\n')
                    process = subprocess.run(
                        [sys.executable, "-B", str(ROOT / "tests" / (name + ".py")),
                         "--output", str(output)], cwd=ROOT, capture_output=True,
                        text=True, timeout=15,
                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                    )
                    self.assertNotEqual(process.returncode, 0)
                    self.assertIn("existing evidence is preserved", process.stderr)
                    self.assertEqual(sentinel.read_bytes(), b'{"outcome":"retained"}\n')
                    if name in DIRECTORY_DRIVERS:
                        self.assertEqual(list(output.iterdir()), [sentinel])

    def test_measurement_projection_is_schema_and_path_specific(self):
        expected = {
            "schema": "structured-study-v2", "oracle_disagreements": 0,
            "generated_at_utc": "old", "timing_ms": {"proof_check": 1.0},
            "peak_rss_kib": 100,
            "nested": {"wall_seconds": "scientific-value", "timing_ms": 7},
        }
        current = copy.deepcopy(expected)
        current.update(generated_at_utc="new", timing_ms={"proof_check": 2.0}, peak_rss_kib=200)
        compare_summary(expected, current, "documented measurement fields")
        self.assertEqual(expected["timing_ms"], {"proof_check": 1.0})
        for key, value in (("wall_seconds", "changed"), ("timing_ms", 8)):
            changed = copy.deepcopy(current); changed["nested"][key] = value
            with self.assertRaises(AssertionError):
                compare_summary(expected, changed, "nested evidence")
        unknown = {"schema": "future-schema", "wall_seconds": 3}
        self.assertEqual(scientific_summary(unknown), unknown)
        edge = {"schema": "edge-case-regression-v1", "left_deep_ast": {"isolated_wall_seconds": 3, "nodes": 65},
                "wall_seconds": "not-a-declared-measurement"}
        projected = scientific_summary(edge)
        self.assertEqual(projected["left_deep_ast"], {"nodes": 65})
        self.assertEqual(projected["wall_seconds"], edge["wall_seconds"])

    def test_scientific_comparison_distinguishes_json_numeric_types(self):
        expected = {"schema": "structured-study-v2", "oracle_disagreements": 0,
                    "witness": {"input": [1], "trace": [[0, 1]]}}
        for path, replacement in (("count", False), ("count", 0.0), ("input", True), ("trace", 1.0)):
            current = copy.deepcopy(expected)
            if path == "count": current["oracle_disagreements"] = replacement
            elif path == "input": current["witness"]["input"][0] = replacement
            else: current["witness"]["trace"][0][1] = replacement
            with self.subTest(path=path, replacement=replacement), self.assertRaises(AssertionError):
                compare_summary(expected, current, "typed evidence")
        compare_exact({"a": 1, "b": [False]}, {"b": [False], "a": 1}, "key order")
        with self.assertRaises(ValueError):
            compare_exact({"v": float("nan")}, {"v": float("nan")}, "non-finite evidence")

    def test_output_helpers_preserve_files_and_dangling_symlinks(self):
        with tempfile.TemporaryDirectory(prefix="repairseal-round2-output-") as temporary:
            root = Path(temporary); file = root / "receipt.json"; file.write_text("old")
            for function in (new_output_directory, new_output_file):
                with self.assertRaises(SystemExit): function(file)
            link = root / "link"; link.symlink_to(root / "not-created")
            for function in (new_output_directory, new_output_file):
                with self.assertRaises(SystemExit): function(link)
            self.assertTrue(link.is_symlink()); self.assertFalse((root / "not-created").exists())
            self.assertEqual(file.read_text(), "old")

    def test_later_gate_failure_replaces_an_early_core_success_status(self):
        with tempfile.TemporaryDirectory(prefix="repairseal-round2-failed-gate-") as temporary:
            output = Path(temporary) / "owned-output"
            def fail_after_core(args):
                (args.output / "complete-reproduction.json").write_text(
                    json.dumps({"outcome": "PASS_COMPLETE_REPRODUCTION", "core_count": 380}))
                raise RuntimeError("injected later gate failure")
            with patch.object(reproduce_all, "_run", fail_after_core), \
                    patch.object(sys, "argv", ["reproduce_all.py", "--output", str(output)]), \
                    self.assertRaisesRegex(RuntimeError, "later gate failure"):
                reproduce_all.main()
            receipt = json.loads((output / "complete-reproduction.json").read_text())
            self.assertEqual(receipt["outcome"], "FAILED_COMPLETE_REPRODUCTION")
            self.assertEqual(receipt["core_count"], 380)
            self.assertEqual(receipt["failure_type"], "RuntimeError")


    def test_contract_reconciliation_allows_only_verified_receiver_identity(self):
        retained = ROOT / "data/contract-study"
        with tempfile.TemporaryDirectory(prefix="repairseal-contract-reconcile-") as temporary:
            current = Path(temporary) / "current"
            current.mkdir()
            for name in ("protocol.json", "corpus-bindings.json", "decisions.json",
                         "transport.json", "summary.json"):
                (current / name).write_bytes((retained / name).read_bytes())

            protocol = json.loads((current / "protocol.json").read_text())
            paths = [*sorted((ROOT / "src").glob("*.py")),
                     ROOT / "tests/contract_comparison.py", ROOT / "tests/scientific_driver.py"]
            protocol["source_bindings"] = {
                path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in paths
            }
            (current / "protocol.json").write_text(
                json.dumps(protocol, sort_keys=True, indent=2) + "\n")

            source_path = str(ROOT / "src")
            sys.path.insert(0, source_path)
            try:
                from domain_transport import receiver_identity
                current_identity = receiver_identity()
            finally:
                sys.path.remove(source_path)
            transport = json.loads((current / "transport.json").read_text())
            for row in transport:
                row["receipt"]["receiver_identity"] = current_identity
            (current / "transport.json").write_text(
                json.dumps(transport, sort_keys=True, indent=2) + "\n")

            summary = json.loads((current / "summary.json").read_text())
            for name in ("protocol.json", "corpus-bindings.json", "decisions.json", "transport.json"):
                summary["records"][name] = hashlib.sha256((current / name).read_bytes()).hexdigest()
            (current / "summary.json").write_text(
                json.dumps(summary, sort_keys=True, indent=2) + "\n")

            result = reproduce_all.compare_contract_study(ROOT, retained, current)
            self.assertTrue(result["current_receiver_identity_exact"])
            self.assertTrue(result["transport_scientific_fields_exact"])

            transport[0]["receipt"]["checked_cells"] += 1
            (current / "transport.json").write_text(
                json.dumps(transport, sort_keys=True, indent=2) + "\n")
            summary["records"]["transport.json"] = hashlib.sha256(
                (current / "transport.json").read_bytes()).hexdigest()
            (current / "summary.json").write_text(
                json.dumps(summary, sort_keys=True, indent=2) + "\n")
            with self.assertRaisesRegex(AssertionError, "transport scientific fields"):
                reproduce_all.compare_contract_study(ROOT, retained, current)

    def test_empty_test_discovery_is_not_conformance_evidence(self):
        with tempfile.TemporaryDirectory(prefix="repairseal-round2-no-tests-") as temporary:
            root = Path(temporary); (root / "tests").mkdir()
            command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_missing.py"]
            with self.assertRaisesRegex(RuntimeError, "required conformance test"):
                reproduce_all.run_check(root, command, 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
