"""Exact weak-order quotient for a deliberately small comparison/copy C profile.

No RepairSeal frontend, circuit, or receiver is imported. Data are symbolic
input-coordinate tokens; only guards inspect their ranks. See proof.md.
"""
from __future__ import annotations

import ast
from itertools import product
import re

from pycparser import c_ast as C, c_parser

INT_MIN = -(2**31)
INT_MAX = 2**31 - 1


class OutsideProfile(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise OutsideProfile(message)


def rank_pattern(values):
    require(bool(values) and all(type(x) is int and INT_MIN <= x <= INT_MAX for x in values),
            "nonempty int32 input")
    ranks = {value: index for index, value in enumerate(sorted(set(values)))}
    return tuple(ranks[value] for value in values)


def patterns(arity):
    require(type(arity) is int and 1 <= arity <= 4, "bounded supported arity")
    return [point for point in product(range(arity), repeat=arity)
            if set(point) == set(range(max(point) + 1))]


def embed(pattern, embedding):
    require(tuple(pattern) in patterns(len(pattern)), "canonical weak order")
    count = max(pattern) + 1
    if embedding == "ranks":
        levels = list(range(count))
    elif embedding == "int32-low":
        levels = [INT_MIN + i for i in range(count)]
    elif embedding == "int32-high":
        levels = [INT_MAX - count + 1 + i for i in range(count)]
    elif embedding == "int32-span":
        levels = [0] if count == 1 else [INT_MIN + ((INT_MAX - INT_MIN) * i // (count-1))
                                       for i in range(count)]
    else:
        raise OutsideProfile("unknown embedding")
    point = tuple(levels[i] for i in pattern)
    require(rank_pattern(point) == tuple(pattern), "embedding preserves all orders and ties")
    return point


EMBEDDINGS = ("ranks", "int32-low", "int32-high", "int32-span")


class Program:
    """Fail-closed syntax gate plus token interpreter; not a general C parser."""

    def __init__(self, raw):
        require(type(raw) is bytes and len(raw) <= 16384 and b"\x00" not in raw,
                "bounded source bytes")
        text = raw.decode("ascii")
        require(text.startswith("#include <stdio.h>\n") and "#" not in text.split("\n", 1)[1],
                "one exact stdio include; no other preprocessing")
        require("\\\n" not in text and "??" not in text and "/*" not in text and "//" not in text,
                "no preprocessing phases or comments")
        self.main = c_parser.CParser().parse(text.split("\n", 1)[1])
        require(len(self.main.ext) == 1 and isinstance(self.main.ext[0], C.FuncDef), "single main")
        main = self.main.ext[0]
        self._attributes(main.decl)
        require(main.decl.name == "main" and isinstance(main.decl.type, C.FuncDecl)
                and self._plain_type(main.decl.type.type, "int"), "unqualified int main")
        params = main.decl.type.args.params if main.decl.type.args else []
        require(len(params) == 1 and isinstance(params[0], C.Typename)
                and not params[0].quals and not params[0].align
                and self._plain_type(params[0].type, "void"), "exact main(void) signature")
        require(not main.param_decls, "no old-style declaration list")
        self.body = main.body
        self.declared = set()
        self.inputs = []
        self.sites = {}
        self._input_closed = False
        self._gate(self.body, top=True)
        require(1 <= len(self.inputs) <= 4 and len(set(self.inputs)) == len(self.inputs),
                "one initial read of each independent input")
        items = self.body.block_items or []
        require(items and isinstance(items[-1], C.Return), "one final return zero")
        self.arity = len(self.inputs)

    @staticmethod
    def _plain_type(node, spelling):
        return (isinstance(node, C.TypeDecl) and not node.quals and not node.align
                and isinstance(node.type, C.IdentifierType) and node.type.names == [spelling])

    @staticmethod
    def _attributes(node):
        require(not node.quals and not node.storage and not node.funcspec and not node.align
                and node.bitsize is None, "no ignored qualifiers, storage, alignment or bit fields")

    def _value(self, node):
        require(isinstance(node, C.ID) and node.name in self.declared,
                "values are declared input copies; arithmetic and data constants rejected")

    def _predicate(self, node):
        if isinstance(node, C.BinaryOp) and node.op in ("<", "<=", ">", ">=", "==", "!="):
            self._value(node.left); self._value(node.right)
        elif isinstance(node, C.BinaryOp) and node.op in ("&&", "||"):
            self._predicate(node.left); self._predicate(node.right)
        elif isinstance(node, C.UnaryOp) and node.op == "!":
            self._predicate(node.expr)
        else:
            raise OutsideProfile("only Boolean combinations of input-copy comparisons")

    def _gate(self, node, top=False):
        if isinstance(node, C.Compound):
            for item in node.block_items or []:
                self._gate(item, top=top and node is self.body)
        elif isinstance(node, C.Decl):
            require(top and self._plain_type(node.type, "int"), "only top-level automatic int locals")
            self._attributes(node)
            require(node.name not in self.declared | {"main", "scanf", "printf"}, "no shadowing or redefinition")
            if node.init is not None:
                self._value(node.init); self._input_closed = True
            self.declared.add(node.name)
        elif isinstance(node, C.Assignment):
            require(node.op == "=", "copy assignment only")
            self._value(node.lvalue); self._value(node.rvalue)
            self._input_closed = True
        elif isinstance(node, C.If):
            self._predicate(node.cond)
            self.sites[id(node)] = len(self.sites)
            self._input_closed = True
            self._gate(node.iftrue)
            if node.iffalse is not None:
                self._gate(node.iffalse)
        elif isinstance(node, C.FuncCall):
            require(isinstance(node.name, C.ID) and node.args, "fixed direct I/O call")
            args = node.args.exprs
            require(isinstance(args[0], C.Constant) and args[0].type == "string", "literal I/O format")
            fmt = ast.literal_eval(args[0].value)
            if node.name.name == "scanf":
                require(top and not self._input_closed and re.fullmatch(r"(?:%d)+", fmt)
                        and len(args)-1 == fmt.count("%d"), "initial complete decimal input shell")
                for arg in args[1:]:
                    require(isinstance(arg, C.UnaryOp) and arg.op == "&", "input address")
                    self._value(arg.expr)
                    self.inputs.append(arg.expr.name)
            else:
                require(node.name.name == "printf" and len(args) == 2 and fmt == "%d\n", "one exact numeric output")
                self._value(args[1]); self._input_closed = True
        elif isinstance(node, C.Return):
            require(top and isinstance(node.expr, C.Constant) and node.expr.type == "int"
                    and node.expr.value == "0", "only final literal return zero")
            require(node is (self.body.block_items or [])[-1], "no early return")
            self._input_closed = True
        elif isinstance(node, C.EmptyStatement):
            pass
        else:
            raise OutsideProfile("unsupported syntax: " + type(node).__name__)

    def evaluate(self, ranks):
        require(tuple(ranks) in patterns(self.arity), "one exact canonical order class")
        env = {}; output = []; trace = []; reads = []
        cursor = 0

        def value(node):
            require(node.name in env and env[node.name] is not None,
                    "undefined read: " + node.name)
            reads.append(node.name)
            return env[node.name]

        def predicate(node):
            if isinstance(node, C.UnaryOp):
                return not predicate(node.expr)
            if node.op == "&&":
                return predicate(node.left) and predicate(node.right)
            if node.op == "||":
                return predicate(node.left) or predicate(node.right)
            left, right = ranks[value(node.left)], ranks[value(node.right)]
            return {"<": lambda: left < right, "<=": lambda: left <= right,
                    ">": lambda: left > right, ">=": lambda: left >= right,
                    "==": lambda: left == right, "!=": lambda: left != right}[node.op]()

        def execute(node):
            nonlocal cursor
            if isinstance(node, C.Compound):
                for item in node.block_items or []: execute(item)
            elif isinstance(node, C.Decl):
                env[node.name] = value(node.init) if node.init is not None else None
            elif isinstance(node, C.Assignment):
                env[node.lvalue.name] = value(node.rvalue)
            elif isinstance(node, C.If):
                take = predicate(node.cond)
                trace.append([self.sites[id(node)], int(take)])
                branch = node.iftrue if take else node.iffalse
                if branch is not None: execute(branch)
            elif isinstance(node, C.FuncCall):
                if node.name.name == "scanf":
                    for arg in node.args.exprs[1:]:
                        env[arg.expr.name] = cursor; cursor += 1
                else:
                    output.append(value(node.args.exprs[1]))
            elif isinstance(node, (C.Return, C.EmptyStatement)):
                pass
            else:
                raise OutsideProfile("unhandled gated node")

        try:
            execute(self.body)
            require(cursor == self.arity and len(output) == 1, "one complete input/output event")
        except OutsideProfile as exc:
            return {"defined": False, "error": str(exc), "trace": trace}
        return {"defined": True, "selected_input": output[0], "output_rank": ranks[output[0]],
                "trace": trace}
