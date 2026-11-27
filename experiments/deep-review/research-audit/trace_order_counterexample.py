"""Executable counterexamples to two prose claims about trace-first ordering.

The receiver's specified ordering is preserved. This experiment disproves the
claims that lexicographic trace order necessarily selects a shallowest path or
refines numeric input order. Authored two-point examples are mechanism controls,
not additional real-world defects or a new corpus population.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from checker import Session
from demand_evaluator import evaluate_demand
from proof_dag_checker import check, evaluate_topological
from proof_dag_producer import produce


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def request(variant):
    plain = "unsigned f(unsigned x) { return 0u; }"
    branches = {
        "deep-first": (
            "if (x == 0u) { scratch = 1u; } else { "
            "if (x == 1u) { if (x == 1u) { scratch = 2u; } "
            "else { scratch = 3u; } } else { scratch = 4u; } }"
        ),
        "shallow-first": (
            "if (x != 0u) { "
            "if (x == 1u) { if (x == 1u) { scratch = 2u; } "
            "else { scratch = 3u; } } else { scratch = 4u; } "
            "} else { scratch = 1u; }"
        ),
    }
    return {
        "id": "diagnostic-order-" + variant,
        "word_bits": 32,
        "inputs": {"x": [0, 1]},
        "original": plain,
        "candidate": "unsigned f(unsigned x) { unsigned scratch = 0u; "
                     + branches[variant] + " return 1u; }",
        "reference": plain,
        "repair_guard": "x == x",
    }


def decision(result):
    return {key: result[key] for key in ("status", "witness")}


def run(output):
    if output.exists():
        raise ValueError("output must be a new directory")
    output.mkdir(parents=True)
    records = []
    for variant in ("deep-first", "shallow-first"):
        task = request(variant)
        # This interpreter has its own source parser and executes statements.
        # It does not obtain its traces from a full/demand circuit result.
        independent = Session(task)
        observations = []
        for value in (0, 1):
            defined, actual, trace = independent.run("candidate", {"x": value})
            reference_defined, expected, _ = independent.run("reference", {"x": value})
            if not defined or not reference_defined or actual == expected:
                raise AssertionError("control must have two defined mismatches")
            observations.append({"input": [value], "defined": defined,
                                 "candidate": actual, "reference": expected,
                                 "trace": [list(event) for event in trace],
                                 "executed_if_count": len(trace)})
        least = min(observations, key=lambda row: (row["trace"], row["input"]))
        expected_result = {"status": "REFUTED", "witness": {
            "obligation": "repair", "trace": least["trace"], "input": least["input"]}}
        packet = produce(task)
        results = {
            "full": check(task, packet),
            "direct": evaluate_topological(task),
            "demand": evaluate_demand(task),
        }
        for name, result in results.items():
            if decision(result) != expected_result:
                raise AssertionError(name + " disagrees with concrete oracle")
        if variant == "deep-first":
            if least["input"] != [1] or least["executed_if_count"] != 3:
                raise AssertionError("expected deeper, numerically later witness")
        elif least["input"] != [0] or least["executed_if_count"] != 1:
            raise AssertionError("expected refactored witness")
        (output / (variant + "-request.json")).write_bytes(canonical(task) + b"\n")
        (output / (variant + "-packet.json")).write_bytes(canonical(packet) + b"\n")
        records.append({"variant": variant, "observations": observations,
                        "receivers": results, "oracle": expected_result,
                        "request_sha256": hashlib.sha256(canonical(task)).hexdigest()})
    if [r["candidate"] for r in records[0]["observations"]] != [r["candidate"] for r in records[1]["observations"]]:
        raise AssertionError("refactoring changed candidate output")
    summary = {
        "status": "PASS",
        "study_kind": "authored diagnostic-order counterexample; fresh local execution",
        "requests": 2,
        "source_input_observations": 4,
        "complete_receiver_results": 6,
        "complete_receiver_disagreements": 0,
        "findings": {
            "lexicographic_trace_order_need_not_select_shortest_trace": True,
            "lexicographic_trace_order_need_not_select_shallowest_executed_path": True,
            "trace_first_order_can_reverse_numeric_input_order": True,
            "output_preserving_branch_refactoring_can_change_canonical_witness": True,
            "scratch_only_branches_do_not_establish_failure_causality": True,
        },
        "scope": "Two admitted unsigned requests over x in {0,1}; no native compiler or external verifier was executed by this experiment.",
        "records": records,
        "environment": {"python": sys.version, "platform": platform.platform()},
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), ROOT / "src/checker.py",
                                    ROOT / "src/proof_dag_checker.py", ROOT / "src/producer.py",
                                    ROOT / "src/proof_dag_producer.py", ROOT / "src/demand_evaluator.py"]},
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({key: result[key] for key in ("status", "requests", "complete_receiver_results", "findings")}))


if __name__ == "__main__":
    main()
