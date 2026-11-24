"""Independent observations and correlated-point controls for direct ablations."""
from pathlib import Path
import sys
import unittest

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "src"), str(Path(__file__).resolve().parent)]
import proof_dag_checker as core
import int32_circuit as signed
import int32_baselines as baselines
from test_int32_circuit import expression_program, raw_program, task, concrete_task_decision, decision, LOW, HIGH
from int32_evaluator_study import orders, ARMS


class SignedDirectBaselineTests(unittest.TestCase):
    def check(self, request):
        expected = concrete_task_decision(request)
        full = signed.verify_evidence(request, signed.make_evidence(request))
        live = baselines.evaluate_live(request)
        projected = baselines.evaluate_projected_live(request)
        demand = signed.evaluate_direct(request)
        for result in (full, live, projected, demand):
            self.assertTrue(core.exact_equal(decision(result), expected), (result, expected))
        self.assertLessEqual(demand["semantic_cells"], projected["semantic_cells"])
        self.assertLessEqual(projected["semantic_cells"], live["semantic_cells"])
        self.assertLessEqual(live["semantic_cells"], full["semantic_cells"])
        self.assertEqual(projected["semantic_cells"], projected["projection_work"]["unique_representatives"])
        return expected, full, live, projected, demand

    def test_correlated_points_and_signed_order(self):
        request = task(expression_program("x"), expression_program("x + 1"),
                       ((-7, 4), (-7, 9), (3, -8), (3, -2)))
        expected, _full, _live, _projected, _demand = self.check(request)
        self.assertEqual(expected["witness"]["input"], [-7, 4])
        self.assertIn(expected["witness"]["input"], request["points"])

    def test_trace_order_overrides_input_order(self):
        candidate = raw_program('if (y < 0) printf("%d", 1); else printf("%d", 2); return 0;')
        request = task(candidate, expression_program("0"), ((-9, -2), (-8, 3), (1, 0)))
        expected, *_ = self.check(request)
        self.assertEqual(expected["witness"]["input"], [-8, 3])
        self.assertEqual(expected["witness"]["trace"], [[0, 0]])

    def test_definedness_priority_and_skipped_faults(self):
        points = ((LOW, -1), (-3, 0), (0, 0), (7, 2), (HIGH, 1))
        for expression in ("x / y", "y == 0 ? 7 : x / y", "(y != 0) && (x / y)", "(y == 0) || (x / y)"):
            with self.subTest(expression=expression):
                expected, *_ = self.check(task(expression_program(expression), expression_program("0"), points))
                self.assertEqual(expected["witness"]["obligation"], "defined")

    def test_dead_original_and_unused_coordinates(self):
        candidate = expression_program("x")
        request = task(candidate, candidate, ((1, 2), (1, 7), (3, -1), (3, 8)),
                       original=expression_program("(x * y + 11) / (y - 4)"))
        expected, full, live, projected, _demand = self.check(request)
        self.assertEqual(expected, {"status": "ACCEPT", "witness": None})
        self.assertLess(live["semantic_cells"], full["semantic_cells"])
        self.assertLess(projected["semantic_cells"], live["semantic_cells"])

    def test_all_binary_controls_on_boundary_pairs(self):
        points = ((LOW, -1), (LOW, 0), (-7, 2), (0, 0), (7, -2), (HIGH, 1), (HIGH, HIGH))
        for op in ("+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=", "&&", "||", "&", "|", "^"):
            with self.subTest(op=op):
                program = expression_program("x " + op + " y")
                self.check(task(program, program, points))

    def test_balanced_orders_are_exact_permutations(self):
        schedule = orders()
        self.assertEqual(len(schedule), 10)
        self.assertEqual(len(set(schedule)), 10)
        for row in schedule:
            self.assertEqual(set(row), set(ARMS))
            self.assertEqual(len(row), len(ARMS))


if __name__ == "__main__":
    unittest.main()
