"""Canonical observations for dense point-local demand evaluation."""
from pathlib import Path
import copy
import itertools
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
import int32_circuit as signed
import int32_baselines as baselines
from int32_point_demand import evaluate_point_demand, PointMemo
from demand_evaluator import _Counter
from test_int32_circuit import (expression_program, raw_program, task,
    concrete_task_decision, decision, LOW, HIGH, BOUNDARIES, BINARY)


class PointDemandTests(unittest.TestCase):
    def check(self, request):
        expected = concrete_task_decision(request)
        full = signed.verify_evidence(request, signed.make_evidence(request))
        live = baselines.evaluate_live(request)
        support = signed.evaluate_direct(request)
        point = evaluate_point_demand(request)
        for result in (full, live, support, point):
            self.assertTrue(core.exact_equal(decision(result), expected), (result, expected))
        self.assertLessEqual(support["semantic_cells"], point["semantic_cells"])
        self.assertLessEqual(point["semantic_cells"], live["semantic_cells"])
        self.assertEqual(point["counters"]["support_nodes"], 0)
        self.assertEqual(point["counters"]["key_coordinates"], 0)
        self.assertEqual(point["counters"]["cache_queries"],
                         point["semantic_cells"] + point["counters"]["cache_hits"])
        return expected, full, live, support, point

    def test_binary_boundary_grid(self):
        points = list(itertools.product(BOUNDARIES, repeat=2))
        for operator in BINARY:
            with self.subTest(operator=operator):
                program = expression_program("x " + operator + " y")
                self.check(task(program, program, points))

    def test_zero_points_rejected_and_one_point_preserved(self):
        base = task(expression_program("x / y"), expression_program("0"), [(LOW, -1)])
        expected, *_ = self.check(base)
        self.assertEqual(expected["witness"]["obligation"], "defined")
        empty = copy.deepcopy(base)
        empty["points"] = []
        with self.assertRaises(core.Invalid):
            evaluate_point_demand(empty)

    def test_correlated_inputs_and_trace_priority(self):
        candidate = raw_program('int scratch = 0; if (x < 0) { scratch = 1; } printf("%d", 1); return 0;')
        request = task(candidate, expression_program("0"), [(-5, -100), (2, 10), (2, 20)])
        expected, *_ = self.check(request)
        self.assertEqual(expected["witness"], {"obligation": "repair", "trace": [[0, 0]], "input": [2, 10]})
        self.assertNotIn([2, -100], request["points"])

    def test_constant_roots_and_unused_axis(self):
        points = [(x, y) for x in (-2, 0, 3) for y in (-11, 9, 12)]
        for expr in ("0", "1", "x", "x < 0 ? 1 : 2"):
            with self.subTest(expr=expr):
                self.check(task(expression_program(expr), expression_program("0"), points))

    def test_undefined_priority_and_skipped_operands(self):
        points = [(LOW, -1), (-3, 0), (0, 0), (7, 2), (HIGH, 1)]
        for expr in ("x / y", "y == 0 ? 7 : x / y", "(y != 0) && (x / y)", "(y == 0) || (x / y)"):
            with self.subTest(expr=expr):
                expected, *_ = self.check(task(expression_program(expr), expression_program("0"), points))
                self.assertEqual(expected["witness"]["obligation"], "defined")

    def test_unexecuted_statements_nested_trace_and_return(self):
        candidate = raw_program('int r = 0; if (x < 0) { printf("%d", 7); return 0; '
                                'if (y) { r = 1 / 0; } } if (y) { r = 8; } else { r = 9; } '
                                'printf("%d", r); return 0; r = 1 / 0;')
        self.check(task(candidate, expression_program("0"), [(-1, 0), (0, 0), (0, 1)]))

    def test_type_checks_and_no_false_zero_cache_miss(self):
        circuit = core.Circuit()
        zero = circuit.const(0)
        count = _Counter(None)
        memo = PointMemo(circuit, (), [()], count)
        self.assertEqual(memo.get(zero, 0), 0)
        self.assertEqual(memo.get(zero, 0), 0)
        self.assertIs(memo.get(circuit.false, 0), False)
        self.assertIs(memo.get(circuit.false, 0), False)
        self.assertEqual(count.values["semantic_cells"], 2)
        self.assertEqual(count.values["cache_hits"], 2)

    def test_invalid_point_order_duplicates_and_schema(self):
        base = task(expression_program("x"), expression_program("x"), [(1, 2), (3, 4)])
        for points in ([], [[3, 4], [1, 2]], [[1, 2], [1, 2]], [[True, 2]], [[LOW - 1, 2]]):
            bad = copy.deepcopy(base)
            bad["points"] = points
            with self.subTest(points=points), self.assertRaises(core.Invalid):
                evaluate_point_demand(bad)


if __name__ == "__main__":
    unittest.main()
