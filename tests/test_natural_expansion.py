"""Negative coverage, input-legality, and retained-evidence checks."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "experiments/natural-expansion"
sys.path[:0] = [str(HERE), str(ROOT / "src"), str(ROOT / "tests")]
import domains
spec = importlib.util.spec_from_file_location("natural_expansion_verify_tested", HERE / "verify.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
study = verifier.study


class NaturalExpansionTests(unittest.TestCase):
    def test_correlated_task_domains_reject_illegal_combinations(self):
        self.assertFalse(domains.legal("194-A", [50, 2]))
        self.assertTrue(domains.legal("194-A", [50, 100]))
        self.assertFalse(domains.legal("570-B", [3, 4]))
        self.assertFalse(domains.legal("112-B", [3, 1, 1]))
        self.assertFalse(domains.legal("638-A", [3, 1]))
        self.assertFalse(domains.legal("659-A", [0, 0, 0]))

    def test_counterintuitive_official_constraints_are_preserved(self):
        self.assertTrue(domains.legal("168-A", [10000, 1, 10000]))
        self.assertTrue(domains.legal("90-A", [0, 0, 1]))
        self.assertFalse(domains.legal("90-A", [0, 0, 0]))
        self.assertFalse(domains.legal("313-A", [-9]))
        self.assertTrue(domains.legal("313-A", [-10]))

    def test_selection_and_all_test_inclusion(self):
        corpus = json.loads(study.CORPUS_PATH.read_text())
        selected = study.selection(corpus)
        base = [s for s, reason in selected if reason == "deterministic-expansion"]
        self.assertEqual(len(base), 20)
        self.assertEqual(len({s["problem"] for s in base}), 20)
        self.assertFalse({s["problem"] for s in base} & {"4-A", "84-A"})
        self.assertEqual(len(selected), 22)
        for subject, _reason in selected:
            points = domains.declared_points(subject)
            self.assertLessEqual(len(points), 4096)
            self.assertTrue(all(domains.legal(subject["problem"], p) for p in points))
            self.assertTrue(all(t["input"] in points for t in subject["tests"]))

    def test_given_invalid_input_is_not_silently_dropped(self):
        subject = {"id": "invalid", "problem": "451-A", "tests": [{"input": [0, 100]}]}
        with self.assertRaises(ValueError):
            domains.declared_points(subject)

    def test_definedness_precedes_output_mismatch(self):
        case = {"points": [[1], [2]], "original_sha256": "p", "reference_sha256": "t"}
        observed = {
            ("p", (1,)): {"defined": True, "value": "wrong", "trace": []},
            ("p", (2,)): {"defined": False, "value": None, "trace": [[0, 1]]},
            ("t", (1,)): {"defined": True, "value": "right", "trace": []},
            ("t", (2,)): {"defined": True, "value": "right", "trace": []},
        }
        result = study.concrete_decision(case, "original", observed)
        self.assertEqual(result["witness"]["obligation"], "defined")
        self.assertEqual(result["witness"]["input"], [2])

    def test_false_packet_cell_is_rejected_even_after_digest_repair(self):
        source = '#include <stdio.h>\nint main(void){int x;scanf("%d",&x);printf("%d",x);return 0;}\n'
        task = {"kind": study.symbolic.PROFILE, "id": "test", "policy": "reference-everywhere", "points": [[1], [2]],
                "sources": {"original": source, "candidate": source, "reference": source}}
        packet = study.symbolic.make_evidence(task)
        self.assertEqual(verifier.verify_packet(packet, task["points"])["status"], "ACCEPT")
        bad = copy.deepcopy(packet)
        ordinal = next(i for i, node in enumerate(bad["nodes"]) if node["op"] == "input")
        bad["vectors"][ordinal][0] = 999
        body = {k: v for k, v in bad.items() if k != "sha256"}
        bad["sha256"] = hashlib.sha256(study.symbolic._canonical(body)).hexdigest()
        with self.assertRaisesRegex(ValueError, "local-value"):
            verifier.verify_packet(bad, task["points"])

    def test_raw_stdout_corruption_is_rejected(self):
        process = {"stdout": "42\n", "stderr": "", "stdout_sha256": hashlib.sha256(b"42\n").hexdigest(),
                   "stderr_sha256": hashlib.sha256(b"").hexdigest(), "stdout_bytes": 3, "stderr_bytes": 0,
                   "truncated": False}
        verifier.verify_receipt_streams(process)
        process["stdout"] = "43\n"
        with self.assertRaisesRegex(ValueError, "stdout receipt digest"):
            verifier.verify_receipt_streams(process)


if __name__ == "__main__":
    unittest.main()
