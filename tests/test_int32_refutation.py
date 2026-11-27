"""Security and semantic boundaries of signed one-point refutations."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]
import int32_circuit as signed
import int32_refutation as compact
import proof_dag_checker as core


def source(expression, before=""):
    return ('#include <stdio.h>\nint main(void) { int x, y; '
            'scanf("%d %d", &x, &y); ' + before +
            'printf("%d", ' + expression + '); return 0; }')


def task(candidate="x / y", reference="x", points=None):
    return {"kind": signed.PROFILE, "id": "compact-controls", "policy": "reference-everywhere",
            "sources": {"original": source("x"), "candidate": source(candidate),
                        "reference": source(reference)},
            "points": points if points is not None else [[-3, 0], [1, 1], [5, 0]]}


def resign(certificate):
    result = copy.deepcopy(certificate)
    body = {key: value for key, value in result.items() if key != "certificate_sha256"}
    result["certificate_sha256"] = hashlib.sha256(signed._canonical(body)).hexdigest()
    return result


class SignedCompactRefutations(unittest.TestCase):
    def test_confirms_definedness_with_exactly_one_semantic_point(self):
        request = task()
        certificate = compact.produce(request)
        self.assertEqual(certificate["obligation"], "defined")
        original = signed._vectors
        calls = []
        def singleton(circuit, names, points):
            calls.append(copy.deepcopy(points))
            return original(circuit, names, points)
        with patch.object(signed, "_vectors", side_effect=singleton):
            checked = compact.check(request, certificate)
        self.assertEqual(calls, [[certificate["input"]]])
        self.assertEqual(checked["checked_points"], 1)
        self.assertEqual(checked["checked_cells"], checked["checked_nodes"])
        self.assertEqual(checked["witness"], signed.evaluate_direct(request)["witness"])

    def test_nonleast_real_violation_is_valid_without_claiming_leastness(self):
        request = task()
        witness = {"obligation": "defined", "input": [5, 0], "trace": []}
        certificate = compact.produce(request, witness)
        self.assertEqual(compact.check(request, certificate)["witness"], witness)
        self.assertNotEqual(witness, signed.evaluate_direct(request)["witness"])

    def test_stale_id_sources_policy_and_domain_are_rejected(self):
        request = task()
        certificate = compact.produce(request)
        variants = []
        r = copy.deepcopy(request); r["id"] += "-changed"; variants.append(r)
        r = copy.deepcopy(request); r["points"].append([6, 0]); variants.append(r)
        r = copy.deepcopy(request); r["policy"] = "preserve-everywhere"; variants.append(r)
        for role in core.ROLES:
            r = copy.deepcopy(request); r["sources"][role] += "/* changed bytes */"; variants.append(r)
        for changed in variants:
            with self.subTest(changed=changed):
                with self.assertRaises(core.Invalid):
                    compact.check(changed, certificate)

    def test_correlated_domain_does_not_admit_an_axis_cross_product(self):
        request = task(candidate="1", reference="0", points=[[1, 2], [3, 4]])
        certificate = compact.produce(request)
        certificate["input"] = [1, 4]
        with self.assertRaisesRegex(core.Invalid, "outside exact domain"):
            compact.check(request, resign(certificate))

    def test_forged_trace_and_nonviolating_point_or_obligation_are_rejected(self):
        request = task(candidate="x + 1", reference="x", points=[[-1, 1], [1, 1]])
        request["sources"]["candidate"] = source("x + 1", "if (x < 0) { y = 2; }")
        certificate = compact.produce(request)
        bad = copy.deepcopy(certificate); bad["trace"][0][1] ^= 1
        with self.assertRaisesRegex(core.Invalid, "trace mismatch"):
            compact.check(request, resign(bad))
        for obligation in ("defined", "preserve"):
            bad = copy.deepcopy(certificate); bad["obligation"] = obligation
            with self.assertRaisesRegex(core.Invalid, "obligation is true"):
                compact.check(request, resign(bad))
        request = task()
        bad = compact.produce(request); bad["input"] = [1, 1]
        with self.assertRaisesRegex(core.Invalid, "obligation is true"):
            compact.check(request, resign(bad))

    def test_acceptance_cannot_be_packaged_as_a_refutation(self):
        with self.assertRaisesRegex(core.Invalid, "no refutation"):
            compact.produce(task(candidate="x", reference="x"))

    def test_rehashed_wrong_types_and_extra_fields_remain_invalid(self):
        request = task(candidate="1", reference="0", points=[[0, 0], [1, 1]])
        base = compact.produce(request)
        variants = []
        for value in ([False, 0], [0.0, 0], [signed.INT_MIN - 1, 0], [0]):
            bad = copy.deepcopy(base); bad["input"] = value; variants.append(bad)
        for value in ([[False, 0]], [[0, True]], [[-1, 0]], [[0, 2]], ""):
            bad = copy.deepcopy(base); bad["trace"] = value; variants.append(bad)
        bad = copy.deepcopy(base); bad["extra"] = 1; variants.append(bad)
        bad = copy.deepcopy(base); bad["obligation"] = 0; variants.append(bad)
        for bad in variants:
            with self.subTest(certificate=bad):
                with self.assertRaises(core.Invalid):
                    compact.check(request, resign(bad))
        bad = copy.deepcopy(base); bad["certificate_sha256"] = "0" * 64
        with self.assertRaises(core.Invalid):
            compact.check(request, bad)

    def test_reference_fault_remains_a_repair_failure(self):
        request = task(candidate="1", reference="x / y", points=[[1, 0]])
        certificate = compact.produce(request)
        self.assertEqual(certificate["obligation"], "repair")
        self.assertEqual(compact.check(request, certificate)["status"], "REFUTED")


if __name__ == "__main__":
    unittest.main()
