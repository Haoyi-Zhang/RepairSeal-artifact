"""Cross-process regressions for deterministic signed-source rejection details.

The programs below are authored controls, not copied benchmark submissions.
The historical bridge is loaded only as a Python parser/interpreter control;
neither version compiles or runs these C programs natively.
"""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "src/codeflaws_int32_bridge.py"
BEFORE = ROOT / "tests/fixtures/unordered-diagnostics.py"
BEFORE_SHA256 = "91f4dee03f7d5d6837962e1089da992c8ccb4431905986b0d7918cae9c43ad52"
HASH_SEEDS = tuple(range(32))


def unit(body):
    return '#include <stdio.h>\nint main(void){' + body + '}\n'


CASES = {
    "branch_initialization": {
        "source": unit('int x,k,l;scanf("%d",&x);'
                       'if(x)k=1;else l=2;printf("%d",k+l);return 0;'),
    },
    "numeric_literals": {
        "source": unit('int x;scanf("%d",&x);'
                       'if(x)puts("04");else puts("123456789012");return 0;'),
    },
    "initialized_branches": {
        "source": unit('int x,k,l;scanf("%d",&x);'
                       'if(x){k=1;l=2;}else{l=4;k=5;}'
                       'printf("%d",k+l);return 0;'),
        "inputs": [[0], [1], [-1]],
    },
    "unreachable_read": {
        "source": unit('int x,k,l;scanf("%d",&x);'
                       'printf("%d",x);return 0;k=l;'),
        "inputs": [[0], [1], [-1]],
    },
    "missing_output_path": {
        "source": unit('int x;scanf("%d",&x);'
                       'if(x)puts("Y");return 0;'),
    },
    "state_limit_before_reads": {
        "source": unit('int x,k,l;scanf("%d",&x);'
                       'if(x)k=1;else l=2;printf("%d",k+l);return 0;'),
        "max_flow_states": 1,
    },
}


CHILD = r'''
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location("diagnostic_bridge", sys.argv[1])
bridge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)
results = {}
for name, case in json.load(sys.stdin).items():
    original_limit = bridge.MAX_FLOW_STATES
    bridge.MAX_FLOW_STATES = case.get("max_flow_states", original_limit)
    try:
        program = bridge.admit_source(case["source"].encode("ascii"), "<owned-control>")
    except bridge.UnsupportedSource as error:
        results[name] = {"admitted": False, "code": error.code, "detail": error.detail}
    else:
        results[name] = {
            "admitted": True, "source_sha256": program.source_sha256,
            "input_targets": list(program.input_targets),
            "output_kind": program.output_kind, "output_labels": list(program.output_labels),
            "evaluations": [bridge.evaluate(program, values).as_dict()
                            for values in case.get("inputs", [])],
        }
    finally:
        bridge.MAX_FLOW_STATES = original_limit
print(json.dumps(results, sort_keys=True))
'''


@lru_cache(maxsize=2)
def seeded_observations(module_path):
    observations = []
    for seed in HASH_SEEDS:
        env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONDONTWRITEBYTECODE="1")
        process = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, str(module_path)],
            input=json.dumps(CASES), text=True, capture_output=True, env=env, timeout=20,
        )
        if process.returncode:
            raise AssertionError((seed, str(module_path), process.returncode, process.stderr))
        observations.append({"seed": seed, "results": json.loads(process.stdout)})
    return observations


class SignedDiagnosticDeterminismTests(unittest.TestCase):
    def test_historical_preimage_demonstrates_both_unstable_details(self):
        self.assertEqual(hashlib.sha256(BEFORE.read_bytes()).hexdigest(), BEFORE_SHA256)
        old = seeded_observations(BEFORE)
        expected = {
            "branch_initialization": ("uninitialized-read", {"k", "l"}),
            "numeric_literals": ("numeric-literal-output", {
                "nonnumeric output token", "noncanonical or out-of-range decimal output"}),
        }
        for name, (code, details) in expected.items():
            with self.subTest(case=name):
                self.assertEqual({row["results"][name]["admitted"] for row in old}, {False})
                self.assertEqual({row["results"][name]["code"] for row in old}, {code})
                self.assertEqual({row["results"][name]["detail"] for row in old}, details)

    def test_current_diagnostics_and_observations_are_seed_independent(self):
        current = seeded_observations(CURRENT)
        expected = current[0]["results"]
        for row in current:
            with self.subTest(seed=row["seed"]):
                self.assertEqual(row["results"], expected)
        self.assertEqual(expected["branch_initialization"], {
            "admitted": False, "code": "uninitialized-read", "detail": "l"})
        self.assertEqual(expected["numeric_literals"], {
            "admitted": False, "code": "numeric-literal-output",
            "detail": "noncanonical or out-of-range decimal output"})

    def test_ordering_preserves_admission_and_concrete_results(self):
        old, current = seeded_observations(BEFORE), seeded_observations(CURRENT)
        for before, after in zip(old, current):
            self.assertEqual(before["seed"], after["seed"])
            for name in CASES:
                with self.subTest(seed=before["seed"], case=name):
                    a, b = before["results"][name], after["results"][name]
                    self.assertEqual(a["admitted"], b["admitted"])
                    if a["admitted"]:
                        self.assertEqual(a, b)
                    else:
                        self.assertEqual(a["code"], b["code"])
        expected = current[0]["results"]
        self.assertEqual([r["value"] for r in expected["initialized_branches"]["evaluations"]],
                         ["9", "3", "3"])
        self.assertEqual([r["value"] for r in expected["unreachable_read"]["evaluations"]],
                         ["0", "1", "-1"])
        self.assertEqual(expected["missing_output_path"], {
            "admitted": False, "code": "not-one-output-on-every-path", "detail": ""})
        self.assertEqual(expected["state_limit_before_reads"], {
            "admitted": False, "code": "control-flow-state-limit", "detail": ""})


if __name__ == "__main__":
    unittest.main()
