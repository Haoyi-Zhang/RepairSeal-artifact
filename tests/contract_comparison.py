"""Compare matched finite decisions and receiver-owned domain transport.

The 380 retained core and 400 grammar requests are fixed before this study.
Dependency pruning preserves the exact canonical status/witness contract.
Guarded-reference equivalence compares Boolean truth at each input, not the
cost of producing a different diagnostic.  Domain transport uses the 95
accepted core requests and gives full and direct receivers identical history.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
from proof_dag_producer import produce
from domain_transport import (AcceptanceTransport, evaluate_pruned,
                              obligation_supports, request_identity)
from scientific_driver import new_output_directory, require_assertions


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def decision(result):
    return {key: result[key] for key in ("status", "witness")}


def require_same(left, right, label):
    if not core.exact_equal(left, right):
        raise AssertionError((label, left, right))


def equivalence(request, certificate):
    circuit, programs, guard, roots = core.build_expected(request)
    vectors = [record["vector"] for record in certificate["nodes"]]
    p, q, t = (programs[role] for role in core.ROLES)
    count = len(vectors[roots[0]])
    for i in range(count):
        selected = t if vectors[guard][i] else p
        guarded = bool(vectors[q.defined][i] and vectors[selected.defined][i]
                       and vectors[q.output][i] == vectors[selected.output][i])
        separate = all(vectors[root][i] for root in roots)
        require_same(guarded, separate, (request["id"], i, "guarded-reference"))
    return count, all(vectors[q.defined]) and all(vectors[roots[2]])


def first_uncovered(values, maximum=1):
    # Deterministic low values, then unsigned maximum; no verdict influences
    # input selection.  Each admitted axis contains at most 64 values.
    old = set(values)
    candidates = [value for value in range(128) if value not in old]
    if core.MASK not in old:
        candidates.append(core.MASK)
    return candidates[:maximum]


def target_domains(request, supports):
    names = list(request["inputs"])
    relevant = set().union(*(set(s) for s in supports))
    targets = []
    subset = copy.deepcopy(request)
    subset["inputs"] = {name: [values[0]] for name, values in request["inputs"].items()}
    targets.append(("axis-subset", subset, True))
    irrelevant = [name for name in names if name not in relevant]
    if irrelevant:
        name = irrelevant[0]
        changed = copy.deepcopy(request)
        other_points = math.prod(len(values) for other, values in request["inputs"].items()
                                 if other != name)
        size = min(64, 4096 // other_points)
        changed["inputs"][name] = first_uncovered(request["inputs"][name], size)
        targets.append(("irrelevant-axis-replacement", changed, True))
    if relevant:
        name = next(name for name in names if name in relevant)
        changed = copy.deepcopy(request)
        # Replacement keeps the original packet's product bound while placing
        # one uncovered value on a relevant axis.
        values = changed["inputs"][name]
        values[-1] = first_uncovered(values)[0]
        changed["inputs"][name] = sorted(values)
        targets.append(("uncovered-relevant-value", changed, False))
    for kind, changed, expected_transport in targets:
        changed["id"] = request["id"] + "-" + {
            "axis-subset": "subset", "irrelevant-axis-replacement": "irrelevant",
            "uncovered-relevant-value": "uncovered"}[kind]
        yield kind, changed, expected_transport


def run(output: Path):
    require_assertions()
    output = new_output_directory(output)
    retained = ROOT / "proof-data"
    protocol = {
        "schema": "contract-comparison-protocol-v1",
        "core_requests": 380, "grammar_requests": 400,
        "same_result": "status plus obligation/trace/input ordered witness",
        "direct_baseline": "dependency-pruned DAG, all live nodes at all domain points",
        "guarded_reference": "pointwise Boolean equivalence only; no diagnostic-cost comparison",
        "transport_population": "all accepted requests in the fixed 380-request core corpus",
        "transport_history": "one current accepted check per arm, identical source and domain",
        "targets": ["one minimum value per axis", "replace first irrelevant axis with up to 64 uncovered low values within the 4096-point bound", "replace largest value on first relevant axis with first uncovered low value"],
        "packet_rule": "each original full packet must be rejected for the new request",
        "runtime_claim": "semantic cells counted; no elapsed-time speedup claim",
        "source_bindings": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [*sorted((ROOT / "src").glob("*.py")),
                                      Path(__file__), ROOT / "tests/scientific_driver.py"]},
    }
    save(output / "protocol.json", protocol)
    cases = []
    accepted = []
    corpus_bindings = {}
    for group, directory, rows_path, certificate_directory in (
            ("core-fixture", "fixture-inputs", "fixture-cases.json", "fixture-certificates"),
            ("core-stress", "stress-inputs", "stress-cases.json", "stress-certificates"),
            ("grammar", "holdout-differential/inputs", "holdout-differential/cases.json", None)):
        expected = {row["id"]: row for row in json.loads((retained / rows_path).read_text())}
        corpus_bindings[rows_path] = hashlib.sha256((retained / rows_path).read_bytes()).hexdigest()
        for path in sorted((retained / directory).glob("*.json")):
            request = core.load_json_strict(path.read_text())
            corpus_bindings[path.relative_to(retained).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            if certificate_directory:
                certificate_path = retained / certificate_directory / path.name
                certificate = core.load_json_strict(certificate_path.read_text())
                corpus_bindings[certificate_path.relative_to(retained).as_posix()] = hashlib.sha256(certificate_path.read_bytes()).hexdigest()
            else:
                certificate = produce(request)
            full = core.check(request, certificate)
            pruned = evaluate_pruned(request)
            require_same(decision(full), decision(expected[request["id"]]), request["id"])
            require_same(decision(pruned), decision(full), request["id"])
            if pruned["checked_cells"] > full["checked_cells"]:
                raise AssertionError("dependency closure grew the circuit")
            points, preserve_only = equivalence(request, certificate)
            cases.append({"id": request["id"], "corpus": group,
                          "request_identity": request_identity(request), **decision(full),
                          "points": points, "full_nodes": full["checked_nodes"],
                          "live_nodes": pruned["checked_nodes"],
                          "full_cells": full["checked_cells"],
                          "pruned_cells": pruned["checked_cells"],
                          "defined_preservation_only_accepts": preserve_only,
                          "guarded_reference_point_agreements": points})
            if group != "grammar" and full["status"] == "ACCEPT":
                accepted.append((request, certificate))
    save(output / "corpus-bindings.json", corpus_bindings)
    save(output / "decisions.json", cases)
    transport_rows = []
    for request, certificate in accepted:
        circuit, _, _, roots = core.build_expected(request)
        supports = obligation_supports(circuit, roots)
        owners = {mode: AcceptanceTransport() for mode in ("full", "direct")}
        for mode, owner in owners.items():
            result = owner.establish(request, certificate if mode == "full" else None, mode=mode)
            if result["status"] != "ACCEPT":
                raise AssertionError("accepted basis changed")
        for kind, target, expected_transport in target_domains(request, supports):
            cold = evaluate_pruned(target)
            fresh = core.check(target, produce(target))
            require_same(decision(cold), decision(fresh), target["id"])
            receipts = {mode: owner.revalidate(target) for mode, owner in owners.items()}
            for mode, receipt in receipts.items():
                require_same(decision(receipt), decision(cold), (target["id"], mode))
                require_same(receipt["transported"], expected_transport, (target["id"], "coverage"))
                if receipt["checked_cells"] != (0 if expected_transport else cold["checked_cells"]):
                    raise AssertionError("incorrect semantic cell count")
            require_same(receipts["full"], receipts["direct"], target["id"])
            try:
                core.check(target, certificate)
            except core.Invalid:
                pass
            else:
                raise AssertionError("stale packet accepted")
            save(output / "requests" / (target["id"] + ".json"), target)
            transport_rows.append({"id": target["id"], "basis": request["id"],
                                   "kind": kind, "supports": [list(s) for s in supports],
                                   "old_points": math.prod(map(len, request["inputs"].values())),
                                   "new_points": math.prod(map(len, target["inputs"].values())),
                                   "cold_pruned_cells": cold["checked_cells"],
                                   "fresh_full_cells": fresh["checked_cells"],
                                   "receipt": receipts["full"], "old_packet_rejected": True})
    save(output / "transport.json", transport_rows)
    groups = {}
    for label in ("core", "grammar"):
        selected = [row for row in cases if row["corpus"].startswith(label)]
        groups[label] = {
            "requests": len(selected), "accepted": sum(r["status"] == "ACCEPT" for r in selected),
            "point_agreements": sum(r["points"] for r in selected),
            "full_cells": sum(r["full_cells"] for r in selected),
            "pruned_cells": sum(r["pruned_cells"] for r in selected),
            "requests_with_fewer_cells": sum(r["pruned_cells"] < r["full_cells"] for r in selected),
            "repair_failures_accepted_by_preservation_ablation": sum(r["defined_preservation_only_accepts"] and r["status"] == "REFUTED" for r in selected),
        }
    transferred = [row for row in transport_rows if row["receipt"]["transported"]]
    fallback = [row for row in transport_rows if not row["receipt"]["transported"]]
    summary = {
        "schema": "contract-comparison-v1", "outcome": "PASS", "corpora": groups,
        "same_canonical_results": len(cases),
        "guarded_reference_point_agreements": sum(row["points"] for row in cases),
        "transport": {
            "accepted_bases": len(accepted), "new_requests": len(transport_rows),
            "same_full_direct_history_results": len(transport_rows),
            "covered_requests": len(transferred),
            "covered_target_points": sum(row["new_points"] for row in transferred),
            "covered_new_semantic_cells_per_arm": sum(row["receipt"]["checked_cells"] for row in transferred),
            "covered_cold_pruned_cells": sum(row["cold_pruned_cells"] for row in transferred),
            "covered_fresh_full_cells": sum(row["fresh_full_cells"] for row in transferred),
            "covered_kinds": dict(Counter(row["kind"] for row in transferred)),
            "fallback_requests": len(fallback),
            "fallback_statuses": dict(Counter(row["receipt"]["status"] for row in fallback)),
            "old_packets_rejected": len(transport_rows),
            "scope": "sequential receiver-owned acceptance history; newly identified results, not stale-packet acceptance or refutation transport",
        },
        "records": {name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                    for name in ("protocol.json", "corpus-bindings.json", "decisions.json", "transport.json")},
    }
    require_same(groups["core"]["requests"], 380, "core population")
    require_same(groups["grammar"]["requests"], 400, "grammar population")
    require_same(len(accepted), 95, "accepted core population")
    save(output / "summary.json", summary)
    return summary


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))


if __name__ == "__main__":
    main()
