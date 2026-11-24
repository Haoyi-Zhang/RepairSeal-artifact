#!/usr/bin/env python3
"""Audit natural point-set coverage independently of retained union outcomes.

All retained candidate/subject combinations are selected from corpus eligibility
and source-interface compatibility.  Repair acceptance and syntactic support
coverage are calculated first and written to a separate record.  Only then are
retained union outcomes accessed and checked by a fresh Boolean evaluation.
No source inputs, domains, receiver implementations, or retained studies change.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write("\n")


def supports_from_graph(circuit, roots, names):
    """Independent structural free-variable calculation, checked by root DFS."""
    positions = {name: i for i, name in enumerate(names)}
    all_supports = []
    for number, node in enumerate(circuit.nodes):
        if node[0] == "input":
            found = {positions[node[1]]}
        elif node[0] in {"b", "u"}:
            found = set()
        else:
            assert all(type(child) is int and 0 <= child < number for child in node[1:])
            found = set().union(*(all_supports[child] for child in node[1:]))
        all_supports.append(found)
    answer = []
    for root in roots:
        pending, visited, found = [root], set(), set()
        while pending:
            number = pending.pop()
            if number in visited:
                continue
            visited.add(number)
            node = circuit.nodes[number]
            if node[0] == "input":
                found.add(positions[node[1]])
            elif node[0] not in {"b", "u"}:
                pending.extend(node[1:])
        assert found == all_supports[root]
        answer.append(tuple(sorted(found)))
    return answer


def projected(points, support):
    return {tuple(point[index] for index in support) for point in points}


def boolean_status(symbolic, circuit, names, roots, points):
    vectors = symbolic._vectors(circuit, names, points)
    return "ACCEPT" if all(all(vectors[root]) for root in roots) else "REFUTED"


def summarize(rows):
    accepted = [row for row in rows if row["repair_status"] == "ACCEPT"]
    covered = [row for row in accepted if row["support_covered"]]
    expanded = [row for row in accepted if row["new_full_inputs"]]
    useful = [row for row in covered if row["new_full_inputs"] and row["root_class"] == "nonempty_syntactic_support"]
    counts = {
        "combinations": len(rows),
        "subjects": len({row["subject"] for row in rows}),
        "problems": len({row["problem"] for row in rows}),
        "repair_status": dict(Counter(row["repair_status"] for row in rows)),
        "accepted_repair": len(accepted),
        "accepted_with_new_full_inputs": len(expanded),
        "accepted_unchanged_point_sets": len(accepted) - len(expanded),
        "accepted_by_root_class": dict(Counter(row["root_class"] for row in accepted)),
        "accepted_with_full_input_support": sum(any(len(root["support_positions"]) == len(row["input_order"])
                                                   for root in row["obligations"]) for row in accepted),
        "covered_accepted": len(covered),
        "uncovered_accepted": len(accepted) - len(covered),
        "covered_with_new_full_inputs": sum(bool(row["new_full_inputs"]) for row in covered),
        "covered_unchanged_point_sets": sum(not row["new_full_inputs"] for row in covered),
        "covered_by_root_class": dict(Counter(row["root_class"] for row in covered)),
        "covered_new_inputs_by_root_class": dict(Counter(row["root_class"] for row in covered if row["new_full_inputs"])),
        "nonempty_support_covered_new_inputs": len(useful),
        "nonempty_support_covered_new_subjects": len({row["subject"] for row in useful}),
        "nonempty_support_covered_new_problems": len({row["problem"] for row in useful}),
    }
    if rows and "union_status" in rows[0]:
        counts.update({
            "union_status": dict(Counter(row["union_status"] for row in rows)),
            "covered_union_status": dict(Counter(row["union_status"] for row in covered)),
            "uncovered_accepted_union_status": dict(Counter(row["union_status"] for row in accepted if not row["support_covered"])),
            "nonempty_support_covered_new_union_status": dict(Counter(row["union_status"] for row in useful)),
        })
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Assertions must remain enabled.")
    args.output.mkdir(parents=True, exist_ok=False)
    artifact = ROOT
    sys.path[:0] = [str(artifact / "src"), str(artifact / "tests")]
    import int32_circuit as symbolic
    import int32_contract_study as retained

    prior_summary = json.loads((args.reference / "summary.json").read_text())
    assert prior_summary["outcome"] == "PASS"
    for name, expected in prior_summary["source_bindings"].items():
        assert digest(artifact / name) == expected, name
    for name, expected in prior_summary["records"].items():
        assert digest(args.reference / name) == expected, name
    source_bindings = dict(prior_summary["source_bindings"])
    source_bindings["tests/signed_coverage_study.py"] = digest(Path(__file__))
    protocol = {
        "question": "Does the original held-out test set add any projection on an accepted repair request's global syntactic obligation supports?",
        "population": "All eligible source-compatible candidate/subject combinations in the retained signed corpus.",
        "planned_combinations": 739,
        "selection": "Corpus eligibility and interface compatibility only; no union-outcome or coverage selection.",
        "coverage": "For each obligation root, project actual repair and union tuples on its structural free inputs; require every union projection in the repair projection set.",
        "root_classes": {
            "all_literal_true": "All three reconstructed obligation roots are literal Boolean true; history adds no semantic fact needed to evaluate them.",
            "empty_support_not_all_literal_true": "All three root supports are empty, but at least one root is not literal true.",
            "nonempty_syntactic_support": "At least one obligation has a nonempty structural input support; this alone does not prove semantic dependence.",
        },
        "outcome_order": "Freeze coverage-before-union.json after all combinations; only then access union status fields and evaluate the actual union inputs.",
        "not_measured": ["elapsed receiving time", "cache implementation or durable state reuse"],
        "source_bindings": source_bindings,
        "reference_records": prior_summary["records"],
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "pycparser": version("pycparser")},
        "inputs": {"corpus": digest(args.corpus), "reference_summary": digest(args.reference / "summary.json"),
                   "reference_requests": digest(args.reference / "requests.json"), "archive": prior_summary["archive_sha256"],
                   "script": digest(Path(__file__))},
    }
    write_new(args.output / "protocol.json", protocol)
    corpus, raw, _admitted, corpus_identity = retained.load_inputs(args.corpus, args.archive)
    assert corpus_identity == prior_summary["corpus_sha256"]
    eligible, cases, _needed = retained.populations(corpus)
    assert len(eligible) == 95 and len(cases) == 739
    records = json.loads((args.reference / "requests.json").read_text())
    repair_records = {row["id"]: row for row in records if row["stage"] == "repair"}
    assert len(repair_records) == len(cases)
    rows, held = [], []
    for index, (subject, candidate) in enumerate(cases):
        sources = {"original": subject["original_sha"], "candidate": candidate, "reference": subject["reference_sha"]}
        role = ("own_reference" if candidate == sources["reference"] else
                "own_original" if candidate == sources["original"] else "cross_source")
        repair_points = sorted({tuple(test["input"]) for test in subject["tests"] if test["split"] == "repair"})
        union_points = sorted({tuple(test["input"]) for test in subject["tests"]})
        assert repair_points and set(repair_points) <= set(union_points)
        new_points = sorted(set(union_points) - set(repair_points))
        task = {"kind": symbolic.PROFILE, "id": f"{subject['id']}-{candidate[:12]}-repair",
                "policy": "reference-everywhere", "points": [list(p) for p in repair_points],
                "sources": {key: raw[value].decode("utf-8") for key, value in sources.items()}}
        old = repair_records[task["id"]]
        assert symbolic.task_identity(task) == old["task_sha256"]
        circuit, _compiled, roots, names, _kind, _labels = symbolic.build_task(task)
        supports = supports_from_graph(circuit, roots, names)
        repair_status = boolean_status(symbolic, circuit, names, roots, repair_points)
        assert repair_status == old["status"]
        all_literal_true = all(circuit.nodes[root][0] == "b" and circuit.nodes[root][1] is True for root in roots)
        root_class = ("all_literal_true" if all_literal_true else
                      "nonempty_syntactic_support" if any(supports) else "empty_support_not_all_literal_true")
        obligation_rows = []
        for number, (root, support) in enumerate(zip(roots, supports)):
            old_projection = projected(repair_points, support)
            new_projection = projected(union_points, support)
            missing = sorted(new_projection - old_projection)
            obligation_rows.append({"obligation": ["defined", "repair", "preserve"][number],
                "root": root, "root_node": list(circuit.nodes[root]), "support_positions": list(support),
                "support_names": [names[i] for i in support], "repair_projection_count": len(old_projection),
                "union_projection_count": len(new_projection), "uncovered_keys": [list(key) for key in missing]})
        row = {"index": index, "subject": subject["id"], "problem": subject["problem"], "role": role,
               "sources": sources, "repair_request_id": task["id"], "repair_status": repair_status,
               "input_order": list(names), "nodes": len(circuit.nodes),
               "dag_nodes": [list(node) for node in circuit.nodes], "obligation_roots": list(roots),
               "repair_points": [list(p) for p in repair_points], "union_points": [list(p) for p in union_points],
               "new_full_inputs": [list(p) for p in new_points], "root_class": root_class,
               "all_obligation_roots_literal_true": all_literal_true,
               "obligations": obligation_rows,
               "support_covered": all(not root_row["uncovered_keys"] for root_row in obligation_rows)}
        rows.append(row)
        held.append((circuit, names, roots, task, union_points))
        if (index + 1) % 100 == 0:
            print(json.dumps({"phase": "coverage_before_union", "completed": index + 1}), flush=True)
    assert Counter(row["role"] for row in rows) == {"own_reference": 95, "own_original": 95, "cross_source": 549}
    assert sum(row["repair_status"] == "ACCEPT" for row in rows) == 420
    write_new(args.output / "coverage-before-union.json", rows)
    write_new(args.output / "coverage-before-union-summary.json", {
        role: summarize(rows if role == "all" else [r for r in rows if r["role"] == role])
        for role in ("all", "own_reference", "own_original", "cross_source")})
    frozen_coverage = digest(args.output / "coverage-before-union.json")

    # Union outcomes are first accessed after coverage selection and results are frozen.
    union_records = {row["id"]: row for row in records if row["stage"] == "union"}
    assert len(union_records) == len(rows)
    for row, (circuit, names, roots, task, points) in zip(rows, held):
        union_task = dict(task)
        union_task["id"] = task["id"].removesuffix("-repair") + "-union"
        union_task["points"] = [list(p) for p in points]
        old = union_records[union_task["id"]]
        assert symbolic.task_identity(union_task) == old["task_sha256"]
        observed = boolean_status(symbolic, circuit, names, roots, points)
        assert observed == old["status"]
        row["union_status"] = observed
        if row["repair_status"] == "REFUTED":
            assert observed == "REFUTED"
        if row["repair_status"] == "ACCEPT" and row["support_covered"]:
            assert observed == "ACCEPT"
    assert digest(args.output / "coverage-before-union.json") == frozen_coverage
    for name, expected in source_bindings.items():
        assert digest(artifact / name) == expected, name
    assert digest(args.corpus) == protocol["inputs"]["corpus"]
    assert digest(args.archive) == protocol["inputs"]["archive"]
    assert digest(args.reference / "summary.json") == protocol["inputs"]["reference_summary"]
    for name, expected in prior_summary["records"].items():
        assert digest(args.reference / name) == expected, name
    write_new(args.output / "coverage-with-union-outcomes.json", rows)
    result = {"outcome": "PASS_SIGNED_COVERAGE_AUDIT", "source_inputs_unchanged": True,
              "coverage_record_identity": frozen_coverage,
              "groups": {role: summarize(rows if role == "all" else [r for r in rows if r["role"] == role])
                         for role in ("all", "own_reference", "own_original", "cross_source")},
              "by_problem": {problem: summarize([r for r in rows if r["problem"] == problem])
                             for problem in sorted({r["problem"] for r in rows})}}
    write_new(args.output / "summary.json", result)
    print(json.dumps({"outcome": result["outcome"], "groups": result["groups"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
