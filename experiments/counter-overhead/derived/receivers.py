"""Demand kernels with measurement-only bookkeeping elided."""
from __future__ import annotations
from dataclasses import dataclass, field
import proof_dag_checker as core
import int32_circuit as signed
from int32_circuit import build_task

def support_sets(circuit, names):
    positions = {name: i for i, name in enumerate(names)}
    supports = []
    for node in circuit.nodes:
        if node[0] == 'input':
            support = (positions[node[1]],)
        elif node[0] in {'b', 'u'}:
            support = ()
        else:
            combined = set()
            for child in node[1:]:
                combined.update(supports[child])
            support = tuple(sorted(combined))
        supports.append(support)
    return tuple(supports)

@dataclass
class SupportFrame:
    node: int
    key: tuple[int, ...]
    values: list = field(default_factory=list)

class SupportMemo:

    def __init__(self, circuit, supports):
        self.circuit = circuit
        self.supports = supports
        self.tables = {}

    def _query(self, node, point):
        support = self.supports[node]
        key = tuple((point[i] for i in support))
        table = self.tables.setdefault(node, {})
        try:
            value = table[key]
        except KeyError:
            return (False, key, None)
        return (True, key, value)

    def _store(self, frame, value):
        expected = self.circuit.sorts[frame.node]
        if expected == 'bool':
            if type(value) is not bool:
                raise core.Invalid('demand evaluator Boolean local value')
        elif type(value) is not int or not 0 <= value <= core.MASK:
            raise core.Invalid('demand evaluator word local value')
        self.tables[frame.node][frame.key] = value

    def get(self, node, point):
        hit, key, value = self._query(node, point)
        if hit:
            return value
        stack = [SupportFrame(node, key)]
        while stack:
            frame = stack[-1]
            term = self.circuit.nodes[frame.node]
            op, values = (term[0], frame.values)
            child = None
            ready = False
            if op in {'b', 'u'}:
                value, ready = (term[1], True)
            elif op == 'input':
                value, ready = (frame.key[0], True)
            elif op in {'and', 'or'}:
                if not values:
                    child = term[1]
                elif len(values) == 1:
                    decisive = op == 'and' and (not values[0]) or (op == 'or' and values[0])
                    if decisive:
                        value, ready = (bool(values[0]), True)
                    else:
                        child = term[2]
                else:
                    value, ready = (core.local_value(op, tuple(values)), True)
            elif op == 'ite':
                if not values:
                    child = term[1]
                elif len(values) == 1:
                    child = term[2] if values[0] else term[3]
                else:
                    value, ready = (values[1], True)
            elif len(values) < len(term) - 1:
                child = term[len(values) + 1]
            else:
                value, ready = (core.local_value(op, tuple(values)), True)
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
                    stack.append(SupportFrame(child, key))
        raise RuntimeError('demand evaluator empty computation')

def evaluate_support(task):
    """Support-keyed, demand-driven decision on an exact finite point set.

    A projected class retains its least actual signed input, rather than
    filling omitted axes independently. This matters for correlated tests.
    """
    from _repairseal_counter_free_derived import SupportMemo, support_sets
    circuit, programs, roots, names, _kind, _labels = build_task(task)
    points = task['points']
    encoded = [tuple((value & core.MASK for value in point)) for point in points]
    supports = support_sets(circuit, names)
    memo = SupportMemo(circuit, supports)
    events = programs['candidate'].events

    def representatives(support):
        chosen = {}
        for i, point in enumerate(encoded):
            key = tuple((point[j] for j in support))
            chosen.setdefault(key, i)
        return list(chosen.values())
    witness = None
    for obligation, root in zip(core.OBLIGATIONS, roots):
        failed = False
        for i in representatives(supports[root]):
            if not memo.get(root, encoded[i]):
                failed = True
                break
        if not failed:
            continue
        joint = set(supports[root])
        for _site, reachable, guard in events:
            joint.update(supports[reachable])
            joint.update(supports[guard])
        best = None
        for i in representatives(tuple(sorted(joint))):
            if memo.get(root, encoded[i]):
                continue
            trace = []
            for site, reachable, guard in events:
                if memo.get(reachable, encoded[i]):
                    trace.append([site, int(bool(memo.get(guard, encoded[i])))])
            key = (trace, points[i])
            if best is None or key < best:
                best = key
        if best is None:
            raise RuntimeError('int32 diagnostic existence')
        witness = {'obligation': obligation, 'trace': best[0], 'input': best[1]}
        break
    return {'status': 'REFUTED' if witness else 'ACCEPT', 'witness': witness}

