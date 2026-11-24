"""Owned-source controls for signed circuit semantics and finite point packets.

The arithmetic oracle uses Python mathematical integers; it imports neither
interpreter for its expected values. Native controls compile only the small C
strings defined in this file, never corpus source. Undefined native cases run
under UBSan and are checked only for rejection, not for an output value.
"""
from pathlib import Path
import copy
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import proof_dag_checker as core
import codeflaws_int32_bridge as bridge
import int32_circuit as circuit


LOW, HIGH = -(1 << 31), (1 << 31) - 1
BOUNDARIES = (LOW, LOW + 1, -65536, -46341, -46340, -2, -1,
              0, 1, 2, 46340, 46341, 65536, HIGH - 1, HIGH)
BINARY = ("+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=",
          "&&", "||", "&", "|", "^")


def raw_program(body, arity=2, signature="int main(void)"):
    names = ("x", "y")[:arity]
    declaration = "int " + ", ".join(names) + ";"
    fmt = " ".join("%d" for _name in names)
    targets = ", ".join("&" + name for name in names)
    return ("#include <stdio.h>\n" + signature + " { " + declaration +
            ' scanf("' + fmt + '", ' + targets + "); " + body + " }\n").encode("ascii")


def expression_program(expression):
    return raw_program('printf("%d", ' + expression + "); return 0;")


def checked_integer(value):
    return str(value) if LOW <= value <= HIGH else None


def mathematical(op, a, b):
    if op == "+": return checked_integer(a + b)
    if op == "-": return checked_integer(a - b)
    if op == "*": return checked_integer(a * b)
    if op in {"/", "%"}:
        if b == 0 or (a == LOW and b == -1):
            return None
        quotient = abs(a) // abs(b)
        if (a < 0) != (b < 0): quotient = -quotient
        return str(quotient if op == "/" else a - quotient * b)
    if op == "<": return str(int(a < b))
    if op == "<=": return str(int(a <= b))
    if op == ">": return str(int(a > b))
    if op == ">=": return str(int(a >= b))
    if op == "==": return str(int(a == b))
    if op == "!=": return str(int(a != b))
    if op == "&&": return str(int(bool(a) and bool(b)))
    if op == "||": return str(int(bool(a) or bool(b)))
    if op == "&": return str(a & b)
    if op == "|": return str(a | b)
    if op == "^": return str(a ^ b)
    raise ValueError(op)


def task(candidate, reference, points, original=None):
    return {"kind": circuit.PROFILE, "id": "owned-int32-control",
            "policy": "reference-everywhere",
            "sources": {"original": (reference if original is None else original).decode("ascii"),
                        "candidate": candidate.decode("ascii"), "reference": reference.decode("ascii")},
            "points": sorted([list(point) for point in points])}


def decision(result):
    return {key: result[key] for key in ("status", "witness")}


def concrete_task_decision(request):
    admitted = {role: bridge.admit_source(request["sources"][role].encode(), filename=role)
                for role in ("candidate", "reference")}
    rows = []
    for point in request["points"]:
        candidate = bridge.evaluate(admitted["candidate"], point)
        reference = bridge.evaluate(admitted["reference"], point)
        rows.append((point, candidate.trace, (candidate.defined,
                    candidate.defined and reference.defined and candidate.value == reference.value, True)))
    for column, obligation in enumerate(core.OBLIGATIONS):
        failures = [row for row in rows if not row[2][column]]
        if failures:
            point, trace, _truth = min(failures, key=lambda row: (row[1], tuple(row[0])))
            return {"status": "REFUTED", "witness": {"obligation": obligation,
                    "trace": [list(event) for event in trace], "input": list(point)}}
    return {"status": "ACCEPT", "witness": None}


def resign(packet):
    body = {key: value for key, value in packet.items() if key != "sha256"}
    encoded = json.dumps(body, sort_keys=True, ensure_ascii=True,
                         separators=(",", ":"), allow_nan=False).encode()
    packet["sha256"] = hashlib.sha256(encoded).hexdigest()
    return packet


