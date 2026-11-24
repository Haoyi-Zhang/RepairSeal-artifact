"""Adversarial contracts for the certificate-free demand evaluator."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import proof_dag_checker as core
import demand_evaluator as demand
from domain_transport import evaluate_pruned


EVALUATORS = (demand.evaluate_demand, demand.evaluate_projected_live)


def make_request(candidate="return x;", *, axes=None, original="return x;",
                 reference="return x;", guard="x == x"):
    axes = {"x": [0, 1], "z": [0, 1]} if axes is None else axes
    parameters = ", ".join("unsigned " + name for name in axes)
    def program(body):
        return "unsigned f(" + parameters + ") { " + body + " }"
    return {"id": "demand-test", "word_bits": 32, "inputs": copy.deepcopy(axes),
            "original": program(original), "candidate": program(candidate),
            "reference": program(reference), "repair_guard": guard}


def decision(result):
    return {key: result[key] for key in ("status", "witness")}


class DemandEvaluatorTests(unittest.TestCase):
    def compare(self, request):
        expected = core.evaluate_topological(request)
        pruned = evaluate_pruned(request)
        results = [evaluate(request) for evaluate in EVALUATORS]
        for result in results:
            self.assertTrue(core.exact_equal(decision(result), decision(expected)))
            self.assertLessEqual(result["checked_cells"], pruned["checked_cells"])
            counts = result["work_counts"]
            self.assertEqual(result["checked_cells"], counts["semantic_cells"])
            self.assertEqual(counts["cache_writes"], counts["semantic_cells"])
            self.assertEqual(counts["cache_queries"], counts["cache_hits"] + counts["cache_writes"])
            self.assertEqual(sum(result["phase_cells"].values()), result["checked_cells"])
        self.assertLessEqual(results[0]["checked_cells"], results[1]["checked_cells"])
        return results

    def test_empty_support_still_has_one_boolean_cell(self):
        request = make_request("return 0u;", original="return 0u;", reference="return 0u;",
                               guard="0u == 0u")
        for result in self.compare(request):
            self.assertEqual(result["status"], "ACCEPT")
            self.assertEqual(result["checked_cells"], 1)
            self.assertEqual(result["obligation_supports"], [[], [], []])
            self.assertEqual(result["work_counts"]["trace_events_examined"], 0)
            self.assertGreater(result["work_counts"]["cache_queries"], 0)
        request["reference"] = request["reference"].replace("0u", "1u")
        for result in self.compare(request):
            self.assertTrue(core.exact_equal(result["witness"],
                {"obligation": "repair", "trace": [], "input": [0, 0]}))
            self.assertEqual(result["work_counts"]["diagnostic_points"], 1)
            self.assertEqual(result["diagnostic_support"], [])

    def test_global_support_is_not_an_observed_constant(self):
        request = make_request("return 0u;", axes={"x": [0], "y": [0]},
                               original="return 0u;", reference="return 1u;",
                               guard="(x != 0u) && (y != 0u)")
        before = demand.evaluate_demand(request)
        self.assertEqual(before["status"], "ACCEPT")
        self.assertIn(["x", "y"], before["obligation_supports"])
        changed = copy.deepcopy(request)
        changed["inputs"] = {"x": [1], "y": [1]}
        for result in self.compare(changed):
            self.assertEqual(result["witness"]["obligation"], "repair")
            self.assertEqual(result["witness"]["input"], [1, 1])

    def test_short_circuit_definedness_and_acceptance_do_not_require_trace_values(self):
        original_local = core.local_value
        for guard in ("(z != 0u) && (x / z > 0u)",
                      "(z == 0u) || (x / z > 0u)"):
            with self.subTest(guard=guard):
                request = make_request("unsigned r = 0u; if (" + guard +
                    ") { r = 0u; } else { r = 0u; } return r;",
                    original="return 0u;", reference="return 0u;")
                operations = []
                def observed(op, values):
                    operations.append(op)
                    return original_local(op, values)
                with mock.patch.object(core, "local_value", side_effect=observed):
                    result = demand.evaluate_demand(request)
                self.assertEqual(result["status"], "ACCEPT")
                self.assertNotIn("/", operations)
                self.assertEqual(result["work_counts"]["trace_events_examined"], 0)
                lazy, projected = self.compare(request)
                self.assertLess(lazy["checked_cells"], projected["checked_cells"])

    def test_unused_division_still_contributes_definedness(self):
        request = make_request("unsigned unused = 1u / z; return x;",
                               axes={"x": [5, 7], "z": [1]})
        self.assertEqual(demand.evaluate_demand(request)["status"], "ACCEPT")
        request["inputs"]["z"] = [0, 1]
        for result in self.compare(request):
            self.assertTrue(core.exact_equal(result["witness"],
                {"obligation": "defined", "trace": [], "input": [5, 0]}))
            self.assertIn("z", result["obligation_supports"][0])

    def test_trace_order_precedes_input_order_and_unused_coordinates_take_minima(self):
        request = make_request("unsigned scratch = 0u; "
            "if (z == 0u) { scratch = 1u; } else { scratch = 2u; } return x + 1u;",
            axes={"z": [0, 1], "x": [2, 4], "unused": [7, 99]})
        for result in self.compare(request):
            self.assertTrue(core.exact_equal(result["witness"],
                {"obligation": "repair", "trace": [[0, 0]], "input": [1, 2, 7]}))
            self.assertEqual(result["diagnostic_support"], ["z", "x"])
        reordered = copy.deepcopy(request)
        reordered["inputs"] = {"x": [2, 4], "z": [0, 1], "unused": [7, 99]}
        for role in core.ROLES:
            reordered[role] = reordered[role].replace("unsigned z, unsigned x", "unsigned x, unsigned z")
        for result in self.compare(reordered):
            self.assertEqual(result["witness"]["input"], [2, 1, 7])

    def test_nested_candidate_event_reachability_is_preserved(self):
        request = make_request("unsigned scratch = 0u; "
            "if (x == 0u) { if (z == 0u) { scratch = 1u; } else { scratch = 2u; } } "
            "else { scratch = 3u; } return x + 1u;",
            axes={"z": [0, 1], "x": [0, 1], "unused": [7, 99]})
        for result in self.compare(request):
            self.assertTrue(core.exact_equal(result["witness"],
                {"obligation": "repair", "trace": [[0, 0]], "input": [0, 1, 7]}))

    def test_defined_failure_precedes_earlier_input_repair_failure(self):
        request = make_request("unsigned unused = 1u / (x ^ 3u); return 0u;",
                               axes={"x": [0, 1, 3]}, original="return 0u;", reference="return 1u;")
        for result in self.compare(request):
            self.assertTrue(core.exact_equal(result["witness"],
                {"obligation": "defined", "trace": [], "input": [3]}))

    def test_changed_axis_values_do_not_reuse_a_previous_call(self):
        request = make_request("return x + 1u;", axes={"x": [core.MASK]},
                               original="return 0u;", reference="return 0u;")
        for evaluate in EVALUATORS:
            self.assertEqual(evaluate(request)["status"], "ACCEPT")
            changed = copy.deepcopy(request)
            changed["inputs"]["x"] = [0]
            result = evaluate(changed)
            self.assertEqual(result["status"], "REFUTED")
            self.assertEqual(result["witness"]["input"], [0])

    def test_exact_boolean_sorts_for_all_boolean_operators_and_ite(self):
        circuit = core.Circuit()
        x, y = circuit.input("x"), circuit.input("y")
        booleans = [circuit.op(op, x, y) for op in sorted(core.REL)]
        p, q = circuit.op("==", x, circuit.const(0)), circuit.op("==", y, circuit.const(0))
        booleans += [circuit.op("not", p), circuit.op("and", p, q),
                     circuit.op("or", p, q), circuit.op("ite", p, q, circuit.op("not", q))]
        word_ite = circuit.op("ite", p, x, y)
        counter = demand._Counter(None)
        memo = demand._Memo(circuit, demand._supports(circuit, ["x", "y"], counter), counter)
        seen = set()
        for point in ([0, 0], [0, 1], [1, 0], [1, 1]):
            for node in booleans:
                value = memo.get(node, point)
                self.assertIs(type(value), bool)
                seen.add(value)
            self.assertIs(type(memo.get(word_ite, point)), int)
        self.assertEqual(seen, {False, True})
        for node, table in memo.tables.items():
            expected = bool if circuit.sorts[node] == "bool" else int
            self.assertTrue(all(type(value) is expected for value in table.values()))

    def test_admission_and_exception_classes_match_existing_receiver(self):
        cases = []
        for axis in ([True], [False], [1.0], [1, 0], [0, 0], (0, 1)):
            request = make_request()
            request["inputs"]["x"] = axis
            cases.append(request)
        for key, value in (("word_bits", True), ("extra", 1), ("candidate", 1),
                           ("candidate", "unsigned f(unsigned x) { return x; }"),
                           ("candidate", "unsigned f(unsigned x, unsigned z) { while (x) {} return x; }")):
            request = make_request()
            request[key] = value
            cases.append(request)
        for request in cases:
            with self.subTest(request=request):
                try:
                    core.evaluate_topological(request)
                except (core.Invalid, core.Unsupported) as error:
                    expected = type(error)
                else:
                    self.fail("negative admission control was accepted")
                for evaluate in EVALUATORS:
                    with self.assertRaises(expected):
                        evaluate(request)

    def test_budget_exception_does_not_return_or_publish_partial_state(self):
        request = make_request("return x + 1u;")
        expected = demand.evaluate_demand(request)
        class Exhausted(RuntimeError):
            pass
        for evaluate in EVALUATORS:
            cells = 0
            def budget(kind, amount):
                nonlocal cells
                if kind == "demand_semantic_cells":
                    cells += amount
                    if cells == 3:
                        raise Exhausted("owned test budget")
            with self.assertRaisesRegex(Exhausted, "owned test budget"):
                evaluate(request, count=budget)
            self.assertTrue(core.exact_equal(decision(evaluate(request)), decision(expected)))
        observed = {}
        def record(kind, amount):
            observed[kind] = observed.get(kind, 0) + amount
        result = demand.evaluate_demand(request, count=record)
        self.assertEqual(observed, {"demand_" + key: value for key, value in
                                   result["work_counts"].items() if value})

    def test_callback_cannot_mutate_the_validated_request_snapshot(self):
        for evaluate in EVALUATORS:
            request = make_request("return x + 1u;")
            expected = decision(evaluate(request))
            def mutate(_kind, _amount):
                request.clear()
            self.assertTrue(core.exact_equal(decision(evaluate(request, count=mutate)), expected))

    def test_long_sequential_dag_uses_an_explicit_evaluation_stack(self):
        length = 650
        candidate = "unsigned r = x; " + "r = r + 1u; " * length + "return r;"
        request = make_request(candidate, axes={"x": [0, core.MASK]},
                               original=f"return x + {length}u;", reference=f"return x + {length}u;")
        result, _projected = self.compare(request)
        self.assertEqual(result["status"], "ACCEPT")
        self.assertGreater(result["maximum_evaluation_stack_depth"], 600)

    def test_scientific_driver_refuses_optimized_runs_and_preserves_existing_evidence(self):
        driver = Path(__file__).with_name("demand_comparison.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for flag in ("-O", "-OO"):
                output = root / flag.lstrip("-")
                process = subprocess.run([sys.executable, flag, "-B", str(driver), "--output", str(output)],
                                         capture_output=True, text=True, check=False)
                self.assertNotEqual(process.returncode, 0)
                self.assertIn("run without -O or -OO", process.stderr)
                self.assertFalse(output.exists())
            output = root / "evidence"
            output.mkdir()
            marker = output / "existing.json"
            marker.write_text('{"owned": true}\n', encoding="utf-8")
            process = subprocess.run([sys.executable, "-B", str(driver), "--output", str(output)],
                                     capture_output=True, text=True, check=False)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("existing evidence is preserved", process.stderr)
            self.assertEqual(list(output.iterdir()), [marker])
            self.assertEqual(marker.read_text(), '{"owned": true}\n')

    @unittest.skipUnless(__debug__, "scientific driver deliberately refuses optimized Python")
    def test_scientific_driver_marks_interrupted_campaigns_failed(self):
        import demand_comparison as study
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "failed-campaign"
            with mock.patch.object(study, "freeze_population", side_effect=ValueError("owned freeze failure")):
                with self.assertRaisesRegex(ValueError, "owned freeze failure"):
                    study.run(output)
            self.assertEqual(json.loads((output / "status.json").read_text())["outcome"], "FAILED")
            self.assertFalse((output / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
