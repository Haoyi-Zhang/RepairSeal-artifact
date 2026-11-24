"""Failure controls for exact witnessed-product provenance and process isolation."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_witness_products as check


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


class ProductEquivalenceVerification(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="repairseal-product-audit-")
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_each_emitter_gets_its_own_dependency_modules(self):
        # Both emitters deliberately import the same module name. A shared
        # interpreter/module cache would silently use the first root twice.
        for name, prefix in (("executed", "old:"), ("current", "new:")):
            root = self.root / name
            (root / "src").mkdir(parents=True)
            (root / "tests").mkdir()
            (root / "src/proof_dag_checker.py").write_text("PREFIX = " + repr(prefix) + "\n")
            (root / "tests/witness_interoperability.py").write_text(
                "from pathlib import Path\nimport sys\n"
                "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))\n"
                "import proof_dag_checker\n"
                "def emit_product(request): return proof_dag_checker.PREFIX + request['id']\n")
        request = self.root / "request.json"
        dump(request, {"id": "owned-control"})
        self.assertEqual(check.emit_isolated(self.root / "executed", [request]), ["old:owned-control"])
        self.assertEqual(check.emit_isolated(self.root / "current", [request]), ["new:owned-control"])

    def test_snapshot_binding_is_literal_and_inventory_is_closed(self):
        for name in check.BOUND_SOURCES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# owned source fixture\n")
        expected = check.source_bindings(self.root)
        self.assertEqual(check.check_snapshot(self.root, expected), expected)
        self.assertRaisesRegex(ValueError, "inventory", check.check_snapshot, self.root,
                               {**expected, "unexpected.py": "0" * 64})
        (self.root / "tests/witness_interoperability.py").write_text("# altered source fixture\n")
        self.assertRaisesRegex(ValueError, "executed source bytes", check.check_snapshot, self.root, expected)

    def test_same_semantic_request_with_different_bytes_is_rejected(self):
        directory = self.root / "cases/0000"
        row = {"index": 0, "population": "core", "input_file": "owned/request.json"}
        dump(directory / "case-summary.json", row)
        dump(directory / "request.json", {"id": "owned"})
        (directory / "program.c").write_text("int main(void) { return 0; }\n")
        protocol = {"requests": [{"population": "core", "path": row["input_file"],
                                    "identity": check.identity(directory / "request.json")}]}
        bindings, paths = check.input_bindings(self.root, protocol, [row])
        self.assertEqual(bindings[0]["index"], 0)
        self.assertEqual(paths, [directory / "request.json"])
        (directory / "request.json").write_text('{"id":"owned"}\n')
        self.assertRaisesRegex(ValueError, "registered input bytes", check.input_bindings,
                               self.root, protocol, [row])

    def test_both_emitters_must_match_retained_bytes(self):
        directory = self.root / "cases/0000"
        directory.mkdir(parents=True)
        product = "int main(void) { return 0; }\n"
        (directory / "program.c").write_text(product)
        rows = [{"index": 0}]
        self.assertEqual(check.compare_products(self.root, rows, [product], [product]), len(product.encode()))
        changed = product.replace("return 0", "return 1")
        self.assertRaisesRegex(ValueError, "executed emitter", check.compare_products,
                               self.root, rows, [changed], [product])
        self.assertRaisesRegex(ValueError, "current emitter", check.compare_products,
                               self.root, rows, [product], [changed])
        self.assertRaisesRegex(ValueError, "sequence lengths", check.compare_products,
                               self.root, rows, [], [product])

    def test_complete_cases_alone_cannot_bypass_missing_study_controls(self):
        populations = [name for name, count in check.POPULATION.items() for _ in range(count)]
        rows = [{"index": index, "population": name} for index, name in enumerate(populations)]
        dump(self.root / "protocol.json", {"pilot_limit": None, "planned_requests": check.REQUESTS,
                                            "population": check.POPULATION, "requests": [{}] * check.REQUESTS})
        dump(self.root / "summary.json", {"outcome": "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES",
                                           "source_inputs_and_tools_unchanged": True,
                                           "producer_disagreements": [], "direct_cpa_disagreements": [],
                                           "groups": {"all": {"requests": check.REQUESTS}}, "control_runs": 0})
        dump(self.root / "cases.json", rows)
        dump(self.root / "controls.json", [])
        self.assertRaisesRegex(ValueError, "study controls", check.completed_study, self.root)

    def test_duplicate_and_nonfinite_json_evidence_is_rejected(self):
        self.assertRaisesRegex(ValueError, "duplicate", check.decode, '{"result":1,"result":2}')
        self.assertRaisesRegex(ValueError, "nonfinite", check.decode, '{"result":NaN}')

    def test_existing_output_and_optimized_execution_leave_evidence_untouched(self):
        target = self.root / "evidence.json"
        target.write_text("original evidence\n")
        script = str(Path(check.__file__).resolve())
        command = [sys.executable, "-B", script, "--study", str(self.root / "missing"), "--output", str(target)]
        result = subprocess.run(command, capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"output must be a new file", result.stderr)
        self.assertEqual(target.read_text(), "original evidence\n")
        new = self.root / "new.json"
        optimized = subprocess.run([sys.executable, "-O", "-B", script, "--study", str(self.root / "missing"),
                                    "--output", str(new)], capture_output=True, timeout=10)
        self.assertNotEqual(optimized.returncode, 0)
        self.assertIn(b"assertions enabled", optimized.stderr)
        self.assertFalse(new.exists())


if __name__ == "__main__":
    unittest.main()
