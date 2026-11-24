"""Conditional evaluation with a separate dense memo for each actual input.

This matched direct control retains the support-keyed evaluator's obligation
priority, conditional rules, trace construction and canonical minimization.
It removes global-support analysis, projection representative selection and
cross-input sharing. Each memo entry is addressed by an input index and node
identifier; every stored value still has the receiver's exact Boolean/word type.

The traversal and its operation counters deliberately follow the released
support memo. The experiment compares complete receiving implementations,
not abstract instruction counts or a compiler-independent speed guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import proof_dag_checker as core
import int32_circuit as signed
from demand_evaluator import _Counter


@dataclass
class _Frame:
    node: int
    values: list = field(default_factory=list)


class PointMemo:
    """Memoize each (actual input, node) at most once; never invent points."""

    def __init__(self, circuit, names, points, count):
        self.circuit = circuit
        self.positions = {name: i for i, name in enumerate(names)}
        self.points = points
        self.count = count
        # A row is allocated only on its first demand. All state is call-local.
        self.rows = [None] * len(points)
        self.maximum_stack_depth = 0

    def _query(self, node, values):
        self.count.add("cache_queries")
        value = values[node]
        if value is not None:
            self.count.add("cache_hits")
            return True, value
        return False, None

    def _store(self, node, value, values):
        expected = self.circuit.sorts[node]
        if expected == "bool":
            if type(value) is not bool:
                raise core.Invalid("point-demand Boolean local value")
        elif type(value) is not int or not 0 <= value <= core.MASK:
            raise core.Invalid("point-demand word local value")
        self.count.add("semantic_cells")
        self.count.add("cache_writes")
        values[node] = value

    def get(self, node, point_index):
        stored = self.rows[point_index]
        if stored is None:
            stored = self.rows[point_index] = [None] * len(self.circuit.nodes)
        hit, value = self._query(node, stored)
        if hit:
            return value
        stack = [_Frame(node)]
        while stack:
            self.maximum_stack_depth = max(self.maximum_stack_depth, len(stack))
            frame = stack[-1]
            term = self.circuit.nodes[frame.node]
            op, values = term[0], frame.values
            child = None
            ready = False
            if op in {"b", "u"}:
                value, ready = term[1], True
            elif op == "input":
                value, ready = self.points[point_index][self.positions[term[1]]], True
            elif op in {"and", "or"}:
                if not values:
                    child = term[1]
                elif len(values) == 1:
                    self.count.add("conditional_choices")
                    decisive = (op == "and" and not values[0]) or (op == "or" and values[0])
                    if decisive:
                        value, ready = bool(values[0]), True
                    else:
                        child = term[2]
                else:
                    value, ready = core.local_value(op, tuple(values)), True
            elif op == "ite":
                if not values:
                    child = term[1]
                elif len(values) == 1:
                    self.count.add("conditional_choices")
                    child = term[2] if values[0] else term[3]
                else:
                    value, ready = values[1], True
            elif len(values) < len(term) - 1:
                child = term[len(values) + 1]
            else:
                value, ready = core.local_value(op, tuple(values)), True
            if ready:
                self._store(frame.node, value, stored)
                stack.pop()
                if stack:
                    stack[-1].values.append(value)
                else:
                    return value
            else:
                hit, value = self._query(child, stored)
                if hit:
                    frame.values.append(value)
                else:
                    stack.append(_Frame(child))
        raise RuntimeError("point-demand empty computation")


def evaluate_point_demand(task):
    """Return the complete canonical decision on the actual signed point set."""
    circuit, programs, roots, names, _kind, _labels = signed.build_task(task)
    points = task["points"]
    encoded = [tuple(value & core.MASK for value in point) for point in points]
    count = _Counter(None)
    memo = PointMemo(circuit, names, encoded, count)
    events = programs["candidate"].events
    witness = None
    for obligation, root in zip(core.OBLIGATIONS, roots):
        failed = False
        for index in range(len(points)):
            count.add("root_predicate_tests")
            if not memo.get(root, index):
                failed = True
                break
        if not failed:
            continue
        best = None
        for index in range(len(points)):
            count.add("diagnostic_points")
            if memo.get(root, index):
                continue
            trace = []
            for site, reachable, guard in events:
                count.add("trace_events_examined")
                if memo.get(reachable, index):
                    trace.append([site, int(bool(memo.get(guard, index)))])
            key = (trace, points[index])
            if best is None or key < best:
                best = key
        if best is None:
            raise RuntimeError("point-demand diagnostic existence")
        witness = {"obligation": obligation, "trace": best[0], "input": best[1]}
        break
    cells = count.values["semantic_cells"]
    if cells != count.values["cache_writes"] or count.values["cache_queries"] != cells + count.values["cache_hits"]:
        raise RuntimeError("point-demand cache accounting")
    return {"status": "REFUTED" if witness else "ACCEPT", "witness": witness,
            "semantic_cells": cells, "counters": count.values,
            "allocated_point_rows": sum(row is not None for row in memo.rows),
            "allocated_value_slots": sum(len(row) for row in memo.rows if row is not None),
            "maximum_evaluation_stack_depth": memo.maximum_stack_depth,
            "nodes": len(circuit.nodes), "mode": "int32-point-demand"}
