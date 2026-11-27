"""Reject C attributes that the signed semantic profile does not model.

These controls include native C constraint violations, valid-but-unsupported
alignment declarations, unreachable declarations, and every request role.
The separately invoked audit stores compiler results; unittest needs no compiler.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

# The historical src/ remains byte-exact for reproduction. Load the current
# version explicitly and redirect only each test's fresh-admission calls.
bridge_path = Path(os.environ.get("REPAIRSEAL_CURRENT_BRIDGE_PATH",
                                ROOT / "current/src/codeflaws_int32_bridge.py"))
spec = importlib.util.spec_from_file_location("repairseal_current_bridge_attributes", bridge_path)
bridge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)
import int32_circuit as signed
import int32_refutation as compact


BODY = 'int x;scanf("%d",&x);printf("%d",x);return 0;'


def source(body=BODY, signature="int main(void)"):
    return ("#include <stdio.h>\n" + signature + "{" + body + "}\n").encode()


def controls():
    rows = {}
    for alignment in ("0", "1", "3", "8", "int"):
        rows["local-align-" + alignment] = {
            "source": source(BODY.replace("int x;", "_Alignas(" + alignment + ") int x;")),
            "code": "alignment-specifier", "admitted": False,
        }
    for alignment in ("0", "8"):
        rows["function-align-" + alignment] = {
            "source": source(signature="_Alignas(" + alignment + ") int main(void)"),
            "code": "alignment-specifier", "admitted": False,
        }
    rows["parameter-align"] = {
        "source": source('scanf("%d",&n);printf("%d",n);return 0;',
                         "int main(_Alignas(8) int n,char **argv)"),
        "code": "alignment-specifier", "admitted": False,
    }
    rows["argv-align"] = {
        "source": source(signature="int main(int argc,_Alignas(8) char **argv)"),
        "code": "alignment-specifier", "admitted": False,
    }
    rows["unreachable-align"] = {
        "source": source(BODY + "_Alignas(3) int after;"),
        "code": "alignment-specifier", "admitted": False,
    }
    rows["nested-align"] = {
        "source": source(BODY.replace('printf("%d",x);',
            'if(x){_Alignas(3) int y=1;printf("%d",y);}else printf("%d",x);')),
        "code": "alignment-specifier", "admitted": False,
    }
    for qualifier in ("const", "volatile", "restrict"):
        rows["qualified-void-" + qualifier] = {
            "source": source(signature="int main(" + qualifier + " void)"),
            "code": "main-parameters", "admitted": False,
        }
    rows["ordinary-void"] = {"source": source(), "admitted": True}
    rows["ordinary-no-prototype"] = {
        "source": source(signature="int main()"), "admitted": True}
    rows["ordinary-parameters"] = {
        "source": source('scanf("%d",&n);printf("%d",n);return 0;',
                         "int main(int n,char **argv)"), "admitted": True}
    rows["attribute-words-in-comment"] = {
        "source": source(BODY + "/* _Alignas(3) and const void are text */"),
        "admitted": True}
    return rows


CASES = controls()


def task(raw, role="candidate"):
    baseline = source().decode()
    request = {"kind": signed.PROFILE, "id": "source-attribute-boundary",
               "policy": "reference-everywhere", "points": [[7]],
               "sources": dict.fromkeys(("original", "candidate", "reference"), baseline)}
    request["sources"][role] = raw.decode()
    return request


class SourceAttributeAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.module_patch = patch.dict(sys.modules, {"codeflaws_int32_bridge": bridge})
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)

    def test_alignas_is_rejected_in_all_syntax_positions(self):
        for name, row in CASES.items():
            if row.get("code") != "alignment-specifier":
                continue
            with self.subTest(case=name), self.assertRaises(bridge.UnsupportedSource) as error:
                bridge.admit_source(row["source"], name)
            self.assertEqual(error.exception.code, row["code"])

    def test_void_parameter_must_be_unqualified(self):
        for name, row in CASES.items():
            if row.get("code") != "main-parameters":
                continue
            with self.subTest(case=name), self.assertRaises(bridge.UnsupportedSource) as error:
                bridge.admit_source(row["source"], name)
            self.assertEqual(error.exception.code, row["code"])

    def test_unreachable_declarations_still_require_admission(self):
        with self.assertRaises(bridge.UnsupportedSource) as error:
            bridge.admit_source(CASES["unreachable-align"]["source"])
        self.assertEqual(error.exception.code, "alignment-specifier")

    def test_valid_alignment_is_unsupported_not_a_semantic_refutation(self):
        for name in ("local-align-0", "local-align-8", "local-align-int"):
            with self.subTest(case=name), self.assertRaises(bridge.UnsupportedSource):
                signed.evaluate_direct(task(CASES[name]["source"]))

    def test_all_public_receivers_readmit_each_source_role(self):
        changed = source(BODY.replace('printf("%d",x);', 'printf("%d",x+1);'))
        good = task(changed)
        packet = signed.make_evidence(good)
        certificate = compact.produce(good)
        entries = (
            ("build", lambda r: signed.build_task(r)),
            ("direct", lambda r: signed.evaluate_direct(r)),
            ("record", lambda r: signed.evaluate_with_record(r)),
            ("produce-full", lambda r: signed.make_evidence(r)),
            ("check-full", lambda r: signed.verify_evidence(r, packet)),
            ("produce-compact", lambda r: compact.produce(r)),
            ("check-compact", lambda r: compact.check(r, certificate)),
        )
        for name in ("local-align-3", "parameter-align", "qualified-void-const"):
            for role in ("original", "candidate", "reference"):
                request = task(CASES[name]["source"], role)
                for entry, invoke in entries:
                    with self.subTest(case=name, role=role, entry=entry), self.assertRaises(bridge.UnsupportedSource):
                        invoke(request)

    def test_ordinary_sources_preserve_exact_bytes_and_boundary_values(self):
        for name, row in CASES.items():
            if not row["admitted"]:
                continue
            admitted = bridge.admit_source(row["source"], name)
            self.assertEqual(admitted.raw, row["source"])
            for value in (bridge.INT_MIN, -1, 0, 1, bridge.INT_MAX):
                with self.subTest(case=name, value=value):
                    concrete = bridge.evaluate(admitted, [value])
                    symbolic = signed.evaluate_program(admitted, [value])
                    self.assertTrue(concrete.defined)
                    self.assertEqual(concrete.value, str(value))
                    self.assertEqual(symbolic["value"], concrete.value)
                    self.assertEqual(symbolic["trace"], concrete.trace)


if __name__ == "__main__":
    unittest.main()