class Int32CircuitTests(unittest.TestCase):
    def observation(self, admitted, point, expected_value, expected_trace=()):
        symbolic = circuit.evaluate_program(admitted, list(point))
        concrete = bridge.evaluate(admitted, tuple(point))
        expected = {"defined": expected_value is not None, "value": expected_value,
                    "trace": tuple(expected_trace)}
        symbolic_observation = {key: symbolic[key] for key in expected}
        concrete_observation = {key: getattr(concrete, key) for key in expected}
        self.assertTrue(core.exact_equal(symbolic_observation, expected),
                        (point, symbolic_observation, expected))
        self.assertTrue(core.exact_equal(concrete_observation, expected),
                        (point, concrete_observation, expected))

    def check_task(self, request):
        packet = circuit.make_evidence(request)
        full = circuit.verify_evidence(request, packet)
        direct = circuit.evaluate_direct(request)
        expected = concrete_task_decision(request)
        self.assertTrue(core.exact_equal(decision(full), expected), (decision(full), expected))
        self.assertTrue(core.exact_equal(decision(direct), expected), (decision(direct), expected))
        self.assertLessEqual(direct["semantic_cells"], full["semantic_cells"])
        self.assertEqual(full["semantic_cells"], full["nodes"] * len(request["points"]))
        self.assertEqual(direct["counters"]["cache_queries"],
                         direct["counters"]["cache_hits"] + direct["counters"]["semantic_cells"])
        return full, direct, packet

    def test_binary_operations_on_signed_boundary_grid(self):
        # 16 operators x 15 x 15 points = 3,600 independent mathematical controls.
        for operator in BINARY:
            admitted = bridge.admit_source(expression_program("x " + operator + " y"))
            for a, b in itertools.product(BOUNDARIES, repeat=2):
                with self.subTest(operator=operator, a=a, b=b):
                    self.observation(admitted, (a, b), mathematical(operator, a, b))

    def test_unary_and_integer_boolean_values(self):
        for operator in ("+", "-", "!", "~"):
            admitted = bridge.admit_source(expression_program(operator + "x"))
            for value in BOUNDARIES:
                answer = ({"+": lambda: checked_integer(value), "-": lambda: checked_integer(-value),
                           "!": lambda: str(int(not value)), "~": lambda: str(~value)}[operator])()
                with self.subTest(operator=operator, value=value):
                    self.observation(admitted, (value, 0), answer)
        admitted = bridge.admit_source(expression_program("(x < y) + (x == y) * 3 + (!x)"))
        for a, b in itertools.product((-1, 0, 1), repeat=2):
            self.observation(admitted, (a, b), str(int(a < b) + 3 * int(a == b) + int(not a)))
        model = core.Circuit()
        compiled = circuit.SignedCompiler(model, admitted, {}).compile()
        vectors = circuit._vectors(model, admitted.input_names, [[-1, 0], [0, 0], [1, -1]])
        self.assertEqual(model.sorts[compiled.output], "u32")
        for sort, vector in zip(model.sorts, vectors):
            expected_type = bool if sort == "bool" else int
            self.assertTrue(all(type(value) is expected_type for value in vector))

    def test_short_circuit_and_conditional_skip_only_unexecuted_faults(self):
        points = ((LOW, -1), (LOW, 0), (LOW, 1), (-7, 2), (0, 0), (7, -2), (7, 0))
        for expression in ("(y != 0) && (x / y)", "(y == 0) || (x / y)", "y == 0 ? 7 : x / y"):
            admitted = bridge.admit_source(expression_program(expression))
            for a, b in points:
                quotient = mathematical("/", a, b)
                if expression.startswith("(y !="):
                    expected = "0" if b == 0 else None if quotient is None else str(int(int(quotient) != 0))
                elif expression.startswith("(y =="):
                    expected = "1" if b == 0 else None if quotient is None else str(int(int(quotient) != 0))
                else:
                    expected = "7" if b == 0 else quotient
                with self.subTest(expression=expression, point=(a, b)):
                    self.observation(admitted, (a, b), expected)
        for expression, positive in (("x ? 1 : y / 0", "1"), ("x || (y / 0)", "1"),
                                     ("!x && (y / 0)", "0")):
            admitted = bridge.admit_source(expression_program(expression))
            self.observation(admitted, (2, 1), positive)
            self.observation(admitted, (0, 1), None)

    def test_unused_overflow_and_compound_updates_contribute_definedness(self):
        cases = (("int unused = x + 1;", (HIGH, 2)),
                 ("int unused = x / y;", (LOW, -1)),
                 ("int unused = x % y;", (LOW, -1)),
                 ("x += y;", (HIGH, 1)), ("x -= y;", (LOW, 1)),
                 ("x *= y;", (HIGH, 2)), ("x /= y;", (LOW, -1)),
                 ("x %= y;", (LOW, -1)), ("x++;", (HIGH, 0)),
                 ("--x;", (LOW, 0)))
        for statement, point in cases:
            admitted = bridge.admit_source(raw_program(statement + ' printf("%d", 7); return 0;'))
            with self.subTest(statement=statement):
                self.observation(admitted, point, None)
                self.observation(admitted, (1, 1), "7")

    def test_early_return_and_static_if_preorder(self):
        raw = raw_program('int r = 0; if (x < 0) { printf("%d", 7); return 0; '
                          'if (y) { r = 1 / 0; } } '
                          'if (y) { r = 8; } else { r = 9; } '
                          'printf("%d", r); return 0; r = 1 / 0;')
        admitted = bridge.admit_source(raw)
        self.assertEqual(len(admitted.if_nodes), 3)
        self.observation(admitted, (-1, 0), "7", ((0, 1),))
        self.observation(admitted, (0, 0), "9", ((0, 0), (2, 0)))
        self.observation(admitted, (0, 1), "8", ((0, 0), (2, 1)))
        undefined_guard = bridge.admit_source(raw_program('int r = 0; if (x) { r = 1; } '
            'if (x / y) { r = 2; } printf("%d", r); return 0;'))
        self.observation(undefined_guard, (1, 0), None, ((0, 1),))

    def test_main_parameter_overwrite_and_unreachable_argc_reference(self):
        cases = (
            b'#include <stdio.h>\nint main(int a, char **v) { scanf("%d", &a); printf("%d", a); return 0; }',
            b'#include <stdio.h>\nint main(int argc, char *argv[]) { int x; scanf("%d", &x); printf("%d", x); return 0; x = argc; }',
        )
        for raw in cases:
            admitted = bridge.admit_source(raw)
            for value in (LOW, -1, 0, HIGH):
                self.observation(admitted, (value,), str(value))

    def test_repeated_scanf_targets_follow_conversion_order(self):
        raw = (b'#include <stdio.h>\nint main(void) { int x; scanf("%d %d", &x, &x); '
               b'printf("%d", x); return 0; }')
        admitted = bridge.admit_source(raw)
        self.assertEqual(admitted.input_targets, ("x", "x"))
        for values in ((LOW, HIGH), (7, -3), (-2, 0)):
            self.observation(admitted, values, str(values[1]))

    def test_sixteen_input_positions_do_not_use_lexicographic_name_order(self):
        names = ["a" + str(i) for i in range(16)]
        raw = ('#include <stdio.h>\nint main(void) { int ' + ', '.join(names) +
               '; scanf("' + ' '.join(['%d'] * 16) + '", ' + ', '.join('&' + n for n in names) +
               '); printf("%d", a2 - a10); return 0; }').encode()
        admitted = bridge.admit_source(raw)
        self.assertEqual(admitted.input_names, tuple("i" + str(i) for i in range(16)))
        for point in (tuple(range(-8, 8)), (0,) * 16, tuple(range(16, 0, -1))):
            self.observation(admitted, point, str(point[2] - point[10]))
        full, _direct, _packet = self.check_task(task(raw, raw, [tuple(range(-8, 8)), (0,) * 16]))
        self.assertEqual(full["status"], "ACCEPT")

    def test_literal_tokens_and_label_conditionals(self):
        for body, expected_kind, expectations in (
            ('puts(x < 0 ? "NEG\\n" : "NONNEG"); return 0;', "label", ((-1, "NEG"), (0, "NONNEG"))),
            ('if (x) { printf("-1"); } else { printf("%d", 0); } return 0;', "numeric", ((-1, "-1"), (0, "0"))),
            ('puts(x ? "0" : "YES"); return 0;', "label", ((1, "0"), (0, "YES"))),
        ):
            admitted = bridge.admit_source(raw_program(body, arity=1))
            self.assertEqual(admitted.output_kind, expected_kind)
            for value, token in expectations:
                trace = ((0, int(bool(value))),) if body.startswith("if") else ()
                self.observation(admitted, (value,), token, trace)

    def test_correlated_projection_uses_an_actual_minimal_signed_point(self):
        candidate = raw_program('int scratch = 0; if (x < 0) { scratch = 1; } '
                                'printf("%d", 1); return 0;')
        reference = expression_program("0")
        request = task(candidate, reference, [(-5, -100), (2, 10), (2, 20)])
        full, direct, _packet = self.check_task(request)
        expected = {"obligation": "repair", "trace": [[0, 0]], "input": [2, 10]}
        self.assertTrue(core.exact_equal(full["witness"], expected))
        self.assertIn(direct["witness"]["input"], request["points"])
        self.assertNotIn([2, -100], request["points"])
        empty_support = task(expression_program("1"), reference,
                             [(LOW, 7), (-1, 2), (0, -100)])
        full, direct, _packet = self.check_task(empty_support)
        self.assertEqual(full["witness"]["input"], [LOW, 7])
        self.assertEqual(direct["witness"]["input"], [LOW, 7])

    def test_reference_everywhere_policy_and_obligation_priority(self):
        candidate = expression_program("x / y")
        reference = expression_program("1")
        request = task(candidate, reference, [(0, 1), (1, 0)])
        full, _direct, _packet = self.check_task(request)
        self.assertEqual(full["witness"]["obligation"], "defined")
        self.assertEqual(full["witness"]["input"], [1, 0])
        request = task(expression_program("1"), expression_program("x / y"), [(1, 0)])
        full, _direct, _packet = self.check_task(request)
        self.assertEqual(full["witness"]["obligation"], "repair")
        request = task(expression_program("1"), expression_program("1"), [(1, 0)], original=expression_program("x / y"))
        full, _direct, _packet = self.check_task(request)
        self.assertEqual(full["status"], "ACCEPT")

    def test_source_point_and_policy_binding_rejects_stale_packets(self):
        request = task(expression_program("x"), expression_program("x"), [(-1, 0), (1, 2)])
        packet = circuit.make_evidence(request)
        changed = []
        current = copy.deepcopy(request); current["id"] += "-new"; changed.append(current)
        current = copy.deepcopy(request); current["points"] = [[-2, 0], [1, 2]]; changed.append(current)
        current = copy.deepcopy(request); current["policy"] = "preserve-everywhere"; changed.append(current)
        for role in core.ROLES:
            current = copy.deepcopy(request); current["sources"][role] += "/* exact bytes changed */"; changed.append(current)
        for current in changed:
            with self.subTest(current=current):
                with self.assertRaises(core.Invalid):
                    circuit.verify_evidence(current, packet)

    def test_packet_types_topology_and_values_are_exact_even_after_resigning(self):
        request = task(raw_program('int r = x; if (y) { r = x + 1; } printf("%d", r); return 0;'),
                       expression_program("x"), [(0, 0), (1, 1)])
        packet = circuit.make_evidence(request)
        boolean_row = next(i for i, node in enumerate(packet["nodes"]) if node["sort"] == "bool")
        word_row = next(i for i, node in enumerate(packet["nodes"]) if node["sort"] == "u32" and packet["vectors"][i][0] in (0, 1))
        variants = []
        p = copy.deepcopy(packet); p["nodes"][0]["id"] = False; variants.append(p)
        p = copy.deepcopy(packet); p["events"][0][0] = False; variants.append(p)
        p = copy.deepcopy(packet); p["vectors"][boolean_row][0] = int(p["vectors"][boolean_row][0]); variants.append(p)
        p = copy.deepcopy(packet); p["vectors"][word_row][0] = bool(p["vectors"][word_row][0]); variants.append(p)
        p = copy.deepcopy(packet); p["vectors"][word_row][0] = float(p["vectors"][word_row][0]); variants.append(p)
        p = copy.deepcopy(packet); p["vectors"][word_row][0] ^= 1; variants.append(p)
        p = copy.deepcopy(packet); p["vectors"].pop(); variants.append(p)
        p = copy.deepcopy(packet); p["events"] = [tuple(event) for event in p["events"]]; variants.append(p)
        p = copy.deepcopy(packet); p["roots"] = tuple(p["roots"]); variants.append(p)
        for index, corrupted in enumerate(variants):
            with self.subTest(corruption=index):
                with self.assertRaises(core.Invalid):
                    circuit.verify_evidence(request, resign(corrupted))
        corrupted = copy.deepcopy(packet); corrupted["sha256"] = "0" * 64
        with self.assertRaises(core.Invalid):
            circuit.verify_evidence(request, corrupted)

    def test_input_schema_and_whole_source_admission_are_not_bypassed(self):
        base = task(expression_program("x"), expression_program("x"), [(0, 0), (1, 1)])
        variants = ([], [[True, 0]], [[False, 0]], [[1.0, 0]], [[LOW - 1, 0]],
                    [[HIGH + 1, 0]], [[0]], [[1, 1], [0, 0]], [[0, 0], [0, 0]],
                    [(0, 0)], [[0, 0]] * (circuit.MAX_POINTS + 1))
        for points in variants:
            request = copy.deepcopy(base); request["points"] = points
            with self.subTest(points=points[:2]):
                with self.assertRaises(core.Invalid):
                    circuit.evaluate_direct(request)
                with self.assertRaises(core.Invalid):
                    circuit.make_evidence(request)
        invalid = raw_program('printf("%d", x); return 0; while (x) { x--; }')
        for role in core.ROLES:
            request = copy.deepcopy(base); request["sources"][role] = invalid.decode()
            with self.assertRaises(bridge.UnsupportedSource):
                circuit.evaluate_direct(request)

    def test_nonfinite_packet_and_non_utf8_source_have_invalid_result_class(self):
        base = task(expression_program("x"), expression_program("x"), [(0, 0)])
        for value in (float("nan"), float("inf"), -float("inf")):
            packet = circuit.make_evidence(base)
            packet["vectors"][0][0] = value
            with self.subTest(value=value):
                with self.assertRaises(core.Invalid):
                    circuit.verify_evidence(base, packet)
        request = copy.deepcopy(base)
        request["sources"]["candidate"] = "\ud800"
        with self.assertRaises(core.Invalid):
            circuit.evaluate_direct(request)

    @unittest.skipUnless(shutil.which("gcc"), "GCC is required for owned native controls")
    def test_owned_native_defined_values_and_ubsan_fault_boundaries(self):
        compiler = shutil.which("gcc")
        env = {**os.environ, "LC_ALL": "C"}
        points = ((LOW, -1), (LOW, 0), (LOW, 1), (-46341, -46341), (-7, 2),
                  (0, 0), (0, -1), (1, HIGH), (7, -2), (46340, 46340), (HIGH, 1), (HIGH, HIGH))
        with tempfile.TemporaryDirectory(prefix="repairseal-owned-int32-") as directory:
            root = Path(directory)
            for index, operator in enumerate(BINARY):
                source, executable = root / f"binary-{index}.c", root / f"binary-{index}"
                source.write_bytes(expression_program("x " + operator + " y"))
                compilation = subprocess.run([compiler, "-std=c11", "-O1", "-fsanitize=undefined",
                    "-fno-sanitize-recover=all", str(source), "-o", str(executable)],
                    capture_output=True, timeout=30, env=env, check=False)
                self.assertEqual(compilation.returncode, 0, compilation.stderr.decode(errors="replace"))
                for a, b in points:
                    expected = mathematical(operator, a, b)
                    process = subprocess.run([str(executable)], input=f"{a} {b}\n".encode(),
                                             capture_output=True, timeout=3, env=env, check=False)
                    with self.subTest(operator=operator, a=a, b=b):
                        if expected is None:
                            self.assertNotEqual(process.returncode, 0)
                            self.assertIn(b"runtime error:", process.stderr)
                        else:
                            self.assertEqual(process.returncode, 0, process.stderr.decode(errors="replace"))
                            self.assertEqual(bridge.canonical_output(process.stdout, "numeric"), expected)


if __name__ == "__main__":
    unittest.main()
