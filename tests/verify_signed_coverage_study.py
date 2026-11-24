#!/usr/bin/env python3
"""Recompute signed support coverage from retained DAGs, without source archives.

This verifier does not import the study writer or receiver.  It independently
traverses the retained circuit, evaluates its total local word rules, projects
the actual point sets, and reconciles every aggregate with the recorded study.
It checks a structural record; source admission and C correspondence remain
the separately recorded responsibilities of the original-source experiments.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

MASK = (1 << 32) - 1
ARITIES = {"not": 1, "inv": 1, "and": 2, "or": 2, "ite": 3,
           **dict.fromkeys(("+", "-", "*", "/", "%", "<<", ">>", "&", "|", "^",
                            "==", "!=", "<", "<=", ">", ">="), 2)}


def read(path):
    return json.loads(path.read_text())


def identity(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(left, right):
    assert type(left) is type(right), (type(left).__name__, type(right).__name__)
    if type(left) is dict:
        assert left.keys() == right.keys()
        for key in left:
            exact(left[key], right[key])
    elif type(left) is list:
        assert len(left) == len(right)
        for a, b in zip(left, right):
            exact(a, b)
    else:
        assert left == right, (left, right)


def point_set(values, arity):
    assert type(values) is list and values
    for value in values:
        assert type(value) is list and len(value) == arity
        assert all(type(x) is int and -(1 << 31) <= x < (1 << 31) for x in value)
    result = [tuple(value) for value in values]
    assert result == sorted(set(result))
    return result


def root_supports(nodes, roots, names):
    assert type(nodes) is list and nodes
    assert len(names) == len(set(names)) and all(type(name) is str for name in names)
    positions = {name: index for index, name in enumerate(names)}
    for number, node in enumerate(nodes):
        assert type(node) is list and node and type(node[0]) is str
        operation = node[0]
        if operation == "input":
            assert len(node) == 2 and node[1] in positions
        elif operation == "b":
            assert len(node) == 2 and type(node[1]) is bool
        elif operation == "u":
            assert len(node) == 2 and type(node[1]) is int and 0 <= node[1] <= MASK
        else:
            assert operation in ARITIES and len(node) == ARITIES[operation] + 1
            assert all(type(child) is int and 0 <= child < number for child in node[1:])
    assert len(roots) == 3 and all(type(root) is int and 0 <= root < len(nodes) for root in roots)
    result = []
    for root in roots:
        todo, seen, inputs = [root], set(), set()
        while todo:
            node_id = todo.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            node = nodes[node_id]
            if node[0] == "input":
                inputs.add(positions[node[1]])
            elif node[0] not in {"u", "b"}:
                todo.extend(node[1:])
        result.append(sorted(inputs))
    return result


def operation_value(operation, arguments):
    if operation == "not": return not arguments[0]
    if operation == "inv": return MASK ^ arguments[0]
    if operation == "and": return bool(arguments[0] and arguments[1])
    if operation == "or": return bool(arguments[0] or arguments[1])
    if operation == "ite": return arguments[1] if arguments[0] else arguments[2]
    left, right = arguments
    if operation == "+": return (left + right) & MASK
    if operation == "-": return (left - right) & MASK
    if operation == "*": return (left * right) & MASK
    if operation == "/": return left // right if right else 0
    if operation == "%": return left % right if right else 0
    if operation == "<<": return (left << right) & MASK if right < 32 else 0
    if operation == ">>": return left >> right if right < 32 else 0
    if operation == "&": return left & right
    if operation == "|": return left | right
    if operation == "^": return left ^ right
    if operation == "==": return left == right
    if operation == "!=": return left != right
    if operation == "<": return left < right
    if operation == "<=": return left <= right
    if operation == ">": return left > right
    if operation == ">=": return left >= right
    raise AssertionError(operation)


def observed_status(nodes, names, roots, points):
    positions = {name: index for index, name in enumerate(names)}
    failed = False
    for point in points:
        encoded = [value & MASK for value in point]
        values = []
        for node in nodes:
            op = node[0]
            if op in {"b", "u"}: value = node[1]
            elif op == "input": value = encoded[positions[node[1]]]
            else: value = operation_value(op, [values[child] for child in node[1:]])
            values.append(value)
        assert all(type(values[root]) is bool for root in roots)
        if not all(values[root] for root in roots):
            failed = True
    return "REFUTED" if failed else "ACCEPT"


def summary(rows):
    accepted = [r for r in rows if r["repair_status"] == "ACCEPT"]
    covered = [r for r in accepted if r["support_covered"]]
    subset = [r for r in covered if r["new_full_inputs"] and r["root_class"] == "nonempty_syntactic_support"]
    return {
        "combinations": len(rows), "subjects": len({r["subject"] for r in rows}),
        "problems": len({r["problem"] for r in rows}),
        "repair_status": dict(Counter(r["repair_status"] for r in rows)),
        "accepted_repair": len(accepted),
        "accepted_with_new_full_inputs": sum(bool(r["new_full_inputs"]) for r in accepted),
        "accepted_unchanged_point_sets": sum(not r["new_full_inputs"] for r in accepted),
        "accepted_by_root_class": dict(Counter(r["root_class"] for r in accepted)),
        "accepted_with_full_input_support": sum(any(len(o["support_positions"]) == len(r["input_order"])
                                                    for o in r["obligations"]) for r in accepted),
        "covered_accepted": len(covered), "uncovered_accepted": len(accepted) - len(covered),
        "covered_with_new_full_inputs": sum(bool(r["new_full_inputs"]) for r in covered),
        "covered_unchanged_point_sets": sum(not r["new_full_inputs"] for r in covered),
        "covered_by_root_class": dict(Counter(r["root_class"] for r in covered)),
        "covered_new_inputs_by_root_class": dict(Counter(r["root_class"] for r in covered if r["new_full_inputs"])),
        "nonempty_support_covered_new_inputs": len(subset),
        "nonempty_support_covered_new_subjects": len({r["subject"] for r in subset}),
        "nonempty_support_covered_new_problems": len({r["problem"] for r in subset}),
        "union_status": dict(Counter(r["union_status"] for r in rows)),
        "covered_union_status": dict(Counter(r["union_status"] for r in covered)),
        "uncovered_accepted_union_status": dict(Counter(r["union_status"] for r in accepted if not r["support_covered"])),
        "nonempty_support_covered_new_union_status": dict(Counter(r["union_status"] for r in subset)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Assertions must remain enabled.")
    if args.output is not None and args.output.exists():
        parser.error("output must be a new file")
    protocol = read(args.study / "protocol.json")
    before = read(args.study / "coverage-before-union.json")
    rows = read(args.study / "coverage-with-union-outcomes.json")
    reported = read(args.study / "summary.json")
    assert reported["outcome"] == "PASS_SIGNED_COVERAGE_AUDIT" and reported["source_inputs_unchanged"] is True
    assert protocol["planned_combinations"] == len(before) == len(rows) == 739
    assert identity(args.study / "coverage-before-union.json") == reported["coverage_record_identity"]
    assert identity(args.reference / "summary.json") == protocol["inputs"]["reference_summary"]
    assert identity(args.reference / "requests.json") == protocol["inputs"]["reference_requests"]
    reference = read(args.reference / "requests.json")
    reference_by_id = {r["id"]: r for r in reference}
    assert len(reference_by_id) == len(reference) == 1478
    reference_repairs = {r["id"] for r in reference if r["stage"] == "repair"}
    assert {r["repair_request_id"] for r in rows} == reference_repairs
    assert [r["index"] for r in rows] == list(range(739))
    total_nodes = total_point_observations = total_node_values = 0
    for original, row in zip(before, rows):
        exact(original, {key: value for key, value in row.items() if key != "union_status"})
        source = row["sources"]
        role = ("own_reference" if source["candidate"] == source["reference"] else
                "own_original" if source["candidate"] == source["original"] else "cross_source")
        assert row["role"] == role
        assert row["root_class"] in protocol["root_classes"]
        repair = point_set(row["repair_points"], len(row["input_order"]))
        union = point_set(row["union_points"], len(row["input_order"]))
        assert set(repair) <= set(union)
        exact(row["new_full_inputs"], [list(p) for p in sorted(set(union) - set(repair))])
        nodes, roots = row["dag_nodes"], row["obligation_roots"]
        assert row["nodes"] == len(nodes)
        supports = root_supports(nodes, roots, row["input_order"])
        literal = all(nodes[root] == ["b", True] for root in roots)
        exact(row["all_obligation_roots_literal_true"], literal)
        category = ("all_literal_true" if literal else "nonempty_syntactic_support" if any(supports)
                    else "empty_support_not_all_literal_true")
        assert row["root_class"] == category
        flags = []
        assert len(row["obligations"]) == len(roots) == 3
        for number, (root, support, declared) in enumerate(zip(roots, supports, row["obligations"])):
            old = {tuple(p[i] for i in support) for p in repair}
            enlarged = {tuple(p[i] for i in support) for p in union}
            missing = sorted(enlarged - old)
            expected = {"obligation": ("defined", "repair", "preserve")[number], "root": root,
                        "root_node": nodes[root], "support_positions": support,
                        "support_names": [row["input_order"][i] for i in support],
                        "repair_projection_count": len(old), "union_projection_count": len(enlarged),
                        "uncovered_keys": [list(key) for key in missing]}
            exact(declared, expected)
            flags.append(not missing)
        exact(row["support_covered"], all(flags))
        for stage, points in (("repair", repair), ("union", union)):
            request_id = row["repair_request_id"].removesuffix("-repair") + "-" + stage
            ref = reference_by_id[request_id]
            exact(ref["sources"], source)
            exact(ref["points"], [list(p) for p in points])
            assert (ref["subject"], ref["problem"], ref["stage"]) == (row["subject"], row["problem"], stage)
            actual = observed_status(nodes, row["input_order"], roots, points)
            assert actual == row[stage + "_status"] == ref["status"]
            total_point_observations += len(points)
            total_node_values += len(nodes) * len(points)
        total_nodes += len(nodes)
        if row["repair_status"] == "ACCEPT" and row["support_covered"]:
            assert row["union_status"] == "ACCEPT"
    groups = {role: summary(rows if role == "all" else [r for r in rows if r["role"] == role])
              for role in ("all", "own_reference", "own_original", "cross_source")}
    exact(groups, reported["groups"])
    exact({problem: summary([r for r in rows if r["problem"] == problem])
           for problem in sorted({r["problem"] for r in rows})}, reported["by_problem"])
    before_summaries = read(args.study / "coverage-before-union-summary.json")
    for role, aggregate in groups.items():
        exact(before_summaries[role], {key: value for key, value in aggregate.items() if "union_status" not in key})
    result = {"outcome": "PASS_INDEPENDENT_SIGNED_COVERAGE_RECOMPUTATION", "combinations": len(rows),
              "circuit_nodes": total_nodes, "point_observations": total_point_observations,
              "local_values": total_node_values, "groups": groups,
              "scope": "Retained DAG syntax, structural support, exact point projection, Boolean local-rule evaluation and aggregate reconciliation; no external archive or C compiler is used."}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
