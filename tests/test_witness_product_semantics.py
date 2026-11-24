"""Independent C executions for the checked witness product's semantic boundary.

The executable oracle exits immediately when the error function is reached.
Its expected flags are written from the owned control's arithmetic/control flow,
then compared with the study's separate sticky-flag native wrapper and DAG roots.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

if not __debug__:
    raise SystemExit("Witness product controls require enabled assertions.")

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import witness_interoperability as study

AUDIT_OUTPUT = None
COMPILER = None
MASK = (1 << 32) - 1
BOUND_SOURCES = ("tests/witness_interoperability.py", "src/proof_dag_checker.py",
                 "src/demand_evaluator.py", "tests/cbmc_comparison.py", "tests/scientific_driver.py",
                 "tests/test_witness_product_semantics.py")


def identity(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(identifier, candidate="return x;", *, original="return x;",
            reference="return x;", guard="x == x", inputs=None):
    inputs = {"x": [0, 1, MASK], "y": [0, 1, 31, 32]} if inputs is None else inputs
    parameters = ", ".join("unsigned " + name for name in inputs)
    def function(body):
        return "unsigned f(" + parameters + ") { " + body + " }"
    return {"id": identifier, "word_bits": 32, "inputs": inputs,
            "original": function(original), "candidate": function(candidate),
            "reference": function(reference), "repair_guard": guard}


EXIT_WRAPPER = r'''#include <limits.h>
#include <stdlib.h>
#define main repairseal_subject_main
#include "program.c"
#undef main
_Static_assert(sizeof(unsigned) * CHAR_BIT == 32, "32-bit unsigned required");
static unsigned supplied[8];
static unsigned position;
unsigned __VERIFIER_nondet_uint(void) { return supplied[position++]; }
void __VERIFIER_error(void) { _Exit(17); }
int main(int argc, char **argv) {
  if (argc < 2 || argc > 9) return 31;
  for (int i = 1; i < argc; ++i) supplied[i-1] = (unsigned)strtoul(argv[i], 0, 10);
  position = 0u;
  repairseal_subject_main();
  return 0;
}
'''


class WitnessProductSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = Path(COMPILER or shutil.which("gcc") or "").resolve()
        if not cls.compiler.is_file():
            raise unittest.SkipTest("a GCC executable is required for the independent native controls")
        cls.temporary = None
        if AUDIT_OUTPUT is None:
            cls.temporary = tempfile.TemporaryDirectory(prefix="repairseal-witness-products-")
            cls.directory = Path(cls.temporary.name)
        else:
            cls.directory = AUDIT_OUTPUT
            cls.directory.mkdir(parents=True, exist_ok=False)
        cls.records = []
        cls.source_bindings = {name: identity(ROOT / name) for name in BOUND_SOURCES}
        cls.compiler_identity = identity(cls.compiler)

    @classmethod
    def tearDownClass(cls):
        unchanged = (cls.source_bindings == {name: identity(ROOT / name) for name in BOUND_SOURCES}
                     and identity(cls.compiler) == cls.compiler_identity)
        report = {"native_controls": len(cls.records), "records": cls.records,
                  "source_bindings": cls.source_bindings,
                  "compiler": str(cls.compiler), "compiler_identity": cls.compiler_identity,
                  "source_and_compiler_unchanged": unchanged,
                  "actual_immediate_error_process_executions": sum(row["actual_process_executions"] for row in cls.records),
                  "actual_sticky_flag_point_calls": sum(row["native_wrapper_points"] for row in cls.records),
                  "scope": "Owned C semantic controls, using immediate-error process exits and the independent study native wrapper; not a new benchmark population."}
        (cls.directory / "native-controls.json").write_text(json.dumps(report, indent=2) + "\n")
        if cls.temporary is not None:
            cls.temporary.cleanup()
        if not unchanged:
            raise AssertionError("a source file or compiler changed during the native controls")

    def native(self, case, flag, outside=()):
        directory = self.directory / case["id"]
        directory.mkdir()
        (directory / "request.json").write_text(json.dumps(case, indent=2) + "\n")
        product = study.emit_product(case)
        (directory / "program.c").write_text(product)
        (directory / "exit-wrapper.c").write_text(EXIT_WRAPPER)
        command = [str(self.compiler), "-std=c11", "-O2", "-pedantic-errors",
                   "exit-wrapper.c", "-o", "exit-product"]
        compiled = subprocess.run(command, cwd=directory, capture_output=True, timeout=30)
        (directory / "exit-compile.stdout.txt").write_bytes(compiled.stdout)
        (directory / "exit-compile.stderr.txt").write_bytes(compiled.stderr)
        self.assertEqual(compiled.returncode, 0, compiled.stderr.decode(errors="replace"))
        points = [list(point) for point in itertools.product(*case["inputs"].values())]
        expected = [int(flag(*point)) for point in points]
        observations = []
        for point, target in [*zip(points, expected), *((list(point), 0) for point in outside)]:
            invocation = [str(directory / "exit-product"), *map(str, point)]
            result = subprocess.run(invocation, capture_output=True, timeout=5)
            observations.append({"input": point, "expected_error_flag": target,
                                 "exit_code": result.returncode,
                                 "stdout": result.stdout.decode(errors="replace"),
                                 "stderr": result.stderr.decode(errors="replace")})
            self.assertEqual(result.returncode, 17 if target else 0, observations[-1])
            self.assertEqual(result.stdout + result.stderr, b"")
        (directory / "exit-product").unlink()
        study.native_correspondence(case, directory, self.compiler)
        sticky = json.loads((directory / "native-correspondence.json").read_text())
        self.assertEqual(sticky["observed"], expected)
        self.assertEqual(sticky["expected"], expected)
        self.assertEqual(sticky["mismatches"], [])
        record = {"id": case["id"], "exit_compile_command": command,
                  "exit_compile_code": compiled.returncode, "actual_process_executions": len(observations),
                  "in_domain_points": len(points), "native_wrapper_points": len(points),
                  "observations": observations}
        (directory / "control.json").write_text(json.dumps(record, indent=2) + "\n")
        self.records.append(record)
        return product, sticky

    def test_overwritten_division_and_shift_faults_remain_observable(self):
        self.native(request("overwritten-division", "unsigned r = 1u / y; r = x; return r;"),
                    lambda x, y: y == 0)
        self.native(request("overwritten-remainder", "unsigned r = x % y; r = x; return r;"),
                    lambda x, y: y == 0)
        self.native(request("overwritten-shift", "unsigned r = x << y; r = x; return r;",
                            inputs={"x": [0, 1, MASK], "y": [0, 31, 32, MASK]}),
                    lambda x, y: y >= 32)

    def test_short_circuit_and_unselected_statement_faults(self):
        for label, condition in (("and", "(y != 0u) && (x / y > 0u)"),
                                 ("or", "(y == 0u) || (x / y > 0u)")):
            body = "unsigned r = 0u; if (" + condition + ") { r = 1u; } else { r = 2u; } return r;"
            self.native(request("short-circuit-" + label, body, reference=body), lambda x, y: False)
        body = "unsigned r = 0u; if (x == 0u) { r = 1u / y; } else { r = x; } r = x; return r;"
        self.native(request("selected-statement-fault", body), lambda x, y: x == 0 and y == 0)

    def test_only_the_selected_reference_role_can_add_a_fault(self):
        domain = {"x": [0, 1, MASK], "y": [0, 1]}
        self.native(request("unselected-original-fault", original="return x / y;", guard="y == 0u", inputs=domain),
                    lambda x, y: False)
        self.native(request("unselected-reference-fault", reference="return x / y;", guard="y != 0u", inputs=domain),
                    lambda x, y: False)
        self.native(request("selected-original-fault", original="return x / y;", guard="x != x", inputs=domain),
                    lambda x, y: y == 0)
        self.native(request("selected-reference-fault", reference="return x / y;", inputs=domain),
                    lambda x, y: y == 0)

    def test_unsigned_high_bits_wrap_without_signed_promotions(self):
        domain = {"x": [0, 1, 2, 2147483648, MASK]}
        self.native(request("unsigned-left-high-bit", "return x << 31u;",
                            reference="return (x & 1u) * 2147483648u;", inputs=domain), lambda x: False)
        self.native(request("unsigned-right-high-bit", "return x >> 31u;",
                            reference="return x / 2147483648u;", inputs=domain), lambda x: False)
        self.native(request("unsigned-wrap", "return (x + 1u) - 1u;", inputs=domain), lambda x: False)

    def test_legitimate_xor_is_not_rejected_as_suspected_power(self):
        self.native(request("legitimate-xor", "return x + (2u ^ 15u);",
                            reference="return x + 13u;", inputs={"x": [0, 1, MASK]}), lambda x: False)

    def test_exact_domain_membership_precedes_every_role(self):
        self.native(request("domain-holes", "return x + 1u;", inputs={"x": [0, 2], "y": [0, 32]}),
                    lambda x, y: True, outside=((1, 0), (0, 1), (MASK, 0), (0, 31)))
        for name in ("f", "main"):
            body = "return " + name + ";"
            self.native(request("identifier-" + name, body, original=body, reference=body,
                                guard=name + " == " + name, inputs={name: [0, 1, MASK]}), lambda x: False)

    def test_all_eight_native_input_slots_are_used(self):
        names = ["x" + str(index) for index in range(8)]
        expression = " + ".join(names)
        case = request("eight-inputs", "return (" + expression + ") + 1u;",
                       original="return " + expression + ";", reference="return " + expression + ";",
                       guard="x0 == x0", inputs={name: [0] for name in names})
        self.native(case, lambda *point: True, outside=([0] * 7 + [1],))

    def test_partial_guard_operators_are_checked_even_in_skipped_branches(self):
        controls = [
            ("guard-skipped-divide", "(x == x) || (1u / 0u > 0u)", True, "__repairseal_div"),
            ("guard-skipped-remainder", "(x != x) && (1u % 0u > 0u)", False, "__repairseal_rem"),
            ("guard-skipped-left-shift", "(x == x) || (1u << 32u > 0u)", True, "__repairseal_shl"),
            ("guard-skipped-right-shift", "(x != x) && (1u >> 32u > 0u)", False, "__repairseal_shr"),
        ]
        for name, guard, selected, helper in controls:
            case = request(name, original="return x + 1u;" if selected else "return x;",
                           reference="return x;" if selected else "return x + 1u;", guard=guard,
                           inputs={"x": [0, 1, MASK]})
            product, _ = self.native(case, lambda x: False)
            self.assertIn(helper + "(", product.split("int main(void)", 1)[1])
        self.native(request("guard-selected-division", original="return x + 1u;",
                            guard="x / 1u == 0u", inputs={"x": [0, 1, MASK]}), lambda x: x != 0)
        self.native(request("guard-selected-unsigned-shift", original="return x + 1u;",
                            guard="x << 1u == 0u", inputs={"x": [0, 2147483648, MASK]}),
                    lambda x: x == MASK)

    def test_admission_excludes_partial_guards_and_signed_promotion_cases(self):
        for body in ("return 2147483648;", "return 4294967296u;", "return (x == 0u) << 31u;",
                     "unsigned r = x == 0u; return r;", "return ~ (x == 0u);"):
            with self.subTest(body=body), self.assertRaises((study.core.Unsupported, study.core.Invalid)):
                study.emit_product(request("inadmissible-numeric-type", body))
        with self.assertRaisesRegex(study.core.Unsupported, "guard totality"):
            study.emit_product(request("partial-guard", guard="1u / x > 0u", inputs={"x": [1, 2]}))

    def test_input_projection_requires_unique_actual_refuting_coordinates(self):
        case = request("projection-point", "return x + 1u;", inputs={"x": [0, 2], "y": [0, 7]})
        program, native = self.native(case, lambda x, y: True)
        sites = sorted(line for line, name in study.call_initializers(program).items()
                       if name == "__VERIFIER_nondet_uint")
        root = ET.Element(study.Q + "graphml")
        graph = ET.SubElement(root, study.Q + "graph")
        ET.SubElement(graph, study.Q + "data", {"key": "witness-type"}).text = "violation_witness"
        for index, (line, value) in enumerate(zip(sites, (2, 7))):
            edge = ET.SubElement(graph, study.Q + "edge", {"source": str(index), "target": str(index + 1)})
            ET.SubElement(edge, study.Q + "data", {"key": "startline"}).text = str(line)
            ET.SubElement(edge, study.Q + "data", {"key": "assumption"}).text = f"return_value___VERIFIER_nondet_uint = {value}u;"
        context = ET.ElementTree(root)
        original = ET.tostring(root)
        projected, data = study.input_projection(context, program, case, native)
        self.assertEqual(data["values"], [2, 7])  # Deliberately not the least diagnostic input [0,0].
        self.assertEqual(data["native_point_index"], 3)
        self.assertEqual(ET.tostring(root), original)
        self.assertEqual(len(projected.getroot().findall("g:graph/g:edge", study.NS)), 3)
        ambiguous = copy.deepcopy(context)
        edge = ambiguous.getroot().find("g:graph/g:edge", study.NS)
        ET.SubElement(edge, study.Q + "data", {"key": "assumption"}).text = "return_value___VERIFIER_nondet_uint = 0u;"
        with self.assertRaisesRegex(ValueError, "unique concrete value"):
            study.input_projection(ambiguous, program, case, native)
        outside = copy.deepcopy(context)
        outside.getroot().find("g:graph/g:edge/g:data[@key='assumption']", study.NS).text = "return_value___VERIFIER_nondet_uint = 1u;"
        with self.assertRaisesRegex(ValueError, "outside the request domain"):
            study.input_projection(outside, program, case, native)
        false_native = copy.deepcopy(native); false_native["observed"][3] = 0
        with self.assertRaisesRegex(AssertionError, "did not refute"):
            study.input_projection(context, program, case, false_native)

    def test_confirmation_is_kind_specific_and_warning_information_survives(self):
        normal = {"timed_out": False, "exit_code": 0}
        for witness_type, terminal, expected in (
                ("violation_witness", "TRUE", "UNCONFIRMED"),
                ("violation_witness", "FALSE", "CONFIRMED"),
                ("correctness_witness", "TRUE", "CONFIRMED"),
                ("correctness_witness", "FALSE", "UNCONFIRMED"),
                ("correctness_witness", "UNKNOWN", "UNKNOWN")):
            self.assertEqual(study.classify_cpa(normal, "Verification result: " + terminal + ".", witness_type)["outcome"], expected)
        warning = "WARNING: ignoring assumption with unknown variables\nVerification result: FALSE."
        result = study.classify_cpa(normal, warning, "violation_witness")
        self.assertEqual(result["outcome"], "CONFIRMED")
        self.assertEqual(len(result["ignored_semantic_annotations"]), 1)
        duplicate = "Verification result: TRUE.\nVerification result: FALSE."
        self.assertEqual(study.classify_cpa(normal, duplicate, "violation_witness")["outcome"], "UNRESOLVED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--gcc", type=Path)
    args = parser.parse_args()
    if args.output is not None and (args.output.exists() or args.output.is_symlink()):
        parser.error("output must be new; retained observations are preserved")
    AUDIT_OUTPUT = args.output.resolve() if args.output is not None else None
    COMPILER = args.gcc.resolve() if args.gcc is not None else None
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WitnessProductSemantics))
    complete = result.wasSuccessful() and result.testsRun > 0 and not result.skipped
    if AUDIT_OUTPUT is not None:
        AUDIT_OUTPUT.mkdir(parents=True, exist_ok=True)
        with (AUDIT_OUTPUT / "test-result.json").open("x") as stream:
            stream.write(json.dumps({"outcome": "PASS" if complete else "INCOMPLETE" if result.wasSuccessful() else "FAILED",
                "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}, indent=2) + "\n")
    raise SystemExit(0 if complete else 1)
