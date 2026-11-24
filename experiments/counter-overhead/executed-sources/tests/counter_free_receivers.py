"""Derive demand receivers with measurement bookkeeping removed.

The source algorithms remain in their original files. This module selects
their actual syntax trees and applies an exact, scope-specific whitelist.
Every removed statement and changed signature is retained in a derivation
manifest. No no-op counter or conditional counting branch remains in the
derived traversal. Type checks, local rules, supports, memo keys, traversal,
source admission and canonical diagnostics are preserved.
"""
from __future__ import annotations

import ast
from collections import Counter
from contextlib import contextmanager
import copy
import hashlib
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
import demand_evaluator as demand
import int32_circuit as signed
import int32_point_demand as point

SOURCES = ("src/demand_evaluator.py", "src/int32_circuit.py",
           "tests/int32_point_demand.py")
SELECTIONS = {
    SOURCES[0]: ("_supports", "_Frame", "_Memo"),
    SOURCES[1]: ("evaluate_direct",),
    SOURCES[2]: ("_Frame", "PointMemo", "evaluate_point_demand"),
}
RENAMES = {
    SOURCES[0]: {"_supports": "support_sets", "_Frame": "SupportFrame", "_Memo": "SupportMemo"},
    SOURCES[1]: {"evaluate_direct": "evaluate_support", "_supports": "support_sets", "_Memo": "SupportMemo"},
    SOURCES[2]: {"_Frame": "PointFrame", "evaluate_point_demand": "evaluate_point"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(data):
    return hashlib.sha256(data).hexdigest()


def normalized(node):
    return ast.dump(node, annotate_fields=True, include_attributes=False)


def statement(text):
    body = ast.parse(text).body
    require(len(body) == 1, "one whitelist statement required")
    return normalized(body[0])


def expression(text):
    return normalized(ast.parse(text, mode="eval").body)


# A whitelist entry is tied to its source function/method and exact AST.
# Counts prevent a new or moved instrumentation site from being silently
# accepted as the same transformation.
REMOVALS = {}


def allow(source, scope, text, count=1):
    key = (source, scope, statement(text))
    require(key not in REMOVALS, "duplicate removal rule")
    REMOVALS[key] = count


for text in (
    'count.add("support_nodes")',
    'count.add("support_edges")',
    'count.add("support_coordinate_visits", len(supports[child]))',
):
    allow(SOURCES[0], "_supports", text)
for source, cls in ((SOURCES[0], "_Memo"), (SOURCES[2], "PointMemo")):
    allow(source, cls + ".__init__", "self.count = count")
    allow(source, cls + ".__init__", "self.maximum_stack_depth = 0")
    allow(source, cls + "._query", 'self.count.add("cache_queries")')
    allow(source, cls + "._query", 'self.count.add("cache_hits")')
    allow(source, cls + "._store", 'self.count.add("semantic_cells")')
    allow(source, cls + "._store", 'self.count.add("cache_writes")')
    allow(source, cls + ".get", "self.maximum_stack_depth = max(self.maximum_stack_depth, len(stack))")
    allow(source, cls + ".get", 'self.count.add("conditional_choices")', 2)
allow(SOURCES[0], "_Memo._query", 'self.count.add("key_coordinates", len(support))')
for source, fn in ((SOURCES[1], "evaluate_direct"), (SOURCES[2], "evaluate_point_demand")):
    allow(source, fn, "count = _Counter(None)")
    for kind in ("root_predicate_tests", "diagnostic_points", "trace_events_examined"):
        allow(source, fn, f'count.add("{kind}")')
allow(SOURCES[1], "evaluate_direct", """projection_work = {
    "points_scanned": 0, "key_coordinates": 0,
    "unique_representatives": 0, "projection_queries": 0,
    "encoded_coordinates": len(points) * len(names)}""")
for text in (
    'projection_work["projection_queries"] += 1',
    'projection_work["points_scanned"] += 1',
    'projection_work["key_coordinates"] += len(support)',
    'projection_work["unique_representatives"] += len(chosen)',
):
    allow(SOURCES[1], "evaluate_direct.representatives", text)
allow(SOURCES[2], "evaluate_point_demand", 'cells = count.values["semantic_cells"]')
allow(SOURCES[2], "evaluate_point_demand", """if cells != count.values["cache_writes"] or count.values["cache_queries"] != cells + count.values["cache_hits"]:
    raise RuntimeError("point-demand cache accounting")""")

SIGNATURES = {
    (SOURCES[0], "_supports"): ("circuit", "names", "count"),
    (SOURCES[0], "_Memo.__init__"): ("self", "circuit", "supports", "count"),
    (SOURCES[2], "PointMemo.__init__"): ("self", "circuit", "names", "points", "count"),
}
CALLS = {
    (SOURCES[1], "evaluate_direct", expression("_supports(circuit, names, count)")),
    (SOURCES[1], "evaluate_direct", expression("_Memo(circuit, supports, count)")),
    (SOURCES[2], "evaluate_point_demand", expression("PointMemo(circuit, names, encoded, count)")),
}
IMPORTS = {
    (SOURCES[1], "evaluate_direct"):
        statement("from demand_evaluator import _Counter, _Memo, _supports"),
}
RETURNS = {
    (SOURCES[1], "evaluate_direct"): statement("""return {
        "status": "REFUTED" if witness else "ACCEPT", "witness": witness,
        "semantic_cells": count.values["semantic_cells"], "counters": count.values,
        "projection_work": projection_work,
        "counter_scope": "local DAG values, named memo/support work, and point-set projection operations; source admission, allocation, and elapsed time excluded",
        "nodes": len(circuit.nodes), "mode": "int32-demand"}"""),
    (SOURCES[2], "evaluate_point_demand"): statement("""return {
        "status": "REFUTED" if witness else "ACCEPT", "witness": witness,
        "semantic_cells": cells, "counters": count.values,
        "allocated_point_rows": sum(row is not None for row in memo.rows),
        "allocated_value_slots": sum(len(row) for row in memo.rows if row is not None),
        "maximum_evaluation_stack_depth": memo.maximum_stack_depth,
        "nodes": len(circuit.nodes), "mode": "int32-point-demand"}"""),
}


class Elider(ast.NodeTransformer):
    def __init__(self, source):
        self.source = source
        self.scope = []
        self.removals = Counter()
        self.signatures = Counter()
        self.calls = Counter()
        self.returns = Counter()
        self.imports = Counter()
        self.changes = []

    @property
    def location(self):
        return self.source, ".".join(self.scope)

    def record(self, kind, before, after=None):
        self.changes.append({
            "source": self.source, "scope": ".".join(self.scope),
            "kind": kind, "line": getattr(before, "lineno", None),
            "before": ast.unparse(before),
            "after": None if after is None else ast.unparse(after),
        })

    def visit(self, node):
        if isinstance(node, ast.stmt):
            key = (*self.location, normalized(node))
            if key in REMOVALS:
                self.removals[key] += 1
                self.record("remove_measurement_statement", node)
                return None
        return super().visit(node)

    def visit_ClassDef(self, node):
        self.scope.append(node.name)
        node = self.generic_visit(node)
        self.scope.pop()
        return node

    def visit_FunctionDef(self, node):
        self.scope.append(node.name)
        if self.location in SIGNATURES:
            expected = SIGNATURES[self.location]
            require(tuple(arg.arg for arg in node.args.args) == expected and
                    not node.args.posonlyargs and not node.args.kwonlyargs and
                    not node.args.defaults and node.args.vararg is None and
                    node.args.kwarg is None, "unexpected measured-helper signature")
            before = copy.deepcopy(node.args)
            node.args.args.pop()
            self.signatures[self.location] += 1
            self.changes.append({
                "source": self.source, "scope": ".".join(self.scope),
                "kind": "remove_counter_parameter",
                "before": ast.unparse(before), "after": ast.unparse(node.args),
            })
        node = self.generic_visit(node)
        self.scope.pop()
        return node

    def visit_Call(self, node):
        key = (*self.location, normalized(node))
        if key in CALLS:
            before = copy.deepcopy(node)
            require(isinstance(node.args[-1], ast.Name) and node.args[-1].id == "count"
                    and not node.keywords, "unexpected counter argument")
            node.args.pop()
            self.calls[key] += 1
            self.record("remove_counter_argument", before, node)
        return self.generic_visit(node)

    def visit_ImportFrom(self, node):
        require(self.location in IMPORTS and normalized(node) == IMPORTS[self.location],
                "unexpected local helper import")
        # Preserve the per-call imports of the two functional helpers. Only
        # _Counter disappears; the other imports route to their exact derived
        # definitions rather than removing unrelated import overhead.
        replacement = ast.parse(
            "from _repairseal_counter_free_derived import SupportMemo, support_sets").body[0]
        self.imports[self.location] += 1
        self.record("route_local_helpers_to_derived_definitions", node, replacement)
        return replacement

    def visit_Return(self, node):
        if self.location in RETURNS:
            require(normalized(node) == RETURNS[self.location],
                    "unexpected result expression; measurement fields must be reviewed")
            before = copy.deepcopy(node)
            keep = [(key, value) for key, value in zip(node.value.keys, node.value.values)
                    if isinstance(key, ast.Constant) and key.value in {"status", "witness"}]
            require([key.value for key, _ in keep] == ["status", "witness"], "canonical return fields")
            node.value = ast.Dict(keys=[key for key, _ in keep], values=[value for _, value in keep])
            self.returns[self.location] += 1
            self.record("omit_measurement_return_fields", before, node)
        return self.generic_visit(node)

    def validate(self):
        expected = {key: count for key, count in REMOVALS.items() if key[0] == self.source}
        require(dict(self.removals) == expected, "measurement-removal whitelist/count mismatch")
        require(dict(self.signatures) == {key: 1 for key in SIGNATURES if key[0] == self.source},
                "counter-parameter whitelist mismatch")
        require(dict(self.calls) == {key: 1 for key in CALLS if key[0] == self.source},
                "counter-argument whitelist mismatch")
        require(dict(self.returns) == {key: 1 for key in RETURNS if key[0] == self.source},
                "measurement-result whitelist mismatch")
        require(dict(self.imports) == {key: 1 for key in IMPORTS if key[0] == self.source},
                "local helper-import whitelist mismatch")


class Renamer(ast.NodeTransformer):
    def __init__(self, mapping):
        self.mapping = mapping
        self.changed = Counter()

    def rename(self, name):
        if name in self.mapping:
            self.changed[name] += 1
            return self.mapping[name]
        return name

    def visit_Name(self, node):
        node.id = self.rename(node.id)
        return node

    def visit_ClassDef(self, node):
        node.name = self.rename(node.name)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.name = self.rename(node.name)
        return self.generic_visit(node)


def source_texts():
    return {name: (ROOT / name).read_bytes().decode("utf-8") for name in SOURCES}


def derive(texts=None):
    """Return exact derived code and its source/AST transformation record."""
    texts = source_texts() if texts is None else texts
    require(set(texts) == set(SOURCES), "exact derivation source inventory")
    body = ast.parse(
        '"""Demand kernels with measurement-only bookkeeping elided."""\n'
        "from __future__ import annotations\n"
        "from dataclasses import dataclass, field\n"
        "import proof_dag_checker as core\n"
        "import int32_circuit as signed\n"
        "from int32_circuit import build_task\n").body
    selections, changes = [], []
    for name in SOURCES:
        tree = ast.parse(texts[name], filename=name)
        selected = [node for node in tree.body
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                    and node.name in SELECTIONS[name]]
        require(tuple(node.name for node in selected) == SELECTIONS[name], "exact source definitions")
        before = ast.Module(body=copy.deepcopy(selected), type_ignores=[])
        elider = Elider(name)
        transformed = elider.visit(ast.Module(body=copy.deepcopy(selected), type_ignores=[]))
        elider.validate()
        renamer = Renamer(RENAMES[name])
        transformed = renamer.visit(transformed)
        ast.fix_missing_locations(transformed)
        changes.extend(elider.changes)
        selections.append({
            "source": name, "definitions": list(SELECTIONS[name]),
            "source_identity": identity(texts[name].encode("utf-8")),
            "selected_ast_identity": identity(normalized(before).encode()),
            "derived_ast_identity": identity(normalized(transformed).encode()),
            "renames": RENAMES[name], "rename_occurrences": dict(renamer.changed),
            "removed_statements": sum(elider.removals.values()),
        })
        body.extend(transformed.body)
    tree = ast.fix_missing_locations(ast.Module(body=body, type_ignores=[]))
    for node in ast.walk(tree):
        require(not (isinstance(node, ast.Name) and
                     node.id in {"count", "_Counter", "projection_work", "cells"}),
                "measurement variable remains in derived kernel")
        require(not (isinstance(node, ast.Attribute) and
                     node.attr in {"count", "maximum_stack_depth"}),
                "measurement attribute remains in derived kernel")
    code = ast.unparse(tree) + "\n"
    require(normalized(ast.parse(code)) == normalized(tree), "derived-source AST round trip")
    manifest = {
        "transformation": "Exact scope-specific AST removal of measurement bookkeeping",
        "source_bindings": {name: identity(texts[name].encode("utf-8")) for name in SOURCES},
        "selections": selections, "changes": changes,
        "derived_source_identity": identity(code.encode("utf-8")),
        "removed_statement_count": sum(item["removed_statements"] for item in selections),
        "canonical_return_fields": ["status", "witness"],
        "preserved": ["source admission and reconstruction", "type checks and local rules",
                      "source definedness", "support construction and projection representatives",
                      "memo keys, lookups, writes and traversal", "trace construction and canonical minimization"],
        "measurement_free_check": "No count, _Counter, projection_work, cells or maximum_stack_depth AST references remain",
    }
    return code, manifest


_KERNEL = None
_CODE = None
_MANIFEST = None
_ORIGINAL_METHODS = None


def initialize():
    global _KERNEL, _CODE, _MANIFEST, _ORIGINAL_METHODS
    if _KERNEL is None:
        _CODE, _MANIFEST = derive()
        name = "_repairseal_counter_free_derived"
        module = types.ModuleType(name)
        sys.modules[name] = module
        try:
            exec(compile(_CODE, "<counter-free-derived>", "exec"), module.__dict__)
        except BaseException:
            del sys.modules[name]
            raise
        _KERNEL = module
        _ORIGINAL_METHODS = {
            (demand._Memo, "_store"): demand._Memo._store,
            (point.PointMemo, "_store"): point.PointMemo._store,
            (point.PointMemo, "get"): point.PointMemo.get,
            (module.SupportMemo, "_store"): module.SupportMemo._store,
            (module.PointMemo, "_store"): module.PointMemo._store,
            (module.PointMemo, "get"): module.PointMemo.get,
        }
    return _KERNEL


def derivation():
    initialize()
    return _CODE, copy.deepcopy(_MANIFEST)


def hooks_restored():
    initialize()
    return all(getattr(cls, name) is function for (cls, name), function in _ORIGINAL_METHODS.items())


def evaluate_support(task):
    return initialize().evaluate_support(task)


def evaluate_point(task):
    return initialize().evaluate_point(task)


def _typed(value):
    require(type(value) in (bool, int), "exact Boolean or integer local value")
    return type(value).__name__, value


@contextmanager
def capture_stores(arm):
    """Observe the value/store sequence only during untimed preflight."""
    module = initialize()
    require(hooks_restored(), "a previous preflight hook remains active")
    classes = {
        "support": (demand._Memo, "support"),
        "support_uninstrumented": (module.SupportMemo, "support"),
        "point": (point.PointMemo, "point"),
        "point_uninstrumented": (module.PointMemo, "point"),
    }
    require(arm in classes, "a demand arm is required for value tracing")
    cls, kind = classes[arm]
    events, active = [], {}
    original_store = cls._store
    original_get = cls.get
    if kind == "support":
        def store(self, frame, value):
            result = original_store(self, frame, value)
            typ, exact = _typed(value)
            events.append([frame.node, list(frame.key), typ, exact])
            return result
        cls._store = store
    else:
        def get(self, node, point_index):
            active[id(self)] = point_index
            return original_get(self, node, point_index)

        def store(self, node, value, values):
            result = original_store(self, node, value, values)
            require(id(self) in active, "point store outside a traced input")
            typ, exact = _typed(value)
            events.append([node, active[id(self)], typ, exact])
            return result
        cls.get, cls._store = get, store
    try:
        yield events
    finally:
        cls._store = original_store
        cls.get = original_get
        require(hooks_restored(), "preflight hooks were not restored")


def trace_record(events):
    data = json.dumps(events, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return {"stored_values": len(events), "identity": identity(data)}

