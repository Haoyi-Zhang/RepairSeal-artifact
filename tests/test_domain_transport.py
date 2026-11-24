"""Adversarial checks for global support and receiver-owned acceptance history."""
from pathlib import Path
import copy
import hashlib
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import proof_dag_checker as core
from proof_dag_producer import produce
from domain_transport import (AcceptanceTransport, evaluate_pruned,
                              obligation_supports, request_identity)


def make_request(*, axes=None, bug=False, undefined=False):
    axes = {"x": [0, 1, 2], "z": [0]} if axes is None else axes
    signature = ", ".join("unsigned " + name for name in axes)
    def source(body):
        return "unsigned f(" + signature + ") { " + body + " }"
    body = ("unsigned out = x; unsigned scratch = 0u; "
            "if (z == 0u) { scratch = 1u; } else { scratch = 0u; } "
            "if (x != 0u) { out = x + 1u; } else { out = x; } ")
    if bug:
        body += "if (x == 63u) { out = 7u; } else { out = out; } "
    if undefined:
        body += "scratch = 1u / z; "
    body += "return out;"
    return {"id": "support-base", "word_bits": 32,
            "inputs": copy.deepcopy(axes), "original": source("return x;"),
            "candidate": source(body), "reference": source("return x + 1u;"),
            "repair_guard": "x != 0u"}


def decision(result):
    return result["status"], result["witness"]


