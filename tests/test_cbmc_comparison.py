"""Harness-semantic checks; external tests need an explicitly supplied CBMC.

CBMC_BINARY and optional CBMC_LIBRARY_DIR select a local executable.  Set
CBMC_CONTROL_OUTPUT to a fresh directory to retain every control's raw output.
The tests do not fetch a tool or execute an unadmitted source.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "src")]
import cbmc_comparison as comparison
from scientific_driver import new_output_directory


IDENTITY = "unsigned f(unsigned x) { return x; }"
INCREMENT = "unsigned f(unsigned x) { return x + 1u; }"
DIVISION = "unsigned f(unsigned x) { return 10u / x; }"


def request(name, candidate=IDENTITY, original=IDENTITY, reference=IDENTITY,
            guard="x == x", values=(0, 1)):
    return {"id": name, "word_bits": 32, "inputs": {"x": list(values)},
            "original": original, "candidate": candidate, "reference": reference,
            "repair_guard": guard}


def semantic_controls():
    short_or = ("unsigned f(unsigned x) { unsigned r = 0u; "
                "if ((x == 0u) || ((10u / x) > 0u)) { r = 1u; } "
                "else { r = 2u; } return r; }")
    short_and = ("unsigned f(unsigned x) { unsigned r = 0u; "
                 "if ((x != 0u) && ((10u / x) > 0u)) { r = 1u; } "
                 "else { r = 2u; } return r; }")
    conditional = ("unsigned f(unsigned x) { unsigned r = 0u; "
                   "if (x == 0u) { r = 0u; } else { r = 10u / x; } return r; }")
    hidden = ("unsigned f(unsigned x) { unsigned r = x; "
              "if (x == 1u) { r = x + 1u; } else { r = x; } return r; }")
    carriage = "unsigned f(unsigned x) { unsigned y = x; // comment\ry = y + 1u;\nreturn y; }"
    shift_left = "unsigned f(unsigned x) { return 1u << x; }"
    shift_right = "unsigned f(unsigned x) { return 1u >> x; }"
    controls = [
        (request("identity"), "ACCEPT"),
        (request("unsigned-wrap", INCREMENT, reference=INCREMENT,
                 values=(0, 4294967295)), "ACCEPT"),
        (request("candidate-div-zero", DIVISION, reference=DIVISION), "REFUTED"),
        (request("candidate-rem-zero", "unsigned f(unsigned x) { return 10u % x; }"), "REFUTED"),
        (request("overwritten-undefined", "unsigned f(unsigned x) { unsigned r = 1u / 0u; r = x; return r; }"), "REFUTED"),
        (request("reference-unselected", reference=DIVISION, guard="x != x"), "ACCEPT"),
        (request("original-unselected", original=DIVISION), "ACCEPT"),
        (request("reference-selected-undefined", reference=DIVISION), "REFUTED"),
        (request("original-selected-undefined", original=DIVISION, guard="x != x"), "REFUTED"),
        (request("short-circuit-or", short_or, reference=short_or), "ACCEPT"),
        (request("short-circuit-and", short_and, reference=short_and), "ACCEPT"),
        (request("skipped-branch-division", conditional, reference=conditional), "ACCEPT"),
        (request("valid-left-shift", shift_left, reference=shift_left, values=(0, 31)), "ACCEPT"),
        (request("invalid-left-shift", shift_left, reference=shift_left, values=(0, 32)), "REFUTED"),
        (request("invalid-right-shift", shift_right, reference=shift_right, values=(0, 32)), "REFUTED"),
        (request("exact-domain-excludes-fault", hidden, values=(0, 2)), "ACCEPT"),
        (request("expanded-domain-includes-fault", hidden, values=(0, 1, 2)), "REFUTED"),
        (request("preserve-selected", INCREMENT, reference=INCREMENT, guard="x == 0u"), "REFUTED"),
        (request("bare-cr-correspondence", carriage, reference=INCREMENT), "ACCEPT"),
        (request("bare-cr-visible-change", carriage), "REFUTED"),
    ]
    collision = {"id": "f-parameter", "word_bits": 32, "inputs": {"f": [0, 1]},
                 "repair_guard": "f == f"}
    collision.update({role: "unsigned f(unsigned f) { return f; }" for role in comparison.core.ROLES})
    controls.append((collision, "ACCEPT"))
    after_undefined = "unsigned f(unsigned x) { unsigned r = 1u / x; r = x << 31u; return r; }"
    controls.append((request("known-failure-before-later-property", after_undefined,
                             reference=after_undefined), "REFUTED"))
    return controls


class HarnessBoundaryTests(unittest.TestCase):
    def test_source_bytes_survive_export(self):
        case = request("raw-bytes", candidate=semantic_controls()[18][0]["candidate"])
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "case"
            comparison.emit_harness(case, output)
            self.assertEqual((output / "candidate.c").read_bytes(), case["candidate"].encode())
            self.assertIn(b"\r", (output / "candidate.c").read_bytes())
            self.assertNotIn("unsigned-overflow-check", comparison.CBMC_FLAGS)

    def test_unadmitted_source_never_written(self):
        with tempfile.TemporaryDirectory() as temporary:
            for source in ("int f(int x) { return x; }",
                           "unsigned f(unsigned x) { return system(x); }",
                           "#include <stdio.h>\nunsigned f(unsigned x) { return x; }"):
                output = Path(temporary) / "case"
                with self.assertRaises((comparison.core.Unsupported, comparison.core.Invalid)):
                    comparison.emit_harness(request("inadmissible", candidate=source), output)
                self.assertFalse(output.exists())

    def test_existing_harness_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "case"
            comparison.emit_harness(request("first"), output)
            old = (output / "harness.c").read_bytes()
            with self.assertRaises(FileExistsError):
                comparison.emit_harness(request("second"), output)
            self.assertEqual((output / "harness.c").read_bytes(), old)

    def test_optimized_driver_refuses_before_tool_use(self):
        result = subprocess.run([sys.executable, "-O", "-B", str(ROOT / "tests/cbmc_comparison.py"), "--help"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires enabled assertions", result.stderr)

    def test_incomplete_or_inconsistent_output_is_not_a_verdict(self):
        for stdout, code in (("[]", 0), ('[{"cProverStatus":"success"}]', 0),
                             ('[{"result":[]},{"cProverStatus":"success"}]', 10),
                             ("not JSON", 0)):
            with self.subTest(stdout=stdout, code=code):
                self.assertEqual(comparison.parse_cbmc_result(stdout, code)["status"], "ERROR")

    def test_known_violation_suffices_but_unknown_cannot_establish_acceptance(self):
        properties = [{"property": "main.assertion.1", "description": "repairseal.repair", "status": "FAILURE"},
                      {"property": "main.assertion.2", "description": "repairseal.preserve", "status": "UNKNOWN"}]
        raw = [{"result": properties}, {"cProverStatus": "failure"}]
        self.assertEqual(comparison.parse_cbmc_result(json.dumps(raw), 10)["status"], "REFUTED")
        properties[0]["status"] = "SUCCESS"
        raw[1]["cProverStatus"] = "success"
        self.assertEqual(comparison.parse_cbmc_result(json.dumps(raw), 0)["status"], "ERROR")


@unittest.skipUnless(os.environ.get("CBMC_BINARY"), "set CBMC_BINARY for independent external execution")
class ExternalSemanticTests(unittest.TestCase):
    def test_independent_c_semantics(self):
        binary = Path(os.environ["CBMC_BINARY"])
        libraries = [Path(os.environ["CBMC_LIBRARY_DIR"])] if os.environ.get("CBMC_LIBRARY_DIR") else []
        engine = comparison.Engine(binary, libraries, timeout=15, memory_mib=1024)
        with tempfile.TemporaryDirectory(prefix="repairseal-cbmc-controls-") as temporary:
            retained = os.environ.get("CBMC_CONTROL_OUTPUT")
            output = new_output_directory(Path(retained)) if retained else Path(temporary)
            comparison.write_json(output / "tool-profile.json", engine.profile)
            rows = []
            for case, expected in semantic_controls():
                with self.subTest(case=case["id"]):
                    directory = output / case["id"]
                    comparison.emit_harness(case, directory)
                    direct = comparison.evaluate_demand(case)
                    actual = engine.run(directory)
                    rows.append({"id": case["id"], "expected": expected,
                                 "direct": direct["status"], "cbmc": actual["status"]})
                    self.assertEqual(direct["status"], expected)
                    self.assertEqual(actual["status"], expected, actual)
            comparison.write_json(output / "controls.json", rows)


if __name__ == "__main__":
    unittest.main()
