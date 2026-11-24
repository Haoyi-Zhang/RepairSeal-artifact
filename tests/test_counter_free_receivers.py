"""Checks for the semantic risks introduced by measurement-only AST elision.

These owned-source controls exercise strict local types, short circuiting,
undefinedness, correlated points, canonical trace priority and hook cleanup.
The test source changes are transient strings; no scientific source is edited.
"""
from __future__ import annotations

import ast
from collections import Counter
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
import int32_circuit as signed
import int32_point_demand as point
import counter_free_receivers as elided
import counter_overhead_study as study
from test_int32_circuit import (expression_program, raw_program, task,
                                concrete_task_decision, decision, LOW, HIGH)


class CounterElisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel = elided.initialize()

    def test_exact_manifest_and_retained_functional_import(self):
        code, manifest = elided.derive()
        self.assertEqual(manifest["removed_statement_count"], 37)
        self.assertEqual(len(manifest["changes"]), 46)
        self.assertEqual(manifest["derived_source_identity"], elided.identity(code.encode()))
        self.assertEqual(set(manifest["source_bindings"]), set(elided.SOURCES))
        self.assertEqual(manifest["canonical_return_fields"], ["status", "witness"])
        tree = ast.parse(code)
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "evaluate_support")
        imports = [node for node in ast.walk(function) if isinstance(node, ast.ImportFrom)]
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].module, "_repairseal_counter_free_derived")
        self.assertEqual([alias.name for alias in imports[0].names], ["SupportMemo", "support_sets"])
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                             and node.func.attr == "add" for node in ast.walk(tree)))
        selected = study.receivers()
        self.assertIs(selected["support_uninstrumented"], self.kernel.evaluate_support)
        self.assertIs(selected["point_uninstrumented"], self.kernel.evaluate_point)

    def test_unreviewed_instrumentation_and_side_effect_argument_rejected(self):
        original = elided.source_texts()
        needle = 'self.count.add("cache_queries")'
        changes = (
            needle + '\n        ' + needle,
            'self.count.add("cache_queries", self._query(node, point))',
        )
        for replacement in changes:
            texts = dict(original)
            self.assertEqual(texts[elided.SOURCES[0]].count(needle), 1)
            texts[elided.SOURCES[0]] = texts[elided.SOURCES[0]].replace(needle, replacement)
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                elided.derive(texts)

    def test_strict_local_types_survive_elision(self):
        circuit = core.Circuit()
        zero = circuit.const(0)
        support = self.kernel.SupportMemo(circuit, self.kernel.support_sets(circuit, ()))
        dense = self.kernel.PointMemo(circuit, (), [()])
        for node, bad in ((zero, True), (circuit.false, 0), (zero, -1), (zero, core.MASK + 1)):
            with self.subTest(node=node, value=bad):
                support._query(node, ())
                with self.assertRaises(core.Invalid):
                    support._store(self.kernel.SupportFrame(node, ()), bad)
                with self.assertRaises(core.Invalid):
                    dense._store(node, bad, [None] * len(circuit.nodes))

    def test_false_and_zero_remain_valid_cached_values(self):
        circuit = core.Circuit()
        zero = circuit.const(0)
        support = self.kernel.SupportMemo(circuit, self.kernel.support_sets(circuit, ()))
        dense = self.kernel.PointMemo(circuit, (), [()])
        for arm, memo, index in (("support_uninstrumented", support, ()),
                                 ("point_uninstrumented", dense, 0)):
            with self.subTest(arm=arm), elided.capture_stores(arm) as events:
                self.assertIs(type(memo.get(zero, index)), int)
                self.assertEqual(memo.get(zero, index), 0)
                self.assertIs(memo.get(circuit.false, index), False)
                self.assertIs(memo.get(circuit.false, index), False)
            self.assertEqual(len(events), 2)
            self.assertEqual([event[2] for event in events], ["int", "bool"])

    def compare_receivers(self, request):
        expected = concrete_task_decision(request)
        traces, results = {}, {}
        functions = study.receivers()
        for arm in ("support", "point", "support_uninstrumented", "point_uninstrumented"):
            with elided.capture_stores(arm) as events:
                result = functions[arm](request)
            self.assertTrue(core.exact_equal(decision(result), expected), (arm, result, expected))
            if arm.endswith("_uninstrumented"):
                self.assertEqual(set(result), {"status", "witness"})
            traces[arm], results[arm] = events, result
        for arm in ("support", "point"):
            self.assertTrue(core.exact_equal(traces[arm], traces[arm + "_uninstrumented"]))
            self.assertEqual(len(traces[arm]), results[arm]["semantic_cells"])
        self.assertTrue(elided.hooks_restored())
        return expected

    def test_undefinedness_short_circuit_and_unused_coordinates(self):
        points = [(LOW, -1), (-3, 0), (0, 0), (7, 2), (HIGH, 1)]
        for expr in ("x / y", "y == 0 ? 7 : x / y", "(y != 0) && (x / y)",
                     "(y == 0) || (x / y)", "0", "x < 0 ? 1 : 2"):
            with self.subTest(expr=expr):
                self.compare_receivers(task(expression_program(expr), expression_program("0"), points))

    def test_correlated_points_and_canonical_trace_priority(self):
        candidate = raw_program('int scratch = 0; if (x < 0) { scratch = 1; } '
                                'printf("%d", 1); return 0;')
        request = task(candidate, expression_program("0"), [(-5, -100), (2, 10), (2, 20)])
        result = self.compare_receivers(request)
        self.assertEqual(result["witness"], {"obligation": "repair", "trace": [[0, 0]], "input": [2, 10]})

    def test_early_return_does_not_evaluate_unreached_fault(self):
        candidate = raw_program('int r = 0; if (x < 0) { printf("%d", 7); return 0; '
                                'if (y) { r = 1 / 0; } } if (y) { r = 8; } else { r = 9; } '
                                'printf("%d", r); return 0; r = 1 / 0;')
        result = self.compare_receivers(task(candidate, expression_program("0"), [(-1, 0), (0, 0), (0, 1)]))
        self.assertEqual(result["witness"]["obligation"], "repair")

    def test_rejected_domains_restore_all_hooks_after_exception(self):
        base = task(expression_program("x"), expression_program("x"), [(1, 2), (3, 4)])
        functions = study.receivers()
        for points in ([], [[3, 4], [1, 2]], [[1, 2], [1, 2]], [[True, 2]], [[LOW - 1, 2]]):
            request = copy.deepcopy(base)
            request["points"] = points
            for arm in ("support", "point", "support_uninstrumented", "point_uninstrumented"):
                with self.subTest(points=points, arm=arm), self.assertRaises(core.Invalid):
                    with elided.capture_stores(arm):
                        functions[arm](request)
                self.assertTrue(elided.hooks_restored())

    def test_nested_trace_hooks_rejected_without_losing_cleanup(self):
        with elided.capture_stores("support"):
            with self.assertRaises(ValueError):
                with elided.capture_stores("point"):
                    pass
        self.assertTrue(elided.hooks_restored())

    def test_design_balances_positions_and_directed_neighbors(self):
        orders = study.orders()
        self.assertEqual(len(orders), 10)
        positions = Counter((arm, index) for order in orders for index, arm in enumerate(order))
        pairs = Counter(pair for order in orders for pair in zip(order, order[1:]))
        self.assertEqual(set(positions.values()), {2})
        self.assertEqual(len(positions), 25)
        self.assertEqual(set(pairs.values()), {2})
        self.assertEqual(len(pairs), 20)


if __name__ == "__main__":
    unittest.main()
