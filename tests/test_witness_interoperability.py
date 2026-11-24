"""Boundary tests for the independently consumed witness experiment."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import witness_interoperability as w


class WitnessInteroperabilityTests(unittest.TestCase):
    def request(self, candidate, original=None, reference=None, guard="x == 0u"):
        def f(body):
            return "unsigned f(unsigned x, unsigned y) { " + body + " }"
        return {"id": "interop-control", "word_bits": 32,
                "inputs": {"x": [0, 1, 4294967295], "y": [0, 1, 31, 32]},
                "candidate": f(candidate), "original": f(original or "return x;"),
                "reference": f(reference or "return x;"), "repair_guard": guard}

    def test_partial_operations_keep_short_circuit(self):
        request = self.request("unsigned r = x; if (y != 0u && x / y > 0u) { r = x % y; } else { r = x; } return r;")
        result = w.emit_product(request)
        self.assertIn("(y != 0u) && ((__repairseal_div(x, y)) > 0u)", result)
        self.assertIn("r = __repairseal_rem(x, y)", result)
        self.assertIn("if (y == 0u) { __VERIFIER_error(); return 0u; }", result)

    def test_shift_helpers_keep_unsigned_modular_operators(self):
        result = w.emit_product(self.request("return (x << y) + (x >> y);"))
        self.assertIn("(__repairseal_shl(x, y)) + (__repairseal_shr(x, y))", result)
        self.assertIn("if (y >= 32u) { __VERIFIER_error(); return 0u; }", result)
        self.assertIn("return x << y;", result)

    def test_cr_comments_cannot_hide_source(self):
        request = self.request("unsigned r = 0u; // ignored\rr = x; return r;")
        self.assertIn("r = x;", w.emit_product(request))

    def test_role_evaluation_is_guarded(self):
        product = w.emit_product(self.request("return x;", "return x / y;", "return x;"))
        main = product.split("int main(void)", 1)[1]
        self.assertLess(main.index("__repairseal_candidate"), main.index("if (x == 0u)"))
        self.assertLess(main.index("__repairseal_reference"), main.index("} else {"))
        self.assertGreater(main.index("__repairseal_original"), main.index("} else {"))
        self.assertNotIn("__CPROVER_assume", main)
        self.assertIn("if (!(x == 0u || x == 1u || x == 4294967295u)) return 0;", main)

    def tree(self):
        return ET.ElementTree(ET.fromstring(f'''<graphml xmlns="{w.GRAPHML}"><graph edgedefault="directed">
          <data key="witness-type">violation_witness</data><node id="a"><data key="entry">true</data></node>
          <node id="b"><data key="violation">true</data></node><edge source="a" target="b">
          <data key="startline">42</data><data key="assumption">return_value___VERIFIER_nondet_uint = 4294967295u;</data>
          <data key="assumption.scope">main</data></edge></graph></graphml>'''))

    def test_return_translation_keeps_location_value_and_graph(self):
        tree = self.tree()
        before = copy.deepcopy(tree)
        changes = w.standardize_return_assumptions(tree)
        self.assertEqual(len(changes), 1)
        data = tree.getroot().find("g:graph/g:edge/g:data[@key='assumption']", w.NS)
        self.assertEqual(data.text, "\\result == 4294967295u;")
        edge = tree.getroot().find("g:graph/g:edge", w.NS)
        self.assertEqual(edge.find("g:data[@key='assumption.resultfunction']", w.NS).text,
                         "__VERIFIER_nondet_uint")
        self.assertEqual(edge.get("source"), "a")
        self.assertEqual(edge.get("target"), "b")
        self.assertEqual(edge.find("g:data[@key='startline']", w.NS).text, "42")
        self.assertEqual(len(before.getroot().findall("g:graph/g:node", w.NS)),
                         len(tree.getroot().findall("g:graph/g:node", w.NS)))

    def test_unrecognized_expression_is_not_erased(self):
        tree = self.tree()
        data = tree.getroot().find("g:graph/g:edge/g:data[@key='assumption']", w.NS)
        data.text = "x = return_value___f;"
        self.assertEqual(w.standardize_return_assumptions(tree), [])
        self.assertEqual(data.text, "x = return_value___f;")

    def test_located_return_uses_callee_not_producer_caller(self):
        program = "extern unsigned sample(void);\nint main(void) {\nunsigned x = sample();\nreturn 0;\n}\n"
        tree = self.tree()
        edge = tree.getroot().find("g:graph/g:edge", w.NS)
        edge.find("g:data[@key='startline']", w.NS).text = "3"
        edge.find("g:data[@key='assumption']", w.NS).text = "\\result = 7u;"
        ET.SubElement(edge, w.Q + "data", {"key": "assumption.resultfunction"}).text = "main"
        changes = w.locate_return_assumptions(tree, program)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["after_function"], "sample")
        self.assertEqual(changes[0]["after"], "\\result == 7u;")
        self.assertEqual(changes[0]["line"], 3)

    def test_nested_call_location_is_not_guessed(self):
        program = "extern unsigned f(unsigned); extern unsigned g(void);\nint main(void) {\nunsigned x = f(g());\nreturn 0;\n}\n"
        self.assertEqual(w.call_initializers(program), {})

    def test_trivial_control_has_no_semantic_annotation(self):
        tree = w.trivial_tree(self.tree())
        graph = tree.getroot().find(w.Q + "graph")
        self.assertEqual(len(graph.findall(w.Q + "node")), 1)
        self.assertEqual(len(graph.findall(w.Q + "edge")), 1)
        self.assertEqual(graph.find("g:node/g:data[@key='violation']", w.NS).text, "true")
        self.assertIsNone(graph.find(".//g:data[@key='assumption']", w.NS))

    def test_no_error_is_classified_as_semantic_refutation(self):
        record = {"timed_out": False, "exit_code": 1}
        result = w.classify_cpa(record, "Invalid configuration: witness format unsupported", "violation_witness")
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["outcome"], "ERROR")
        self.assertEqual(w.classify_cpa(record, "Verification result: FALSE.", "violation_witness")["outcome"], "ERROR")
        result = w.classify_cpa({"timed_out": True, "exit_code": -9},
                               "Verification result: FALSE.", "violation_witness")
        self.assertEqual(result["outcome"], "TIMEOUT")

    def test_validation_requires_witness_kind_specific_result(self):
        record = {"timed_out": False, "exit_code": 0}
        self.assertEqual(w.classify_cpa(record, "Verification result: FALSE.", "violation_witness")["outcome"], "CONFIRMED")
        self.assertEqual(w.classify_cpa(record, "Verification result: FALSE.", "correctness_witness")["outcome"], "UNCONFIRMED")
        self.assertEqual(w.classify_cpa(record, "Verification result: UNKNOWN.", "violation_witness")["outcome"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