class DomainTransportTests(unittest.TestCase):
    def test_pruned_keeps_trace_and_exact_diagnostic(self):
        for request in (make_request(), make_request(bug=True,
                        axes={"x": [0, 1, 63], "z": [0, 1]}),
                        make_request(undefined=True)):
            with self.subTest(request=request["candidate"]):
                full = core.check(request, produce(request))
                direct = evaluate_pruned(request)
                self.assertEqual(decision(full), decision(direct))
                self.assertLessEqual(direct["checked_nodes"], full["checked_nodes"])
                self.assertEqual(direct["checked_cells"], direct["checked_nodes"] *
                                 len(core.validate_request(request)[2]))

    def test_irrelevant_axis_changes_with_identical_full_and_direct_history(self):
        original = make_request()
        expanded = make_request(axes={"x": [0, 1, 2], "z": list(range(1, 65))})
        expanded["id"] = "support-expanded"
        cold = evaluate_pruned(expanded)
        self.assertEqual(cold["status"], "ACCEPT")
        self.assertGreater(cold["checked_cells"], 0)
        for mode in ("full", "direct"):
            owner = AcceptanceTransport()
            base = owner.establish(original, produce(original) if mode == "full"
                                   else None, mode=mode)
            calls = []
            result = owner.revalidate(expanded, count=lambda kind, n: calls.append(kind))
            self.assertTrue(result["transported"])
            self.assertEqual(decision(result), decision(cold))
            self.assertEqual(result["checked_cells"], 0)
            self.assertEqual(result["relevant_inputs"], ["x"])
            self.assertEqual(set(calls), {"transport_axis_values"})
            self.assertNotEqual(result["request_identity"], base["request_identity"])
            self.assertEqual(result["basis_request_identity"], base["request_identity"])

    def test_new_relevant_value_is_checked_and_finds_real_failure(self):
        owner = AcceptanceTransport()
        original = make_request(bug=True)
        self.assertEqual(owner.establish(original)["status"], "ACCEPT")
        previous = owner.basis_request_identity
        expanded = make_request(bug=True, axes={"x": [0, 1, 2, 63], "z": [1]})
        result = owner.revalidate(expanded)
        self.assertFalse(result["transported"])
        self.assertEqual(result["fallback_reason"], "uncovered-relevant-value")
        self.assertEqual(result["status"], "REFUTED")
        self.assertEqual(result["witness"]["input"], [63, 1])
        self.assertEqual(previous, owner.basis_request_identity)

    def test_unused_value_still_contributes_definedness(self):
        owner = AcceptanceTransport()
        original = make_request(undefined=True, axes={"x": [0, 1], "z": [1]})
        self.assertEqual(owner.establish(original)["status"], "ACCEPT")
        changed = make_request(undefined=True, axes={"x": [0, 1], "z": [0]})
        result = owner.revalidate(changed)
        self.assertFalse(result["transported"])
        self.assertEqual(result["witness"]["obligation"], "defined")

    def test_global_support_not_observed_constant_on_old_domain(self):
        signature = "unsigned f(unsigned x, unsigned y)"
        original = {"id": "global-support", "word_bits": 32,
                    "inputs": {"x": [0], "y": [0]},
                    "original": signature + " { return 0u; }",
                    "candidate": signature + " { return 0u; }",
                    "reference": signature + " { return 1u; }",
                    "repair_guard": "(x != 0u) && (y != 0u)"}
        circuit, _, _, roots = core.build_expected(original)
        self.assertIn(("x", "y"), obligation_supports(circuit, roots))
        owner = AcceptanceTransport()
        self.assertEqual(owner.establish(original)["status"], "ACCEPT")
        changed = copy.deepcopy(original)
        changed["inputs"] = {"x": [1], "y": [1]}
        result = owner.revalidate(changed)
        self.assertFalse(result["transported"])
        self.assertEqual(result["witness"]["obligation"], "repair")

    def test_refutation_is_not_an_acceptance_basis_or_a_reused_trace(self):
        owner = AcceptanceTransport()
        original = make_request(bug=True, axes={"x": [63], "z": [0]})
        first = owner.establish(original)
        self.assertEqual(first["status"], "REFUTED")
        self.assertIsNone(owner.basis_request_identity)
        changed = make_request(bug=True, axes={"x": [63], "z": [1]})
        second = owner.revalidate(changed)
        self.assertEqual(second["status"], "REFUTED")
        self.assertFalse(second["transported"])
        self.assertNotEqual(first["witness"]["trace"], second["witness"]["trace"])
        self.assertEqual(decision(second), decision(core.evaluate_topological(changed)))

    def test_source_and_policy_changes_require_new_check(self):
        original = make_request()
        for field, replacement in (
                ("candidate", original["candidate"] + " /* changed bytes */"),
                ("reference", original["reference"].replace("x + 1u", "x + 2u")),
                ("repair_guard", "x == 0u")):
            owner = AcceptanceTransport()
            owner.establish(original)
            changed = copy.deepcopy(original)
            changed[field] = replacement
            result = owner.revalidate(changed)
            self.assertFalse(result["transported"])
            self.assertEqual(result["fallback_reason"], "context-changed")
            self.assertEqual(decision(result), decision(core.evaluate_topological(changed)))

    def test_input_order_is_bound_even_when_dictionary_encoding_is_sorted(self):
        original = make_request(axes={"x": [0, 1], "z": [0, 1]})
        reordered = copy.deepcopy(original)
        reordered["inputs"] = {"z": [0, 1], "x": [0, 1]}
        self.assertNotEqual(request_identity(original), request_identity(reordered))
        for role in core.ROLES:
            reordered[role] = reordered[role].replace(
                "unsigned x, unsigned z", "unsigned z, unsigned x")
        owner = AcceptanceTransport()
        owner.establish(original)
        result = owner.revalidate(reordered)
        self.assertFalse(result["transported"])
        self.assertEqual(decision(result), decision(evaluate_pruned(reordered)))

    def test_packet_staleness_is_not_waived_by_acceptance_history(self):
        original = make_request()
        owner = AcceptanceTransport()
        cert = produce(original)
        owner.establish(original, cert, mode="full")
        previous = owner.basis_request_identity
        changed = make_request(axes={"x": [0, 1, 2], "z": [1]})
        with self.assertRaises(core.Invalid):
            owner.establish(changed, cert, mode="full")
        self.assertEqual(owner.basis_request_identity, previous)
        self.assertTrue(owner.revalidate(changed)["transported"])
        corrupt = copy.deepcopy(cert)
        corrupt["nodes"][0]["vector"][0] = not corrupt["nodes"][0]["vector"][0]
        corrupt.pop("certificate_sha256")
        corrupt["certificate_sha256"] = hashlib.sha256(core.canonical_bytes(corrupt)).hexdigest()
        with self.assertRaises(core.Invalid):
            owner.establish(original, corrupt, mode="full")
        self.assertEqual(owner.basis_request_identity, previous)

    def test_request_mutation_and_failed_calls_leave_owned_basis_unchanged(self):
        original = make_request()
        owner = AcceptanceTransport()
        owner.establish(original)
        previous = owner.basis_request_identity
        original["inputs"]["x"].append(63)
        original["candidate"] = "not a program"
        covered = make_request(axes={"x": [0, 1], "z": [1]})
        self.assertTrue(owner.revalidate(covered)["transported"])
        malformed = copy.deepcopy(covered)
        malformed["inputs"]["x"] = [True]
        with self.assertRaises(core.Invalid):
            owner.revalidate(malformed)
        def exhausted(_kind, _n):
            raise RuntimeError("owned test budget")
        with self.assertRaisesRegex(RuntimeError, "owned test budget"):
            owner.revalidate(covered, count=exhausted)
        with self.assertRaisesRegex(RuntimeError, "owned test budget"):
            owner.establish(covered, count=exhausted)
        self.assertEqual(owner.basis_request_identity, previous)

    def test_no_packet_can_be_silently_ignored_in_direct_mode(self):
        owner = AcceptanceTransport()
        original = make_request()
        with self.assertRaises(core.Invalid):
            owner.establish(original, produce(original), mode="direct")
        with self.assertRaises(core.Invalid):
            owner.establish(original, mode="untrusted-basis")
        self.assertIsNone(owner.basis_request_identity)


if __name__ == "__main__":
    unittest.main()
