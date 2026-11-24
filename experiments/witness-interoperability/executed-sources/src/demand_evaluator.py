"""Certificate-free finite decisions with support-keyed demand evaluation.

Both entry points use the existing receiver's request admission, reconstruction,
word semantics, obligation order and candidate event order.  A node value is
memoized by the values of its globally derived free input variables.  No support
is inferred from a vector that happens to be constant on a sample.

``evaluate_projected_live`` materializes every live node on its own projected
domain.  ``evaluate_demand`` additionally visits obligations in priority order,
uses conditional local rules, and requests trace values only for inputs that
fail the first failed obligation.  Both preserve the complete canonical result.

The counters describe local semantic values and named logical operations.  They
are not instruction counts or elapsed-time measurements.  Parsing, circuit
reconstruction and Python allocation are outside those counters.  A zero value
for one category is never a claim of zero total receiving cost.  All memo state
is confined to one call; callback exceptions propagate without returning a
semantic result or publishing reusable state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import itertools
import math
from typing import Callable

import proof_dag_checker as core


_KINDS = (
    "semantic_cells", "cache_queries", "cache_hits", "cache_writes",
    "key_coordinates", "support_nodes", "support_edges",
    "support_coordinate_visits", "axis_values_copied", "axes_copied",
    "projected_point_visits", "point_coordinates_filled",
    "root_predicate_tests", "trace_events_examined", "conditional_choices",
    "diagnostic_points", "diagnostic_candidates", "diagnostic_key_comparisons",
)


class _Counter:
    def __init__(self, callback):
        self.values = dict.fromkeys(_KINDS, 0)
        self.callback = callback

    def add(self, kind: str, amount: int = 1) -> None:
        self.values[kind] += amount
        if self.callback is not None and amount:
            self.callback("demand_" + kind, amount)


def _children(node):
    return () if node[0] in {"b", "u", "input"} else node[1:]


def _closure(circuit, roots):
    pending = list(roots)
    selected = set()
    while pending:
        node = pending.pop()
        if node not in selected:
            selected.add(node)
            pending.extend(_children(circuit.nodes[node]))
    return tuple(sorted(selected))


def _supports(circuit, names, count):
    positions = {name: i for i, name in enumerate(names)}
    supports = []
    for node in circuit.nodes:
        count.add("support_nodes")
        if node[0] == "input":
            support = (positions[node[1]],)
        elif node[0] in {"b", "u"}:
            support = ()
        else:
            combined = set()
            for child in node[1:]:
                count.add("support_edges")
                count.add("support_coordinate_visits", len(supports[child]))
                combined.update(supports[child])
            support = tuple(sorted(combined))
        supports.append(support)
    return tuple(supports)


@dataclass
class _Frame:
    node: int
    key: tuple[int, ...]
    values: list = field(default_factory=list)


class _Memo:
    def __init__(self, circuit, supports, count):
        self.circuit = circuit
        self.supports = supports
        self.count = count
        self.tables = {}
        self.maximum_stack_depth = 0

    def _query(self, node, point):
        self.count.add("cache_queries")
        support = self.supports[node]
        self.count.add("key_coordinates", len(support))
        key = tuple(point[i] for i in support)
        table = self.tables.setdefault(node, {})
        try:
            value = table[key]
        except KeyError:
            return False, key, None
        self.count.add("cache_hits")
        return True, key, value

    def _store(self, frame, value):
        expected = self.circuit.sorts[frame.node]
        if expected == "bool":
            if type(value) is not bool:
                raise core.Invalid("demand evaluator Boolean local value")
        elif type(value) is not int or not 0 <= value <= core.MASK:
            raise core.Invalid("demand evaluator word local value")
        self.count.add("semantic_cells")
        self.count.add("cache_writes")
        self.tables[frame.node][frame.key] = value

    def get(self, node, point):
        hit, key, value = self._query(node, point)
        if hit:
            return value
        stack = [_Frame(node, key)]
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
                value, ready = frame.key[0], True
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
                self._store(frame, value)
                stack.pop()
                if stack:
                    stack[-1].values.append(value)
                else:
                    return value
            else:
                hit, key, value = self._query(child, point)
                if hit:
                    frame.values.append(value)
                else:
                    stack.append(_Frame(child, key))
        raise RuntimeError("demand evaluator empty computation")


def _points(axes, support, count):
    for values in itertools.product(*(axes[i] for i in support)):
        count.add("projected_point_visits")
        count.add("point_coordinates_filled", len(axes) + len(support))
        point = [axis[0] for axis in axes]
        for coordinate, value in zip(support, values):
            point[coordinate] = value
        yield point


def _run(request, callback, projected_live):
    domains, names = core.validate_request_fields(request)
    # Snapshot only fields already admitted as exact built-in JSON types.
    snapshot = {"id": request["id"], "word_bits": request["word_bits"],
                "inputs": {name: list(domains[name]) for name in names},
                **{role: request[role] for role in core.ROLES},
                "repair_guard": request["repair_guard"]}
    axes = tuple(tuple(snapshot["inputs"][name]) for name in names)
    circuit, programs, _guard, roots = core.build_expected(snapshot)
    count = _Counter(callback)
    count.add("axes_copied", len(axes))
    count.add("axis_values_copied", sum(map(len, axes)))
    supports = _supports(circuit, names, count)
    events = programs["candidate"].events
    event_roots = [node for _site, reachable, guard in events for node in (reachable, guard)]
    live = _closure(circuit, (*roots, *event_roots))
    live_projected_cells = sum(math.prod(len(axes[i]) for i in supports[node]) for node in live)
    memo = _Memo(circuit, supports, count)
    if projected_live:
        for node in live:
            for point in _points(axes, supports[node], count):
                memo.get(node, point)
        if count.values["semantic_cells"] != live_projected_cells:
            raise RuntimeError("projected live cell accounting")
    precompute_cells = count.values["semantic_cells"]
    failure = None
    for obligation, root in zip(core.OBLIGATIONS, roots):
        for point in _points(axes, supports[root], count):
            count.add("root_predicate_tests")
            if not memo.get(root, point):
                failure = obligation, root
                break
        if failure is not None:
            break
    decision_cells = count.values["semantic_cells"] - precompute_cells
    diagnostic_support = ()
    if failure is None:
        result = {"status": "ACCEPT", "witness": None}
    else:
        obligation, root = failure
        diagnostic_support = tuple(sorted(set(supports[root]).union(
            *(set(supports[node]) for node in event_roots))))
        least = None
        for point in _points(axes, diagnostic_support, count):
            count.add("diagnostic_points")
            count.add("root_predicate_tests")
            if memo.get(root, point):
                continue
            count.add("diagnostic_candidates")
            trace = []
            for site, reachable, guard in events:
                count.add("trace_events_examined")
                if memo.get(reachable, point):
                    trace.append((site, int(memo.get(guard, point))))
            key = (tuple(trace), tuple(point))
            if least is not None:
                count.add("diagnostic_key_comparisons")
            if least is None or key < least:
                least = key
        if least is None:
            raise RuntimeError("failed obligation has no diagnostic")
        result = {"status": "REFUTED", "witness": {
            "obligation": obligation, "trace": [list(event) for event in least[0]],
            "input": list(least[1])}}
    cells = count.values["semantic_cells"]
    if cells != count.values["cache_writes"] or count.values["cache_queries"] != cells + count.values["cache_hits"]:
        raise RuntimeError("demand cache accounting")
    if cells > live_projected_cells:
        raise RuntimeError("demand work exceeds projected live support space")
    truth_support = set().union(*(set(supports[root]) for root in roots))
    result.update({
        "mode": "direct-projected-live" if projected_live else "direct-demand",
        "constructed_nodes": len(circuit.nodes),
        "checked_nodes": sum(bool(table) for table in memo.tables.values()),
        "checked_cells": cells,
        "input_points": math.prod(map(len, axes)),
        "live_nodes": len(live), "projected_live_cell_bound": live_projected_cells,
        "obligation_supports": [[names[i] for i in supports[root]] for root in roots],
        "truth_irrelevant_axes": [name for i, name in enumerate(names) if i not in truth_support],
        "diagnostic_support": [names[i] for i in diagnostic_support],
        "maximum_evaluation_stack_depth": memo.maximum_stack_depth,
        "phase_cells": {"projection_precompute": precompute_cells,
                        "decision_search": decision_cells,
                        "canonical_diagnostic": cells - precompute_cells - decision_cells},
        "work_counts": dict(count.values),
        "work_count_scope": "Semantic values and named logical visits/queries; parsing, reconstruction, allocation and elapsed time are separate costs.",
    })
    return result


def evaluate_demand(request: dict, count: Callable[[str, int], None] | None = None) -> dict:
    """Return the complete canonical decision using per-call demand memoization."""
    return _run(request, count, projected_live=False)


def evaluate_projected_live(request: dict, count: Callable[[str, int], None] | None = None) -> dict:
    """Control that computes every live node at every global-support projection."""
    return _run(request, count, projected_live=True)
