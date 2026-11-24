"""Symbolic interpretation of the separately admitted scalar int32 C profile.

The bridge owns lexical/syntactic admission and a concrete signed interpreter.
This module independently translates its admitted AST to the existing total,
typed word circuit.  Signed overflow is a source-definedness condition, not
unsigned wraparound.  The input encoding is two's complement; diagnostics use
the original signed input order.  Output observations are one canonical token,
as specified by the bridge, rather than the bytes of formatted stdout.

No arbitrary source is compiled or executed here.  This frontend is an
additional trusted component; its study checks require the bridge interpreter
and native compilers. Those finite checks are not a machine-checked C semantics
proof and do not extend the original unsigned packet schema.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from pycparser import c_ast

import proof_dag_checker as core


INT_MIN = -(1 << 31)
INT_MAX = (1 << 31) - 1
SIGN = 1 << 31
PROFILE = "repairseal-int32-point-task-v1"
EVIDENCE = "repairseal-int32-point-vectors-v1"
MAX_POINTS = 4096


@dataclass
class _State:
    env: dict[str, int]
    active: int
    defined: int
    output: int
    emitted: int

    def copy(self):
        return _State(dict(self.env), self.active, self.defined,
                      self.output, self.emitted)


class SignedCompiler:
    """Compile only an object returned by codeflaws_int32_bridge.admit_source.

    Callers must not mutate its AST. Public request entry points below perform
    fresh admission from the exact source bytes on every call.
    """

    def __init__(self, circuit, admitted, labels):
        self.c = circuit
        self.a = admitted
        self.labels = labels
        self.events = []
        self.sites = {id(node): i for i, node in enumerate(admitted.if_nodes)}
        self.input_index = 0
        self.zero = self.c.const(0)
        self.one = self.c.const(1)
        self.sign = self.c.const(SIGN)
        self.maximum = self.c.const(INT_MAX)
        self.minus_one = self.c.const(core.MASK)

    def both(self, *nodes):
        value = self.c.true
        for node in nodes:
            value = self.c.op("and", value, node)
        return value

    def truth(self, word):
        return self.c.op("!=", word, self.zero)

    def bit(self, flag):
        return self.c.op("ite", flag, self.one, self.zero)

    def negative(self, word):
        return self.c.op(">=", word, self.sign)

    def magnitude(self, word):
        return self.c.op("ite", self.negative(word),
                         self.c.op("-", self.zero, word), word)

    def less(self, left, right):
        ln, rn = self.negative(left), self.negative(right)
        return self.c.op("ite", self.c.op("!=", ln, rn), ln,
                         self.c.op("<", left, right))

    def arithmetic(self, op, left, right):
        c = self.c
        if op in {"+", "-"}:
            value = c.op(op, left, right)
            ln, rn, vn = map(self.negative, (left, right, value))
            exceptional = self.both(c.op("==" if op == "+" else "!=", ln, rn),
                                    c.op("!=", vn, ln))
            return value, c.op("not", exceptional)
        if op == "*":
            lm, rm = self.magnitude(left), self.magnitude(right)
            negative = c.op("!=", self.negative(left), self.negative(right))
            limit = c.op("ite", negative, self.sign, self.maximum)
            safe = c.op("or", c.op("==", lm, self.zero),
                        c.op("<=", rm, c.op("/", limit, lm)))
            return c.op("*", left, right), safe
        if op in {"/", "%"}:
            magnitude = c.op(op, self.magnitude(left), self.magnitude(right))
            negative = (c.op("!=", self.negative(left), self.negative(right))
                        if op == "/" else self.negative(left))
            value = c.op("ite", negative, c.op("-", self.zero, magnitude), magnitude)
            exceptional = self.both(c.op("==", left, self.sign),
                                    c.op("==", right, self.minus_one))
            return value, self.both(c.op("!=", right, self.zero),
                                    c.op("not", exceptional))
        if op in {"&", "|", "^"}:
            return c.op(op, left, right), c.true
        if op in {"==", "!="}:
            return self.bit(c.op(op, left, right)), c.true
        if op in {"<", ">", "<=", ">="}:
            flag = self.less(left, right) if op in {"<", ">="} else self.less(right, left)
            if op in {"<=", ">="}:
                flag = c.op("not", flag)
            return self.bit(flag), c.true
        raise core.Unsupported("int32 symbolic binary operator")

    def expression(self, node, env):
        c = self.c
        if isinstance(node, c_ast.ID):
            return env[node.name], c.true
        if isinstance(node, c_ast.Constant):
            # Admission has ruled out strings, nondecimal and wide literals
            # in numeric expression positions.
            if node.type != "int":
                raise core.Unsupported("int32 symbolic numeric literal")
            return c.const(int(node.value)), c.true
        if isinstance(node, c_ast.BinaryOp):
            left, ld = self.expression(node.left, env)
            right, rd = self.expression(node.right, env)
            if node.op in {"&&", "||"}:
                lt, rt = self.truth(left), self.truth(right)
                condition = c.op("ite", lt, rd, c.true) if node.op == "&&" else c.op("ite", lt, c.true, rd)
                value = self.bit(c.op("and" if node.op == "&&" else "or", lt, rt))
                return value, self.both(ld, condition)
            value, safe = self.arithmetic(node.op, left, right)
            return value, self.both(ld, rd, safe)
        if isinstance(node, c_ast.UnaryOp):
            value, defined = self.expression(node.expr, env)
            if node.op == "+":
                return value, defined
            if node.op == "-":
                return c.op("-", self.zero, value), self.both(defined, c.op("!=", value, self.sign))
            if node.op == "~":
                return c.op("inv", value), defined
            if node.op == "!":
                return self.bit(c.op("not", self.truth(value))), defined
            raise core.Unsupported("int32 symbolic unary operator")
        if isinstance(node, c_ast.TernaryOp):
            guard, gd = self.expression(node.cond, env)
            yes, yd = self.expression(node.iftrue, env)
            no, nd = self.expression(node.iffalse, env)
            truth = self.truth(guard)
            return c.op("ite", truth, yes, no), self.both(gd, c.op("ite", truth, yd, nd))
        raise core.Unsupported("int32 symbolic expression")

    def label(self, node, env):
        from codeflaws_int32_bridge import literal_string
        c = self.c
        if isinstance(node, c_ast.Constant):
            token = literal_string(node).strip()
            value = (int(token) & core.MASK if self.a.output_kind == "numeric"
                     else self.labels[token])
            return c.const(value), c.true
        if isinstance(node, c_ast.TernaryOp):
            guard, gd = self.expression(node.cond, env)
            yes, yd = self.label(node.iftrue, env)
            no, nd = self.label(node.iffalse, env)
            truth = self.truth(guard)
            return c.op("ite", truth, yes, no), self.both(gd, c.op("ite", truth, yd, nd))
        raise core.Unsupported("int32 symbolic output label")

    def check(self, state, expression_defined):
        c = self.c
        state.defined = self.both(state.defined,
                                 c.op("or", c.op("not", state.active), expression_defined))
        state.active = self.both(state.active, expression_defined)

    def assign(self, state, name, value, defined):
        self.check(state, defined)
        state.env[name] = self.c.op("ite", state.active, value, state.env[name])

    def statement(self, node, state):
        c = self.c
        if node is None or isinstance(node, c_ast.EmptyStatement):
            return state
        if isinstance(node, c_ast.Compound):
            for child in node.block_items or []:
                state = self.statement(child, state)
            return state
        if isinstance(node, c_ast.Decl):
            if node.init is not None:
                value, defined = self.expression(node.init, state.env)
                self.assign(state, node.name, value, defined)
            return state
        if isinstance(node, c_ast.Assignment):
            value, defined = self.expression(node.rvalue, state.env)
            name = node.lvalue.name
            if node.op != "=":
                value, safe = self.arithmetic(node.op[:-1], state.env[name], value)
                defined = self.both(defined, safe)
            self.assign(state, name, value, defined)
            return state
        if isinstance(node, c_ast.UnaryOp):
            name = node.expr.name
            value, safe = self.arithmetic("+" if "+" in node.op else "-",
                                          state.env[name], self.one)
            self.assign(state, name, value, safe)
            return state
        if isinstance(node, c_ast.If):
            guard, defined = self.expression(node.cond, state.env)
            self.check(state, defined)
            truth = self.truth(guard)
            self.events.append((self.sites[id(node)], state.active, truth))
            yes, no = state.copy(), state.copy()
            yes.active = self.both(state.active, truth)
            no.active = self.both(state.active, c.op("not", truth))
            yes = self.statement(node.iftrue, yes)
            no = self.statement(node.iffalse, no)
            state.env = {name: c.op("ite", truth, yes.env[name], no.env[name])
                         for name in state.env}
            state.active = c.op("or", yes.active, no.active)
            state.defined = self.both(yes.defined, no.defined)
            state.output = c.op("ite", truth, yes.output, no.output)
            state.emitted = c.op("ite", truth, yes.emitted, no.emitted)
            return state
        if isinstance(node, c_ast.Return):
            # Admission requires the literal 0; a return only stops its path.
            state.active = c.false
            return state
        if isinstance(node, c_ast.FuncCall):
            name = node.name.name
            args = node.args.exprs if node.args else []
            if name == "scanf":
                for arg in args[1:]:
                    target = arg.expr.name
                    value = c.input(self.a.input_names[self.input_index])
                    self.input_index += 1
                    self.assign(state, target, value, c.true)
                return state
            if name == "printf" and len(args) == 2:
                value, defined = self.expression(args[1], state.env)
            else:
                value, defined = self.label(args[0], state.env)
            self.check(state, defined)
            state.output = c.op("ite", state.active, value, state.output)
            state.emitted = c.op("or", state.emitted, state.active)
            return state
        raise core.Unsupported("int32 symbolic statement")

    def compile(self):
        locals_ = []

        class Names(c_ast.NodeVisitor):
            def visit_Decl(self, node):
                locals_.append(node.name)

        function = self.a.tree.ext[0]
        body = function.body
        Names().visit(body)
        parameters = function.decl.type.args.params if function.decl.type.args else []
        # Admission forbids reading main's environment before initialization.
        # Its named parameters can nevertheless be overwritten by scanf or
        # mentioned in unreachable code, which is still structurally lowered.
        locals_.extend(param.name for param in parameters if isinstance(param, c_ast.Decl))
        state = _State(dict.fromkeys(locals_, self.zero), self.c.true,
                       self.c.true, self.zero, self.c.false)
        state = self.statement(body, state)
        if self.input_index != len(self.a.input_names):
            raise core.Unsupported("int32 symbolic input arity")
        return core.Compiled(state.output, self.both(state.defined, state.emitted), self.events)


def decode(word, output_kind, labels):
    if output_kind == "numeric":
        return str(word - (1 << 32) if word >= SIGN else word)
    inverse = {value: key for key, value in labels.items()}
    if word not in inverse:
        raise core.Invalid("int32 label code")
    return inverse[word]


def evaluate_program(admitted, signed_inputs):
    """Independent DAG observation for one admitted source and input."""
    from codeflaws_int32_bridge import InvalidInput
    if type(signed_inputs) not in {tuple, list} or len(signed_inputs) != len(admitted.input_names):
        raise InvalidInput("input arity")
    if any(type(value) is not int or not INT_MIN <= value <= INT_MAX for value in signed_inputs):
        raise InvalidInput("int32 input")
    labels = {token: i for i, token in enumerate(sorted(admitted.output_labels))}
    circuit = core.Circuit()
    compiled = SignedCompiler(circuit, admitted, labels).compile()
    positions = {name: i for i, name in enumerate(admitted.input_names)}
    encoded = [value & core.MASK for value in signed_inputs]
    values = []
    for node in circuit.nodes:
        op = node[0]
        value = (node[1] if op in {"b", "u"} else encoded[positions[node[1]]]
                 if op == "input" else core.local_value(op, tuple(values[ch] for ch in node[1:])))
        values.append(value)
    defined = values[compiled.defined]
    trace = tuple((site, int(bool(values[guard]))) for site, reachable, guard in compiled.events
                  if values[reachable])
    return {"defined": defined,
            "value": decode(values[compiled.output], admitted.output_kind, labels) if defined else None,
            "trace": trace, "nodes": len(circuit.nodes)}


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"), allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError, UnicodeError) as exc:
        raise core.Invalid("int32 canonical JSON") from exc


def task_identity(task):
    return hashlib.sha256(_canonical(task)).hexdigest()


def build_task(task):
    """Reconstruct a reference-everywhere task on an exact finite point set.

    This extension compares the candidate with the supplied reference on all
    listed points. It does not infer an oracle or Cartesian-complete the tests.
    The original role is retained to make the supplied versions explicit, but
    is not a required behavior under this policy.
    """
    from codeflaws_int32_bridge import admit_source
    if type(task) is not dict or set(task) != {"kind", "id", "policy", "sources", "points"}:
        raise core.Invalid("int32 task schema")
    if task["kind"] != PROFILE or task["policy"] != "reference-everywhere":
        raise core.Invalid("int32 task profile/policy")
    if type(task["id"]) is not str or not task["id"] or len(task["id"]) > 160:
        raise core.Invalid("int32 task id")
    if type(task["sources"]) is not dict or set(task["sources"]) != set(core.ROLES):
        raise core.Invalid("int32 task sources")
    if any(type(source) is not str for source in task["sources"].values()):
        raise core.Invalid("int32 source type")
    try:
        programs = {role: admit_source(task["sources"][role].encode("utf-8"), filename=role)
                    for role in core.ROLES}
    except UnicodeError as exc:
        raise core.Invalid("int32 source UTF-8") from exc
    names = programs["candidate"].input_names
    output_kind = programs["candidate"].output_kind
    if any(program.input_names != names or program.output_kind != output_kind
           for program in programs.values()):
        raise core.Invalid("int32 incompatible program interfaces")
    points = task["points"]
    if type(points) is not list or not 1 <= len(points) <= MAX_POINTS:
        raise core.Invalid("int32 point count")
    if any(type(point) is not list or len(point) != len(names)
           or any(type(v) is not int or not INT_MIN <= v <= INT_MAX for v in point)
           for point in points):
        raise core.Invalid("int32 point schema")
    if points != sorted(points) or len(set(map(tuple, points))) != len(points):
        raise core.Invalid("int32 point order/duplicates")
    labels = {token: i for i, token in enumerate(sorted({token for p in programs.values()
                                                       for token in p.output_labels}))}
    circuit = core.Circuit()
    compiled = {role: SignedCompiler(circuit, programs[role], labels).compile() for role in core.ROLES}
    candidate, reference = compiled["candidate"], compiled["reference"]
    roots = [candidate.defined,
             circuit.op("and", candidate.defined,
                        circuit.op("and", reference.defined,
                                   circuit.op("==", candidate.output, reference.output))),
             circuit.true]
    return circuit, compiled, roots, tuple(names), output_kind, labels


def _vectors(circuit, names, points):
    positions = {name: i for i, name in enumerate(names)}
    encoded = [[value & core.MASK for value in point] for point in points]
    vectors = []
    for node in circuit.nodes:
        op = node[0]
        vector = []
        for column, point in enumerate(encoded):
            value = (node[1] if op in {"b", "u"} else point[positions[node[1]]]
                     if op == "input" else core.local_value(op, tuple(vectors[ch][column] for ch in node[1:])))
            vector.append(value)
        vectors.append(vector)
    return vectors


def _materialize(task):
    circuit, programs, roots, names, _kind, _labels = build_task(task)
    body = {"kind": EVIDENCE, "task_sha256": task_identity(task),
            "nodes": [core._expected_record(i, node, sort) for i, (node, sort)
                      in enumerate(zip(circuit.nodes, circuit.sorts))],
            "roots": roots, "events": [list(event) for event in programs["candidate"].events],
            "vectors": _vectors(circuit, names, task["points"])}
    body["sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
    result = core.classify_vectors(task["points"], roots, programs["candidate"].events, body["vectors"])
    return body, {**result, "semantic_cells": len(circuit.nodes) * len(task["points"]),
                  "nodes": len(circuit.nodes), "mode": "int32-direct-with-record"}


def make_evidence(task):
    """Materialize a packet with this compiler; not an independent frontend."""
    return _materialize(task)[0]


def evaluate_with_record(task):
    """Return a direct decision and the same complete locally generated record.

    Producing an inspectable record does not require validating an external
    vector packet. This arm deliberately materializes every node and point.
    """
    packet, result = _materialize(task)
    return result, packet


def verify_evidence(task, packet):
    """Reconstruct source, check every submitted cell, then classify."""
    circuit, programs, roots, names, _kind, _labels = build_task(task)
    fields = {"kind", "task_sha256", "nodes", "roots", "events", "vectors", "sha256"}
    if type(packet) is not dict or set(packet) != fields:
        raise core.Invalid("int32 evidence schema")
    if packet["kind"] != EVIDENCE or packet["task_sha256"] != task_identity(task):
        raise core.Invalid("int32 evidence binding")
    unhashed = {key: value for key, value in packet.items() if key != "sha256"}
    if type(packet["sha256"]) is not str or packet["sha256"] != hashlib.sha256(_canonical(unhashed)).hexdigest():
        raise core.Invalid("int32 evidence digest")
    expected = [core._expected_record(i, node, sort) for i, (node, sort)
                in enumerate(zip(circuit.nodes, circuit.sorts))]
    if not core.exact_equal(packet["nodes"], expected) or not core.exact_equal(packet["roots"], roots) or not core.exact_equal(packet["events"], [list(event) for event in programs["candidate"].events]):
        raise core.Invalid("int32 evidence topology")
    # Values used for classification are receiver-computed, never producer data.
    vectors = _vectors(circuit, names, task["points"])
    if not core.exact_equal(packet["vectors"], vectors):
        raise core.Invalid("int32 evidence local values")
    result = core.classify_vectors(task["points"], roots, programs["candidate"].events, vectors)
    return {**result, "semantic_cells": len(circuit.nodes) * len(task["points"]),
            "nodes": len(circuit.nodes), "mode": "int32-full"}


def evaluate_direct(task):
    """Support-keyed, demand-driven decision on an exact finite point set.

    A projected class retains its least actual signed input, rather than
    filling omitted axes independently. This matters for correlated tests.
    """
    from demand_evaluator import _Counter, _Memo, _supports
    circuit, programs, roots, names, _kind, _labels = build_task(task)
    points = task["points"]
    encoded = [tuple(value & core.MASK for value in point) for point in points]
    count = _Counter(None)
    projection_work = {"points_scanned": 0, "key_coordinates": 0,
                       "unique_representatives": 0, "projection_queries": 0,
                       "encoded_coordinates": len(points) * len(names)}
    supports = _supports(circuit, names, count)
    memo = _Memo(circuit, supports, count)
    events = programs["candidate"].events

    def representatives(support):
        chosen = {}
        projection_work["projection_queries"] += 1
        # points are in signed order, so the first representative is minimal.
        for i, point in enumerate(encoded):
            projection_work["points_scanned"] += 1
            projection_work["key_coordinates"] += len(support)
            key = tuple(point[j] for j in support)
            chosen.setdefault(key, i)
        projection_work["unique_representatives"] += len(chosen)
        return list(chosen.values())

    witness = None
    for obligation, root in zip(core.OBLIGATIONS, roots):
        failed = False
        for i in representatives(supports[root]):
            count.add("root_predicate_tests")
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
            count.add("diagnostic_points")
            if memo.get(root, encoded[i]):
                continue
            trace = []
            for site, reachable, guard in events:
                count.add("trace_events_examined")
                if memo.get(reachable, encoded[i]):
                    trace.append([site, int(bool(memo.get(guard, encoded[i])))])
            key = (trace, points[i])
            if best is None or key < best:
                best = key
        if best is None:
            raise RuntimeError("int32 diagnostic existence")
        witness = {"obligation": obligation, "trace": best[0], "input": best[1]}
        break
    return {"status": "REFUTED" if witness else "ACCEPT", "witness": witness,
            "semantic_cells": count.values["semantic_cells"], "counters": count.values,
            "projection_work": projection_work,
            "counter_scope": "local DAG values, named memo/support work, and point-set projection operations; source admission, allocation, and elapsed time excluded",
            "nodes": len(circuit.nodes), "mode": "int32-demand"}
