"""Matched direct controls for the signed exact-point receiver.

The live-vector control computes the static dependency closure of obligations
and candidate events at every supplied point. The projected-live control
computes each node in that closure on every distinct projection of the actual
point set onto that node's global support. Neither control receives evidence.
Both return the existing complete, canonically ordered diagnostic.

These controls share source admission and lowering with int32_circuit. They
are cost ablations, not independent source-semantics oracles.
"""
from __future__ import annotations

import proof_dag_checker as core
import int32_circuit as signed
from demand_evaluator import _Counter, _Memo, _closure, _supports


def _task(task):
    circuit, programs, roots, names, _kind, _labels = signed.build_task(task)
    events = programs["candidate"].events
    live = _closure(circuit, (*roots, *(node for _site, reachable, guard in events
                                       for node in (reachable, guard))))
    encoded = [tuple(value & core.MASK for value in point) for point in task["points"]]
    return circuit, roots, names, events, live, encoded


def evaluate_live(task):
    """Compute each live node at each actual input, without a supplied packet."""
    circuit, roots, names, events, live, encoded = _task(task)
    positions = {name: i for i, name in enumerate(names)}
    vectors = [None] * len(circuit.nodes)
    for index in live:
        node = circuit.nodes[index]
        op = node[0]
        vectors[index] = [
            node[1] if op in {"b", "u"} else point[positions[node[1]]]
            if op == "input" else
            core.local_value(op, tuple(vectors[child][column] for child in node[1:]))
            for column, point in enumerate(encoded)
        ]
    result = core.classify_vectors(task["points"], roots, events, vectors)
    return {**result, "semantic_cells": len(live) * len(encoded),
            "nodes": len(circuit.nodes), "live_nodes": len(live),
            "mode": "int32-live-vector"}


def evaluate_projected_live(task):
    """Materialize all live support classes in an exact, possibly correlated set."""
    circuit, roots, names, events, live, encoded = _task(task)
    count = _Counter(None)
    supports = _supports(circuit, names, count)
    memo = _Memo(circuit, supports, count)
    projection_work = {"points_scanned": 0, "key_coordinates": 0,
                       "unique_representatives": 0, "projection_queries": 0,
                       "encoded_coordinates": len(encoded) * len(names)}
    projected_cells = 0
    for node in live:
        support = supports[node]
        chosen = {}
        projection_work["projection_queries"] += 1
        for index, point in enumerate(encoded):
            projection_work["points_scanned"] += 1
            projection_work["key_coordinates"] += len(support)
            chosen.setdefault(tuple(point[j] for j in support), index)
        projected_cells += len(chosen)
        projection_work["unique_representatives"] += len(chosen)
        for index in chosen.values():
            memo.get(node, encoded[index])
    if count.values["semantic_cells"] != projected_cells:
        raise RuntimeError("projected-live exact-point work accounting")

    # Expand only classification roots and event observations. Every queried
    # key was already materialized; this adds lookups, never semantic cells.
    observations = set(roots)
    observations.update(node for _site, reachable, guard in events
                        for node in (reachable, guard))
    vectors = [None] * len(circuit.nodes)
    for node in sorted(observations):
        vectors[node] = [memo.get(node, point) for point in encoded]
    result = core.classify_vectors(task["points"], roots, events, vectors)
    if count.values["semantic_cells"] != projected_cells:
        raise RuntimeError("classification requested an unmaterialized support class")
    return {**result, "semantic_cells": projected_cells,
            "nodes": len(circuit.nodes), "live_nodes": len(live),
            "counters": count.values, "projection_work": projection_work,
            "mode": "int32-projected-live"}
