"""Guard secondary analysis against ambiguous or mismatched external records."""
import unittest
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from analyze_witness_search import command_profile, extract, extract_owned, started_analyses
from verify_witness_interoperability import ARMS, Q, check_arm_inventory, check_path_adapter, envelope, resource_resume_plan


class WitnessSearchStatisticsTests(unittest.TestCase):
    def test_final_resource_phase_cannot_lose_its_protocol(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(AssertionError, "protocol is missing"):
                resource_resume_plan(root, {}, {}, {"execution": {"resource_resume_protocol": "resource-resume-protocol.json", "resource_interruptions": 1}})
            self.assertIsNone(resource_resume_plan(root, {}, {}, None))
            self.assertIsNone(resource_resume_plan(root, {}, {}, {}))

    def test_started_analysis_comes_from_execution_events(self):
        text = ("Last algorithm used: concurrency.properties\n"
                "Loading analysis 1 from file /tool/config/violation.properties ... (RestartAlgorithm.run, INFO)\n"
                "Starting analysis 1 ... (RestartAlgorithm.run, INFO)\n"
                "Ignoring restart configuration '/tool/config/concurrency.properties' because condition did not match.\n")
        sequence, issues = started_analyses(text)
        self.assertEqual(sequence, [{"analysis": 1, "configuration": "/tool/config/violation.properties"}])
        self.assertEqual(issues, [])
        _, issues = started_analyses(text + "Starting analysis 1 ... (RestartAlgorithm.run, INFO)\n")
        self.assertTrue(issues)

    def test_abstraction_computation_owner_is_value_analysis(self):
        values, issues, owners = extract_owned("ValueAnalysisPrecisionAdjustment statistics\n----\n"
                                              "Number of abstraction computations: 56\n")
        self.assertEqual(values["abstraction_computations"], 56)
        self.assertEqual(owners["abstraction_computations"], ["ValueAnalysisPrecisionAdjustment"])
        values, issues, _ = extract_owned("PredicateCPA statistics\n----\nNumber of abstraction computations: 56\n")
        self.assertNotIn("abstraction_computations", values)
        self.assertIn("abstraction_computations", issues)

    def test_adapter_audit_preserves_unmatched_assumptions_and_scope(self):
        before = ET.fromstring('<graph xmlns="http://graphml.graphdrawing.org/xmlns">'
                               '<edge source="a" target="b"><data key="assumption">return_value_f = 2u;</data>'
                               '<data key="assumption.scope">main</data></edge>'
                               '<edge source="b" target="c"><data key="assumption">x = 7u;</data></edge></graph>')
        after = copy.deepcopy(before)
        edge = after.find(Q + "edge")
        edge.find(Q + "data").text = "\\result == 2u;"
        ET.SubElement(edge, Q + "data", {"key": "assumption.resultfunction"}).text = "f"
        self.assertEqual(len(check_path_adapter(before, after, "standard", "")), 1)
        changed = copy.deepcopy(after)
        changed.findall(Q + "edge")[1].find(Q + "data").text = "x = 8u;"
        with self.assertRaisesRegex(AssertionError, "undeclared"):
            check_path_adapter(before, changed, "standard", "")
        changed = copy.deepcopy(after)
        changed.find(Q + "edge").findall(Q + "data")[1].text = "f"
        with self.assertRaisesRegex(AssertionError, "undeclared"):
            check_path_adapter(before, changed, "standard", "")

    def test_adapter_audit_leaves_ambiguous_call_sites_unchanged(self):
        source = ("unsigned f(unsigned x) { return x; }\nint main(void) {\n"
                  "unsigned a=f(1u), b=f(2u);\nunsigned c=f(f(1u));\n"
                  "unsigned d=f(3u);\nreturn 0;\n}\n")
        before = ET.Element(Q + "graph")
        for line in (3, 4, 5):
            edge = ET.SubElement(before, Q + "edge", {"source": str(line), "target": str(line + 1)})
            for key, value in (("startline", str(line)), ("assumption", "\\result = 3u;"),
                               ("assumption.resultfunction", "main"), ("originfile", "program.c")):
                ET.SubElement(edge, Q + "data", {"key": key}).text = value
        after = copy.deepcopy(before)
        fields = after.findall(Q + "edge")[-1].findall(Q + "data")
        fields[1].text = "\\result == 3u;"
        fields[2].text = "f"
        self.assertEqual([change["line"] for change in check_path_adapter(before, after, "located", source)], [5])
        after.find(Q + "edge").findall(Q + "data")[2].text = "f"
        with self.assertRaisesRegex(AssertionError, "undeclared"):
            check_path_adapter(before, after, "located", source)

    def test_duplicate_declarations_and_metadata_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "witness.graphml"
            path.write_text('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">'
                            '<key id="programhash"/><key id="programhash"/><graph/></graphml>')
            with self.assertRaisesRegex(AssertionError, "duplicate GraphML key"):
                envelope(path)
            path.write_text('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"><graph>'
                            '<data key="programhash">a</data><data key="programhash">b</data>'
                            '</graph></graphml>')
            with self.assertRaisesRegex(AssertionError, "duplicate graph metadata"):
                envelope(path)

    def test_definitive_producer_cannot_hide_missing_receivers(self):
        for arms in ({}, {arm: {} for arm in ARMS if arm != "input"}):
            with self.assertRaisesRegex(AssertionError, "every receiving arm"):
                check_arm_inventory({"producer": {"status": "REFUTED"}, "arms": arms})
        check_arm_inventory({"producer": {"status": "REFUTED"}, "arms": {arm: {} for arm in ARMS}})
        check_arm_inventory({"producer": {"status": "TIMEOUT"}, "arms": {}})
        with self.assertRaisesRegex(AssertionError, "unresolved producer"):
            check_arm_inventory({"producer": {"status": "TIMEOUT"}, "arms": {"input": {}}})

    def test_reached_set_is_not_witness_automaton_size(self):
        values, issues = extract("Number of states: 5\nSize of reached set: 71\n"
                                 "Number of iterations: 80\nNumber of CEGAR refinements: 2\n"
                                 "Number of abstraction computations: 91\n")
        self.assertEqual(values["reached_states"], 71)
        self.assertEqual(values["iterations"], 80)
        self.assertEqual(issues, {})

    def test_repeated_blocks_are_not_silently_averaged(self):
        values, issues = extract("Number of iterations: 20\nNumber of iterations: 30\n")
        self.assertNotIn("iterations", values)
        self.assertEqual(issues["iterations"], "multiple statistics blocks")

    def test_missing_and_zero_are_distinct(self):
        values, issues = extract("Number of CEGAR refinements: 0\n")
        self.assertEqual(values["cegar_refinements"], 0)
        self.assertEqual(issues["iterations"], "missing")

    def test_only_nonsemantic_paths_are_normalized(self):
        left = ["cpa", "--32", "--output-path", "input-output", "--witness", "input.graphml", "program.c"]
        right = ["cpa", "--32", "--output-path", "trivial-output", "--witness", "trivial.graphml", "program.c"]
        self.assertEqual(command_profile(left, "input"), command_profile(right, "trivial"))
        right[1] = "--64"
        self.assertNotEqual(command_profile(left, "input"), command_profile(right, "trivial"))

    def test_optimized_audits_stop_before_any_output(self):
        scripts = ("analyze_witness_search.py", "verify_witness_interoperability.py", "witness_projection_controls.py",
                   "continue_witness_interoperability.py", "resume_witness_interoperability.py")
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "must-not-exist.json"
            for script in scripts:
                for mode in ("-O", "-OO"):
                    command = [sys.executable, mode, "-B", str(Path(__file__).parent / script),
                               "--study", str(Path(temporary) / "missing"), "--output", str(output)]
                    result = subprocess.run(command, capture_output=True, text=True, timeout=15)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("assertions enabled", result.stderr)
                    self.assertFalse(output.exists())

    def test_completed_analysis_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "completed.json"
            output.write_text("completed evidence\n")
            for script in ("analyze_witness_search.py", "verify_witness_interoperability.py"):
                result = subprocess.run([sys.executable, "-B", str(Path(__file__).parent / script),
                                         "--study", str(Path(temporary) / "missing"), "--output", str(output)],
                                        capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("output must be a new file", result.stderr)
                self.assertEqual(output.read_text(), "completed evidence\n")

    def test_secondary_steps_reject_unfinished_campaign(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "protocol.json").write_text("{}")
            (root / "summary.json").write_text(json.dumps({"outcome": "RUNNING"}))
            for script, extra in (("analyze_witness_search.py", []),
                                  ("witness_projection_controls.py", ["--cpachecker", "/bin/true"])):
                output = root / "must-not-exist"
                result = subprocess.run([sys.executable, "-B", str(Path(__file__).parent / script),
                                         "--study", str(root), "--output", str(output), *extra],
                                        capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