@dataclass
class PointFrame:
    node: int
    values: list = field(default_factory=list)

class PointMemo:
    """Memoize each (actual input, node) at most once; never invent points."""

    def __init__(self, circuit, names, points):
        self.circuit = circuit
        self.positions = {name: i for i, name in enumerate(names)}
        self.points = points
        self.rows = [None] * len(points)

    def _query(self, node, values):
        value = values[node]
        if value is not None:
            return (True, value)
        return (False, None)

    def _store(self, node, value, values):
        expected = self.circuit.sorts[node]
        if expected == 'bool':
            if type(value) is not bool:
                raise core.Invalid('point-demand Boolean local value')
        elif type(value) is not int or not 0 <= value <= core.MASK:
            raise core.Invalid('point-demand word local value')
        values[node] = value

    def get(self, node, point_index):
        stored = self.rows[point_index]
        if stored is None:
            stored = self.rows[point_index] = [None] * len(self.circuit.nodes)
        hit, value = self._query(node, stored)
        if hit:
            return value
        stack = [PointFrame(node)]
        while stack:
            frame = stack[-1]
            term = self.circuit.nodes[frame.node]
            op, values = (term[0], frame.values)
            child = None
            ready = False
            if op in {'b', 'u'}:
                value, ready = (term[1], True)
            elif op == 'input':
                value, ready = (self.points[point_index][self.positions[term[1]]], True)
            elif op in {'and', 'or'}:
                if not values:
                    child = term[1]
                elif len(values) == 1:
                    decisive = op == 'and' and (not values[0]) or (op == 'or' and values[0])
                    if decisive:
                        value, ready = (bool(values[0]), True)
                    else:
                        child = term[2]
                else:
                    value, ready = (core.local_value(op, tuple(values)), True)
            elif op == 'ite':
                if not values:
                    child = term[1]
                elif len(values) == 1:
                    child = term[2] if values[0] else term[3]
                else:
                    value, ready = (values[1], True)
            elif len(values) < len(term) - 1:
                child = term[len(values) + 1]
            else:
                value, ready = (core.local_value(op, tuple(values)), True)
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
                    stack.append(PointFrame(child))
        raise RuntimeError('point-demand empty computation')

def evaluate_point(task):
    """Return the complete canonical decision on the actual signed point set."""
    circuit, programs, roots, names, _kind, _labels = signed.build_task(task)
    points = task['points']
    encoded = [tuple((value & core.MASK for value in point)) for point in points]
    memo = PointMemo(circuit, names, encoded)
    events = programs['candidate'].events
    witness = None
    for obligation, root in zip(core.OBLIGATIONS, roots):
        failed = False
        for index in range(len(points)):
            if not memo.get(root, index):
                failed = True
                break
        if not failed:
            continue
        best = None
        for index in range(len(points)):
            if memo.get(root, index):
                continue
            trace = []
            for site, reachable, guard in events:
                if memo.get(reachable, index):
                    trace.append([site, int(bool(memo.get(guard, index)))])
            key = (trace, points[index])
            if best is None or key < best:
                best = key
        if best is None:
            raise RuntimeError('point-demand diagnostic existence')
        witness = {'obligation': obligation, 'trace': best[0], 'input': best[1]}
        break
    return {'status': 'REFUTED' if witness else 'ACCEPT', 'witness': witness}
