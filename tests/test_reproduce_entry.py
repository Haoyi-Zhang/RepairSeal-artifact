"""Protect scope reporting, process failure, and retained evidence at the entry point."""
from argparse import Namespace
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repairseal_reproduction_entry", ROOT / "reproduce.py")
entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entry)


def arguments(output, data, checks=None):
    return Namespace(output=output, data=data, checks=checks, archive=None, cbmc=None, witness_cbmc=None,
                     cpachecker=None, gcc=None, clang=None, library_dir=[], cpu=None,
                     jobs=1, step_timeout=2.0)


class ReproductionEntryTests(unittest.TestCase):
    def test_default_selection_includes_every_study_and_witness(self):
        self.assertEqual(entry.selected_checks(None), entry.CHECKS)
        self.assertIn("witness", entry.CHECKS)
        self.assertEqual(entry.CHECKS[entry.CHECKS.index("signed") + 1], "coverage")
        self.assertEqual(entry.CHECKS[entry.CHECKS.index("point-timing") + 1], "counter-overhead")
        self.assertEqual(entry.selected_checks(["point-timing", "analysis", "analysis"]),
                         ("analysis", "point-timing"))
        with self.assertRaises(ValueError):
            entry.selected_checks([])

    def test_existing_directory_and_symlink_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            kept = parent / "kept"; kept.mkdir()
            sentinel = kept / "evidence.json"; sentinel.write_text('{"retained": true}\n')
            for output in (kept, parent / "link"):
                if output != kept:
                    output.symlink_to(kept, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "existing evidence is preserved"):
                    entry.reserve_output(output)
                self.assertEqual(sentinel.read_text(), '{"retained": true}\n')
            inside = ROOT / "forbidden-reproduction-output"
            with self.assertRaisesRegex(ValueError, "outside artifact"):
                entry.reserve_output(inside)
            self.assertFalse(inside.exists())

    def test_missing_external_prerequisites_start_no_study(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            args = arguments(output, Path(temporary) / "missing-data")
            with patch.object(entry, "run_command", side_effect=AssertionError("no child may start")):
                code = entry.run(args)
            self.assertEqual(code, 2)
            report = json.loads((output / "reproduction.json").read_text())
            self.assertEqual(report["outcome"], "FAILED_PRECONDITION")
            self.assertEqual(report["scientific_studies_started"], 0)
            self.assertTrue(all(row["status"] == "NOT_RUN" for row in report["steps"]))
            self.assertFalse((output / "logs").exists())

    def test_failed_child_never_marks_later_study_or_overrides_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; (root / "tests").mkdir(parents=True)
            # An owned child writes an optimistic receipt and exits nonzero.
            # The entry must trust the process failure, not that receipt.
            child = root / "tests" / "reproduce_all.py"
            child.write_text('import argparse,json,pathlib\np=argparse.ArgumentParser();p.add_argument("--output");p.add_argument("--child-timeout");a=p.parse_args();d=pathlib.Path(a.output);d.mkdir();(d/"complete-reproduction.json").write_text(json.dumps({"outcome":"PASS_COMPLETE_REPRODUCTION"}));raise SystemExit(7)\n')
            args = arguments(base / "out", base / "data", ["functional", "demand"])
            with patch.object(entry, "preconditions", return_value=[]), \
                 patch.dict(entry.NEEDS, {"functional": set(), "demand": set()}):
                code = entry.run(args, root=root)
            self.assertEqual(code, 1)
            report = entry.load(args.output / "reproduction.json")
            state = {row["name"]: row for row in report["steps"]}
            self.assertEqual(report["outcome"], "FAILED")
            self.assertEqual(state["functional"]["status"], "FAILED")
            self.assertEqual(state["functional"]["returncode"], 7)
            self.assertEqual(state["demand"]["status"], "NOT_RUN")
            self.assertEqual(state["witness"]["status"], "NOT_REQUESTED")

    def test_selected_analysis_success_cannot_be_full_reproduction(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; root.mkdir()
            args = arguments(base / "out", base / "data", ["analysis"])
            def checked_records(_data, destination, _root, *, timeout):
                self.assertEqual(timeout, args.step_timeout)
                destination.mkdir()
                return {"outcome": "PASS_RETAINED_ANALYSIS", "fresh_receiving_calls": 0}
            with patch.object(entry, "preconditions", return_value=[]), \
                 patch.object(entry, "analyze_retained", side_effect=checked_records):
                code = entry.run(args, root=root)
            self.assertEqual(code, 0)
            report = entry.load(args.output / "reproduction.json")
            self.assertEqual(report["outcome"], "PASS_SELECTED_CHECKS")
            self.assertFalse(report["complete_selection"])
            self.assertEqual(next(row for row in report["steps"] if row["name"] == "witness")["status"], "NOT_REQUESTED")

    def test_process_timeout_terminates_the_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            marker = parent / "too-late"
            command = [sys.executable, "-c", 'import pathlib,time;time.sleep(2);pathlib.Path("too-late").write_text("bad")']
            with self.assertRaises(entry.ExecutionFailure) as caught:
                entry.run_command(command, parent, dict(os.environ), parent / "stdout", parent / "stderr", .05)
            self.assertTrue(caught.exception.timed_out)
            self.assertIsNotNone(caught.exception.returncode)
            self.assertFalse(marker.exists())

    def test_skipped_units_are_incomplete_not_passed(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            stdout, stderr = parent / "stdout", parent / "stderr"
            stdout.write_text("")
            stderr.write_text("Ran 3 tests in 0.01s\n\nOK (skipped=1)\n")
            with self.assertRaises(entry.Incomplete):
                entry.check_units(stdout, stderr, parent)
            stderr.write_text("Ran 0 tests in 0.00s\n\nOK\n")
            with self.assertRaises(ValueError):
                entry.check_units(stdout, stderr, parent)

    def test_fresh_upstream_outputs_are_selected_for_dependent_studies(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            args = arguments(base / "out", base / "data")
            args.archive = base / "archive.tar.gz"
            for kind in ("timing", "point-timing"):
                command = entry.command_for(kind, args, ("native", "signed", kind), args.output)
                self.assertEqual(command[command.index("--corpus") + 1], args.output / "source-programs/normalized-corpus.json")
                self.assertEqual(command[command.index("--prior") + 1], args.output / "signed-contract")
            command = entry.command_for("timing", args, ("timing",), args.output)
            self.assertEqual(command[command.index("--prior") + 1], args.data / "signed-contract")
            command = entry.command_for("coverage", args, ("native", "signed", "coverage"), args.output)
            self.assertEqual(command[command.index("--corpus") + 1], args.output / "source-programs/normalized-corpus.json")
            self.assertEqual(command[command.index("--reference") + 1], args.output / "signed-contract")
            command = entry.command_for("coverage", args, ("coverage",), args.output)
            self.assertEqual(command[command.index("--corpus") + 1], args.data / "source-programs/normalized-corpus.json")
            self.assertEqual(command[command.index("--reference") + 1], args.data / "signed-contract")
            command = entry.command_for("counter-overhead", args,
                                        ("native", "signed", "point-timing", "counter-overhead"), args.output)
            self.assertEqual(command[command.index("--corpus") + 1], args.output / "source-programs/normalized-corpus.json")
            self.assertEqual(command[command.index("--prior") + 1], args.output / "signed-contract")
            self.assertEqual(command[command.index("--point-prior") + 1], args.output / "point-demand")
            point = args.data / "point-demand/measurements"
            point.mkdir(parents=True)
            command = entry.command_for("counter-overhead", args, ("counter-overhead",), args.output)
            self.assertEqual(command[command.index("--prior") + 1], args.data / "signed-contract")
            self.assertEqual(command[command.index("--point-prior") + 1], point)

    def test_optimized_invocation_stops_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            result = subprocess.run([sys.executable, "-O", "-B", str(ROOT / "reproduce.py"),
                                     "--output", str(output), "--checks", "analysis"],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires enabled assertions", result.stderr)
            self.assertFalse(output.exists())

    def test_child_timeout_reaches_nested_orchestration_and_remains_bounded(self):
        import reproduce_all
        import reproduce_all_core
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            args = arguments(base / 'out', base / 'data', ['functional'])
            args.step_timeout = 17.5
            command = entry.command_for('functional', args, args.checks, args.output)
            self.assertEqual(command[command.index('--child-timeout') + 1], '17.5')
            args.output.mkdir()
            child_args = Namespace(output=args.output, child_timeout=17.5)
            stopped = subprocess.CompletedProcess([], 1, '', 'owned early stop')
            with patch.object(reproduce_all.subprocess, 'run', return_value=stopped) as invoked, \
                    self.assertRaises(SystemExit):
                reproduce_all._run(child_args)
            core_command = invoked.call_args.args[0]
            self.assertEqual(core_command[core_command.index('--child-timeout') + 1], '17.5')
            with self.assertRaises(subprocess.TimeoutExpired):
                reproduce_all_core.run([sys.executable, '-c', 'import time;time.sleep(1)'], .02)
            for invalid in (0, -1, float('inf'), float('nan')):
                with self.assertRaises(ValueError):
                    reproduce_all_core.run([sys.executable, '-c', 'raise AssertionError()'], invalid)

    def test_distinct_witness_producer_and_shared_fallback_are_probed_correctly(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; root.mkdir()
            for distinct in (False, True):
                args = arguments(base / str(distinct), base / "data", ["cbmc", "witness"])
                args.cbmc = base / "boolean-producer"
                args.witness_cbmc = base / "witness-producer" if distinct else None
                args.cpachecker = base / "cpachecker"
                args.gcc = base / "gcc"
                calls = []
                def startup_then_stop(command, _cwd, _env, stdout, stderr, _timeout):
                    calls.append(command)
                    if command[-1] != "--version":
                        raise entry.ExecutionFailure("owned stop after startup probes", 7)
                    stdout.write_text(command[0].name)
                    stderr.write_text("")
                    return 0
                with patch.object(entry, "preconditions", return_value=[]), \
                        patch.object(entry, "run_command", side_effect=startup_then_stop):
                    self.assertEqual(entry.run(args, root=root), 1)
                expected = args.witness_cbmc if distinct else args.cbmc
                boolean = entry.command_for("cbmc", args, args.checks, args.output, root)
                witness = entry.command_for("witness", args, args.checks, args.output, root)
                self.assertEqual(boolean[boolean.index("--cbmc") + 1], args.cbmc)
                self.assertEqual(witness[witness.index("--cbmc") + 1], expected)
                probes = [command[0] for command in calls if command[-1] == "--version"]
                self.assertEqual(probes.count(args.cbmc), 1)
                if distinct:
                    self.assertEqual(probes.count(args.witness_cbmc), 1)
                states = {row["tool"]: row for row in entry.load(args.output / "reproduction.json")["tool_probes"]}
                self.assertEqual(states["witness-cbmc"]["status"], "READY")
                self.assertEqual("shared_startup_probe" in states["witness-cbmc"], not distinct)

    def test_missing_witness_completion_scripts_stop_before_any_campaign(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; (root / "tests").mkdir(parents=True)
            (root / "tests/witness_interoperability.py").write_text("raise AssertionError('must not run')\n")
            args = arguments(base / "out", base / "data", ["witness"])
            args.cbmc = args.cpachecker = args.gcc = Path(sys.executable)
            (args.data / "natural-domains").mkdir(parents=True)
            (args.data / "natural-domains/requests.json").write_text("[]\n")
            with patch.object(entry, "run_command", side_effect=AssertionError("no child may start")):
                self.assertEqual(entry.run(args, root=root), 2)
            report = entry.load(args.output / "reproduction.json")
            for script in entry.WITNESS_FOLLOWUP_SCRIPTS:
                self.assertIn("missing witness completion check: tests/" + script, report["problems"])
            self.assertEqual(report["scientific_studies_started"], 0)

    def test_failed_witness_reconciliation_prevents_later_analysis_and_controls(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; (root / "tests").mkdir(parents=True)
            primary = root / "tests/witness_interoperability.py"
            primary.write_text(
                "import argparse,json,pathlib\n"
                "p=argparse.ArgumentParser();p.add_argument('--output');a,_=p.parse_known_args();d=pathlib.Path(a.output);d.mkdir()\n"
                "summary={'outcome':'COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES','source_inputs_and_tools_unchanged':True,'producer_disagreements':[],'direct_cpa_disagreements':[],'control_runs':18,'groups':{}}\n"
                "(d/'summary.json').write_text(json.dumps(summary));(d/'protocol.json').write_text(json.dumps({'planned_requests':804,'pilot_limit':None}));(d/'cases.json').write_text(json.dumps([{'index':i} for i in range(804)]))\n")
            reconciler = root / "tests/verify_witness_interoperability.py"
            reconciler.write_text(
                "import argparse,json,pathlib\n"
                "p=argparse.ArgumentParser();p.add_argument('--output');p.add_argument('--study');a=p.parse_args()\n"
                "pathlib.Path(a.output).write_text(json.dumps({'outcome':'PASS_RETAINED_WITNESS_RECORDS','requests':804,'checked':{'control_processes':18}}));raise SystemExit(9)\n")
            for name in ("analyze_witness_search.py", "witness_projection_controls.py"):
                (root / "tests" / name).write_text("raise AssertionError('later witness work must not start')\n")
            args = arguments(base / "out", base / "data", ["witness"])
            with patch.object(entry, "preconditions", return_value=[]), \
                    patch.dict(entry.NEEDS, {"witness": set()}):
                self.assertEqual(entry.run(args, root=root), 1)
            report = entry.load(args.output / "reproduction.json")
            row = next(row for row in report["steps"] if row["name"] == "witness")
            self.assertEqual(report["outcome"], "FAILED")
            self.assertEqual(row["status"], "FAILED")
            self.assertEqual(row["returncode"], 0)
            self.assertEqual(row["failed_followup"], "record-verification")
            self.assertEqual(row["followups"][0]["returncode"], 9)
            self.assertEqual([step["status"] for step in row["followups"]], ["FAILED", "NOT_RUN", "NOT_RUN", "NOT_RUN"])
            self.assertFalse((args.output / "witness-interoperability/product-equivalence.json").exists())
            self.assertFalse((args.output / "witness-interoperability/search-statistics.json").exists())
            self.assertFalse((args.output / "witness-input-controls").exists())
            self.assertTrue(report["source_unchanged_during_run"])

    def test_coverage_independent_process_failure_overrides_an_optimistic_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; (root / "tests").mkdir(parents=True)
            checker = root / "tests/verify_signed_coverage_study.py"
            checker.write_text(
                "import argparse,json,pathlib\n"
                "p=argparse.ArgumentParser();p.add_argument('--output');a,_=p.parse_known_args()\n"
                "pathlib.Path(a.output).write_text(json.dumps({'outcome':'PASS_INDEPENDENT_SIGNED_COVERAGE_RECOMPUTATION','combinations':739,'local_values':1}))\n"
                "raise SystemExit(6)\n")
            destination = base / "out"; destination.mkdir()
            with self.assertRaises(entry.ExecutionFailure) as failed:
                entry.verify_coverage_records(base / "study", base / "reference", destination, root, 2)
            self.assertEqual(failed.exception.returncode, 6)
            self.assertTrue((destination / "coverage-verification.stdout.log").exists())
            self.assertTrue((destination / "coverage-verification.json").exists())

    def test_product_followup_requires_every_product_and_literal_continuity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "products.json"
            result = {"outcome": "PASS_IDENTICAL_WITNESS_PRODUCTS", "requests": 804,
                      "identical_products": 804, "isolated_emitter_processes": 2, "unchanged_during_check": True}
            path.write_text(json.dumps(result))
            self.assertEqual(entry.validate_witness_followup("product-equivalence", path)["identical_products"], 804)
            for field, value in (("identical_products", 803), ("unchanged_during_check", False)):
                path.write_text(json.dumps({**result, field: value}))
                with self.assertRaises(ValueError):
                    entry.validate_witness_followup("product-equivalence", path)

    def test_missing_point_reference_record_stops_counter_campaign_before_archive_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; (root / "tests").mkdir(parents=True)
            for name in ("counter_overhead_study.py", "verify_counter_overhead_study.py"):
                (root / "tests" / name).write_text("raise AssertionError('must not run')\n")
            args = arguments(base / "out", base / "data", ["counter-overhead"])
            args.archive = base / "archive"; args.archive.write_bytes(b"owned archive fixture")
            corpus = args.data / "source-programs"; corpus.mkdir(parents=True)
            (corpus / "normalized-corpus.json").write_text(json.dumps({"archive_sha256": entry.file_identity(args.archive)}))
            signed = args.data / "signed-contract"; signed.mkdir()
            (signed / "summary.json").write_text(json.dumps({"records": {"requests.json": "unused in this precondition control"}}))
            (signed / "requests.json").write_text("[]\n")
            point = args.data / "point-demand/measurements"; point.mkdir(parents=True)
            (point / "summary.json").write_text(json.dumps({"records": {"work.json": "owned", "timings.jsonl": "absent"}}))
            (point / "work.json").write_text("[]\n")
            with patch.object(entry, "run_command", side_effect=AssertionError("no scientific child may start")):
                self.assertEqual(entry.run(args, root=root), 2)
            report = entry.load(args.output / "reproduction.json")
            self.assertEqual(report["scientific_studies_started"], 0)
            self.assertTrue(any("timings.jsonl" in problem for problem in report["problems"]))

    def test_failed_counter_verifier_keeps_the_primary_success_and_stops_later_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "artifact"; (root / "tests").mkdir(parents=True)
            primary = root / "tests/counter_overhead_study.py"
            primary.write_text(
                "import argparse,json,pathlib\n"
                "p=argparse.ArgumentParser();p.add_argument('--output');a,_=p.parse_known_args();d=pathlib.Path(a.output);d.mkdir()\n"
                "result={'outcome':'PASS_COUNTER_OVERHEAD_STUDY','requests':1478,'preflight_receiving_calls':7390,'timed_receiving_calls':73900,'source_inputs_unchanged':True,'canonical_disagreements':0,'value_trace_disagreements':0}\n"
                "(d/'summary.json').write_text(json.dumps(result))\n")
            (root / "tests/verify_counter_overhead_study.py").write_text(
                "import argparse,json,pathlib\n"
                "p=argparse.ArgumentParser();p.add_argument('--output');a,_=p.parse_known_args()\n"
                "pathlib.Path(a.output).write_text(json.dumps({'outcome':'PASS_INDEPENDENT_COUNTER_OVERHEAD_RECOMPUTATION','requests':1478,'preflight_receiving_calls':7390,'timed_receiving_calls':73900}))\n"
                "raise SystemExit(9)\n")
            args = arguments(base / "out", base / "data", ["counter-overhead", "headers"])
            with patch.object(entry, "preconditions", return_value=[]), \
                    patch.dict(entry.NEEDS, {"counter-overhead": set(), "headers": set()}):
                self.assertEqual(entry.run(args, root=root), 1)
            report = entry.load(args.output / "reproduction.json")
            states = {row["name"]: row for row in report["steps"]}
            self.assertEqual(states["counter-overhead"]["status"], "FAILED")
            self.assertEqual(states["counter-overhead"]["returncode"], 0)
            self.assertEqual(states["counter-overhead"]["failed_validation_process"]["returncode"], 9)
            self.assertEqual(states["headers"]["status"], "NOT_RUN")
            self.assertEqual(report["outcome"], "FAILED")


if __name__ == "__main__":
    unittest.main()
