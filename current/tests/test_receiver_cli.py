"""Observable current-profile CLI contracts, including source/evidence rejection."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CURRENT = Path(__file__).resolve().parents[1]
ENTRY = CURRENT / "receiver.py"


def request(candidate="x + 1"):
    def source(expression):
        return '#include <stdio.h>\nint main(void){int x;scanf("%d",&x);printf("%d",'+expression+');return 0;}'
    return {"kind": "repairseal-int32-point-task-v1", "id": "cli-regression",
            "policy": "reference-everywhere", "points": [[-1], [0], [1]],
            "sources": {"original": source("x"), "candidate": source(candidate), "reference": source("x")}}


class CurrentCLI(unittest.TestCase):
    def invoke(self, directory, operation, task=None, extra=()):
        path = Path(directory) / "request.json"
        path.write_text(json.dumps(task if task is not None else request()))
        return subprocess.run([sys.executable, "-B", str(ENTRY), operation,
                               "--request", str(path), *map(str, extra)],
                              capture_output=True, text=True, timeout=30)

    def test_complete_receivers_and_roundtrip_refutation(self):
        with tempfile.TemporaryDirectory() as directory:
            direct = self.invoke(directory, "decide")
            demand = self.invoke(directory, "decide", extra=["--algorithm", "materialized"])
            self.assertEqual(direct.returncode, 0, direct.stderr)
            self.assertEqual(demand.returncode, 0, demand.stderr)
            a, b = json.loads(direct.stdout), json.loads(demand.stdout)
            self.assertEqual(a["result"]["witness"], b["result"]["witness"])
            certificate = Path(directory) / "certificate.json"
            produced = self.invoke(directory, "produce-refutation", extra=["--output", certificate])
            self.assertEqual(produced.returncode, 0, produced.stderr)
            checked = self.invoke(directory, "check-refutation", extra=["--evidence", certificate])
            self.assertEqual(checked.returncode, 0, checked.stderr)
            result = json.loads(checked.stdout)
            self.assertEqual(result["result"]["checked_points"], 1)
            self.assertEqual(result["result"]["witness"], a["result"]["witness"])
            self.assertTrue(result["implementation"]["src/codeflaws_int32_bridge.py"])
            changed = request(); changed["points"].append([2])
            rejected = self.invoke(directory, "check-refutation", changed, ["--evidence", certificate])
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(json.loads(rejected.stdout)["result"]["status"], "INVALID")

    def test_acceptance_full_record_and_no_refutation(self):
        with tempfile.TemporaryDirectory() as directory:
            task = request("x")
            packet = Path(directory) / "packet.json"
            created = self.invoke(directory, "produce-record", task, ["--output", packet])
            self.assertEqual(created.returncode, 0, created.stderr)
            checked = self.invoke(directory, "check-record", task, ["--evidence", packet])
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertEqual(json.loads(checked.stdout)["result"]["status"], "ACCEPT")
            rejected = self.invoke(directory, "produce-refutation", task)
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(json.loads(rejected.stdout)["result"]["status"], "INVALID")

    def test_new_source_admission_rejection_reaches_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            task = request()
            task["sources"]["candidate"] = task["sources"]["candidate"].replace("int x;", "_Alignas(3) int x;")
            result = self.invoke(directory, "decide", task)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads(result.stdout)["result"]["status"], "UNSUPPORTED")

    def test_duplicate_json_keys_and_existing_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"kind": 1, "kind": 2}')
            result = subprocess.run([sys.executable, "-B", str(ENTRY), "decide", "--request", str(path)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["result"]["status"], "INVALID")
            output = Path(directory) / "preserved.json"; output.write_text("preserve me")
            result = self.invoke(directory, "decide", extra=["--output", output])
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
