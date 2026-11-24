"""A closed signed-C frontend and concrete interpreter for finite observations.

The source bytes are never rewritten for native execution. Admission checks the
entire translation unit, including unreachable code, before an AST may be used.
The observation is one canonical decimal or literal token, not arbitrary stdout.
This module is independent of the RepairSeal circuit, producer and checker.
"""
from __future__ import annotations

import ast as python_ast
from collections import Counter
from dataclasses import dataclass
import hashlib
import re
from typing import Any

from pycparser import c_ast, c_parser

PROFILE_ID = "codeflaws-closed-int32-v1"
INT_MIN, INT_MAX = -(2**31), 2**31 - 1
MAX_SOURCE_BYTES = 65536
MAX_AST_NODES = 4096
MAX_INPUTS = 16
MAX_STEPS = 16384
MAX_FLOW_STATES = 1024
HEADERS = frozenset({"stdio", "stdlib", "string", "math", "ctype"})
# Header directives are removed only for parsing; the native source keeps them.
# Do not let a local declaration or main parameter hide an object-like macro
# from the AST.  Function-like macro names are excluded too: this is a closed
# source profile, not a substitute C preprocessor.  Implementation macros and
# compiler predefined names are covered by the leading-underscore exclusion.
HEADER_MACROS = {
    "stdio": frozenset({"BUFSIZ", "EOF", "FILENAME_MAX", "FOPEN_MAX", "L_tmpnam",
                        "NULL", "SEEK_CUR", "SEEK_END", "SEEK_SET", "TMP_MAX",
                        "stdin", "stdout", "stderr"}),
    "stdlib": frozenset({"EXIT_FAILURE", "EXIT_SUCCESS", "MB_CUR_MAX", "NULL", "RAND_MAX"}),
    "string": frozenset({"NULL"}),
    "math": frozenset({"FP_FAST_FMA", "FP_FAST_FMAF", "FP_FAST_FMAL", "FP_ILOGB0",
                       "FP_ILOGBNAN", "FP_INFINITE", "FP_NAN", "FP_NORMAL",
                       "FP_SUBNORMAL", "FP_ZERO", "HUGE_VAL", "HUGE_VALF", "HUGE_VALL",
                       "INFINITY", "MATH_ERREXCEPT", "MATH_ERRNO", "NAN",
                       "fpclassify", "isfinite", "isgreater", "isgreaterequal", "isinf",
                       "isless", "islessequal", "islessgreater", "isnan", "isnormal",
                       "isunordered", "math_errhandling", "signbit"}),
    "ctype": frozenset({"isalnum", "isalpha", "isblank", "iscntrl", "isdigit",
                        "isgraph", "islower", "isprint", "ispunct", "isspace",
                        "isupper", "isxdigit", "tolower", "toupper"}),
}
CALLS = frozenset({"scanf", "printf", "puts"})
BINARY_OPS = frozenset({"+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=", "&&", "||", "&", "|", "^"})
UNARY_OPS = frozenset({"+", "-", "!", "~"})
ASSIGNMENT_OPS = frozenset({"=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="})
INCREMENTS = frozenset({"++", "--", "p++", "p--"})
INTEGER_LITERAL = re.compile(r"(?:0|[1-9][0-9]*)\Z")
DECIMAL_TOKEN = re.compile(r"[+-]?[0-9]+\Z")
SCALAR_PRINTF = re.compile(r"\s*%d\s*\Z", re.ASCII)
SCALAR_SCANF = re.compile(r"\s*%d(?:\s*%d)*\s*\Z", re.ASCII)
COMMENT_OR_STRING = re.compile(r'''("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(/\*.*?\*/|//[^\r\n]*)''', re.S)


class UnsupportedSource(ValueError):
    def __init__(self, code: str, detail: str = ""):
        self.code, self.detail = code, detail
        super().__init__(code + (": " + detail if detail else ""))


class InvalidInput(ValueError):
    pass


def require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise UnsupportedSource(code, detail)


def _ordered_flow_states(states: set[tuple[frozenset[str], int]]) -> list[tuple[frozenset[str], int]]:
    """Keep the state set unchanged while fixing which rejection is reported first."""
    return sorted(states, key=lambda state: (tuple(sorted(state[0])), state[1]))


def line_of(node: c_ast.Node | None) -> int | None:
    return node.coord.line if node is not None and node.coord is not None else None


def literal_string(node: c_ast.Node) -> str:
    require(isinstance(node, c_ast.Constant) and node.type == "string", "nonliteral-string")
    require(re.search(r'\\(?![\\"nrt])', node.value) is None, "unsupported-string-escape")
    try:
        value = python_ast.literal_eval(node.value)
    except (ValueError, SyntaxError, TypeError, RecursionError) as exc:
        raise UnsupportedSource("string-literal", str(exc)) from exc
    require(type(value) is str and value.isascii(), "non-ascii-string")
    require("\0" not in value and all(c in "\n\r\t" or 32 <= ord(c) <= 126 for c in value), "string-control-character")
    return value


def canonical_output(raw: bytes | str, output_kind: str) -> str:
    """Decode exactly one token; never silently equate 04, +4, -0 and 4/0."""
    if isinstance(raw, bytes):
        try:
            text = raw.decode("ascii")
        except UnicodeError as exc:
            raise InvalidInput("non-ASCII output") from exc
    elif type(raw) is str:
        text = raw
    else:
        raise InvalidInput("output must be bytes or text")
    if not text.isascii() or len(text) > 1024 or len(text.split()) != 1:
        raise InvalidInput("output is not one bounded ASCII token")
    token = text.strip()
    if any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise InvalidInput("nonprinting output token")
    if output_kind == "numeric":
        if DECIMAL_TOKEN.fullmatch(token) is None or len(token) > 11:
            raise InvalidInput("nonnumeric output token")
        value = int(token)
        if not INT_MIN <= value <= INT_MAX or str(value) != token:
            raise InvalidInput("noncanonical or out-of-range decimal output")
    elif output_kind != "label":
        raise InvalidInput("unknown output codec")
    return token


def parse_input(raw: bytes, arity: int) -> tuple[int, ...]:
    if type(raw) is not bytes or not 0 < len(raw) <= 4096 or not 1 <= arity <= MAX_INPUTS:
        raise InvalidInput("input size or arity")
    try:
        text = raw.decode("ascii")
    except UnicodeError as exc:
        raise InvalidInput("non-ASCII input") from exc
    if re.fullmatch(r"[ \t\r\n\v\f]*[+-]?[0-9]+(?:[ \t\r\n\v\f]+[+-]?[0-9]+)*[ \t\r\n\v\f]*", text) is None:
        raise InvalidInput("unsupported input token separation")
    tokens = text.split()
    if len(tokens) != arity or any(DECIMAL_TOKEN.fullmatch(t) is None for t in tokens):
        raise InvalidInput("input is not exactly the declared decimal vector")
    if any(len(t) > 64 for t in tokens):
        raise InvalidInput("decimal input token limit")
    values = tuple(int(t) for t in tokens)
    if any(not INT_MIN <= v <= INT_MAX for v in values):
        raise InvalidInput("scanf conversion outside int32")
    return values


@dataclass(frozen=True)
class AdmittedSource:
    tree: c_ast.FileAST
    source_sha256: str
    raw: bytes
    input_names: tuple[str, ...]
    input_targets: tuple[str, ...]
    output_kind: str
    output_labels: tuple[str, ...]
    if_nodes: tuple[c_ast.If, ...]
    input_calls: tuple[c_ast.FuncCall, ...]
    headers: tuple[str, ...]
    ast_nodes: int
    profile_id: str = PROFILE_ID

    @property
    def input_arity(self) -> int:
        return len(self.input_names)


@dataclass(frozen=True)
class Evaluation:
    defined: bool
    value: str | None
    trace: tuple[tuple[int, int], ...]
    undefined_reason: str | None
    undefined_line: int | None
    counters: dict[str, int]
    steps: int

    def as_dict(self) -> dict[str, Any]:
        return {"defined": self.defined, "value": self.value,
                "trace": [list(t) for t in self.trace],
                "undefined_reason": self.undefined_reason,
                "undefined_line": self.undefined_line,
                "counters": self.counters, "steps": self.steps}


def _prepare(raw: bytes) -> tuple[str, tuple[str, ...]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES, "source-size")
    require(b"\0" not in raw, "source-nul")
    # C performs line splicing and trigraph replacement before comment removal.
    # Reject them rather than pretending Python's physical lines are C tokens.
    require(re.search(rb"\\(?:\r\n|\r|\n)", raw) is None, "line-splicing")
    require(b"??" not in raw, "trigraph")
    require(b"\r" not in raw.replace(b"\r\n", b""), "bare-carriage-return")
    try:
        source = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise UnsupportedSource("source-encoding") from exc
    # Preserve source line numbers and prevent token concatenation across comments.
    source = COMMENT_OR_STRING.sub(lambda m: m[1] if m[1] else "".join("\n" if c == "\n" else " " for c in m[2]), source)
    require(all(c in "\t\r\n" or 32 <= ord(c) <= 126 for c in source), "source-character-profile")
    headers: list[str] = []
    lines: list[str] = []
    for physical in source.splitlines(keepends=True):
        if physical.lstrip().startswith("#"):
            matched = re.fullmatch(r"[ \t]*#[ \t]*include[ \t]*<([a-z]+)\.h>[ \t]*(?:\r?\n)?", physical)
            require(matched is not None and matched[1] in HEADERS, "preprocessing-directive")
            require(not "".join(lines).strip(), "header-after-source-token")
            headers.append(matched[1]); lines.append("\n" if physical.endswith("\n") else "")
        else:
            lines.append(physical)
    require("stdio" in headers, "missing-stdio-declaration")
    return "".join(lines), tuple(headers)


def _is_int(decl: c_ast.Decl) -> bool:
    return (isinstance(decl, c_ast.Decl) and not decl.quals and not decl.storage and not decl.funcspec
            and isinstance(decl.type, c_ast.TypeDecl) and not decl.type.quals
            and isinstance(decl.type.type, c_ast.IdentifierType) and decl.type.type.names == ["int"])


def _argv_type(decl: c_ast.Decl) -> bool:
    if not isinstance(decl, c_ast.Decl) or decl.quals or decl.storage or decl.funcspec:
        return False
    ty = decl.type
    if isinstance(ty, c_ast.ArrayDecl):
        if ty.dim is not None or ty.dim_quals:
            return False
        ty = ty.type
    elif isinstance(ty, c_ast.PtrDecl) and not ty.quals:
        ty = ty.type
    else:
        return False
    return (isinstance(ty, c_ast.PtrDecl) and not ty.quals
            and isinstance(ty.type, c_ast.TypeDecl) and not ty.type.quals
            and isinstance(ty.type.type, c_ast.IdentifierType) and ty.type.type.names == ["char"])


class _Admission:
    def __init__(self, tree: c_ast.FileAST, headers: tuple[str, ...]):
        self.tree = tree
        self.header_macros = frozenset().union(*(HEADER_MACROS[h] for h in headers))
        self.names: set[str] = set()
        self.input_targets: list[str] = []
        self.input_calls: list[c_ast.FuncCall] = []
        self.if_nodes: list[c_ast.If] = []
        self.output_forms: set[str] = set()
        self.output_labels: set[str] = set()
        self.input_closed = False
        self.node_count = 0

    def _count(self, node: c_ast.Node) -> None:
        self.node_count += 1
        require(self.node_count <= MAX_AST_NODES, "ast-size")
        for _name, child in node.children():
            self._count(child)

    def _expression(self, node: c_ast.Node, visible: set[str], *, strings: bool = False) -> None:
        if isinstance(node, c_ast.Constant):
            if strings:
                require(node.type == "string", "nonliteral-output-label")
                value = literal_string(node)
                require("%" not in value, "literal-percent-output")
                try:
                    token = canonical_output(value, "label")
                except InvalidInput as exc:
                    raise UnsupportedSource("output-label", str(exc)) from exc
                self.output_labels.add(token)
                return
            require(node.type == "int" and INTEGER_LITERAL.fullmatch(node.value) is not None, "integer-literal")
            require(len(node.value) <= 10 and 0 <= int(node.value) <= INT_MAX, "integer-literal-range")
            return
        if isinstance(node, c_ast.ID):
            require(not strings and node.name in visible, "lexical-identifier", node.name)
            return
        if isinstance(node, c_ast.TernaryOp):
            self._expression(node.cond, visible)
            self._expression(node.iftrue, visible, strings=strings)
            self._expression(node.iffalse, visible, strings=strings)
            return
        require(not strings, "nonliteral-output-label")
        if isinstance(node, c_ast.BinaryOp):
            require(node.op in BINARY_OPS, "binary-operator", node.op)
            self._expression(node.left, visible); self._expression(node.right, visible)
            return
        if isinstance(node, c_ast.UnaryOp):
            require(node.op in UNARY_OPS, "unary-expression", node.op)
            self._expression(node.expr, visible)
            return
        raise UnsupportedSource("expression-node", type(node).__name__)

    def _source_identifier(self, name: str) -> None:
        require(not name.startswith("_"), "reserved-identifier", name)
        require(name not in self.header_macros, "header-macro-identifier", name)

    def _declaration(self, node: c_ast.Decl, visible: set[str]) -> None:
        require(_is_int(node), "non-int32-local")
        require(node.name not in self.names and node.name not in CALLS and node.name != "main", "shadowed-or-reserved-local")
        self._source_identifier(node.name)
        self.names.add(node.name)
        if node.init is not None:
            self._expression(node.init, visible)
        visible.add(node.name)

    def _call(self, node: c_ast.FuncCall, visible: set[str], at_root: bool) -> None:
        require(isinstance(node.name, c_ast.ID) and node.name.name in CALLS, "unapproved-call")
        name = node.name.name
        args = node.args.exprs if isinstance(node.args, c_ast.ExprList) else []
        if name == "scanf":
            require(at_root and not self.input_closed, "scanf-not-unconditional-prelude")
            require(len(args) >= 2, "scanf-arity")
            fmt = literal_string(args[0])
            require(len(fmt) <= 256, "scanf-format-length")
            require(SCALAR_SCANF.fullmatch(fmt) is not None, "scanf-format")
            require(fmt.count("%d") == len(args) - 1, "scanf-format-arity")
            for arg in args[1:]:
                require(isinstance(arg, c_ast.UnaryOp) and arg.op == "&" and isinstance(arg.expr, c_ast.ID), "scanf-target")
                require(arg.expr.name in visible, "scanf-undeclared-target")
                self.input_targets.append(arg.expr.name)
            require(len(self.input_targets) <= MAX_INPUTS, "input-arity-limit")
            self.input_calls.append(node)
            return
        self.input_closed = True
        if name == "printf":
            require(bool(args), "printf-arity")
            fmt = literal_string(args[0])
            require(len(fmt) <= 1024, "printf-format-length")
            if SCALAR_PRINTF.fullmatch(fmt):
                require(len(args) == 2, "printf-format-arity")
                self._expression(args[1], visible); self.output_forms.add("numeric")
            else:
                require(len(args) == 1, "printf-nonscalar-format")
                self._expression(args[0], visible, strings=True); self.output_forms.add("label")
        else:
            require(len(args) == 1, "puts-arity")
            self._expression(args[0], visible, strings=True); self.output_forms.add("label")

    def _shape(self, node: c_ast.Node | None, visible: set[str], *, at_root: bool = False) -> None:
        if node is None or isinstance(node, c_ast.EmptyStatement):
            return
        if isinstance(node, c_ast.Compound):
            local = set(visible)
            for child in node.block_items or []:
                self._shape(child, local)
            return
        if isinstance(node, c_ast.Decl):
            self._declaration(node, visible); return
        if isinstance(node, c_ast.Assignment):
            require(isinstance(node.lvalue, c_ast.ID) and node.lvalue.name in visible, "assignment-target")
            require(node.op in ASSIGNMENT_OPS, "assignment-operator")
            self._expression(node.rvalue, visible); return
        if isinstance(node, c_ast.UnaryOp):
            require(node.op in INCREMENTS and isinstance(node.expr, c_ast.ID) and node.expr.name in visible, "standalone-unary")
            return
        if isinstance(node, c_ast.FuncCall):
            self._call(node, visible, at_root); return
        if isinstance(node, c_ast.If):
            self.input_closed = True; self.if_nodes.append(node)
            self._expression(node.cond, visible)
            self._shape(node.iftrue, set(visible)); self._shape(node.iffalse, set(visible))
            return
        if isinstance(node, c_ast.Return):
            self.input_closed = True
            require(isinstance(node.expr, c_ast.Constant) and node.expr.type == "int" and node.expr.value == "0", "main-return-not-zero")
            return
        raise UnsupportedSource("statement-node", type(node).__name__)

    def _read(self, node: c_ast.Node | None, initialized: frozenset[str]) -> None:
        if node is None:
            return
        if isinstance(node, c_ast.ID):
            require(node.name in initialized, "uninitialized-read", node.name)
        else:
            for _name, child in node.children():
                self._read(child, initialized)

    def _flow(self, node: c_ast.Node | None, states: set[tuple[frozenset[str], int]]) -> tuple[set, set]:
        if not states or node is None or isinstance(node, c_ast.EmptyStatement):
            return states, set()
        require(len(states) <= MAX_FLOW_STATES, "control-flow-state-limit")
        if isinstance(node, c_ast.Compound):
            live, done = states, set()
            locals_here = {n.name for n in node.block_items or [] if isinstance(n, c_ast.Decl)}
            for child in node.block_items or []:
                live, terminated = self._flow(child, live); done |= terminated
            return ({(i - locals_here, c) for i, c in live}, {(i - locals_here, c) for i, c in done})
        live, done = set(), set()
        for initialized, outputs in _ordered_flow_states(states):
            if isinstance(node, c_ast.Decl):
                if node.init is not None:
                    self._read(node.init, initialized); initialized = initialized | {node.name}
            elif isinstance(node, c_ast.Assignment):
                if node.op != "=":
                    self._read(node.lvalue, initialized)
                self._read(node.rvalue, initialized); initialized = initialized | {node.lvalue.name}
            elif isinstance(node, c_ast.UnaryOp):
                self._read(node.expr, initialized)
            elif isinstance(node, c_ast.FuncCall):
                args = node.args.exprs
                if node.name.name == "scanf":
                    initialized = initialized | {a.expr.name for a in args[1:]}
                else:
                    for arg in args:
                        self._read(arg, initialized)
                    outputs = min(2, outputs + 1)
            elif isinstance(node, c_ast.If):
                self._read(node.cond, initialized)
                state = {(initialized, outputs)}
                a, b = self._flow(node.iftrue, state); c, d = self._flow(node.iffalse, state)
                live |= a | c; done |= b | d
                continue
            elif isinstance(node, c_ast.Return):
                done.add((initialized, outputs)); continue
            else:
                raise AssertionError("shape pass and flow pass disagree")
            live.add((initialized, outputs))
        return live, done

    def run(self) -> str:
        self._count(self.tree)
        require(len(self.tree.ext) == 1 and isinstance(self.tree.ext[0], c_ast.FuncDef), "single-main-only")
        fn = self.tree.ext[0]
        require(fn.decl.name == "main" and not fn.decl.storage and not fn.decl.quals and not fn.decl.funcspec, "main-signature")
        require(isinstance(fn.decl.type, c_ast.FuncDecl), "main-signature")
        rt = fn.decl.type.type
        require(isinstance(rt, c_ast.TypeDecl) and not rt.quals and isinstance(rt.type, c_ast.IdentifierType) and rt.type.names == ["int"], "main-return-type")
        params = fn.decl.type.args.params if fn.decl.type.args else []
        visible: set[str] = set()
        if len(params) == 2:
            require(_is_int(params[0]) and _argv_type(params[1]), "main-parameters")
            require(params[0].name is not None and params[1].name is not None and params[0].name != params[1].name, "main-parameter-names")
            require(params[0].name not in CALLS and params[1].name not in CALLS, "reserved-parameter")
            self._source_identifier(params[0].name)
            self._source_identifier(params[1].name)
            visible.add(params[0].name); self.names.add(params[0].name); self.names.add(params[1].name)
        elif params:
            require(len(params) == 1 and isinstance(params[0], c_ast.Typename)
                    and isinstance(params[0].type, c_ast.TypeDecl)
                    and isinstance(params[0].type.type, c_ast.IdentifierType)
                    and params[0].type.type.names == ["void"], "main-parameters")
        require(fn.param_decls is None, "old-style-parameters")
        # Structural/lexical validation deliberately visits statements after return.
        for child in fn.body.block_items or []:
            self._shape(child, visible, at_root=True)
        require(bool(self.input_targets), "missing-scalar-input")
        live, done = self._flow(fn.body, {(frozenset(), 0)})
        require({count for _init, count in live | done} == {1}, "not-one-output-on-every-path")
        numeric_labels = all(DECIMAL_TOKEN.fullmatch(s) for s in self.output_labels)
        if numeric_labels:
            for token in sorted(self.output_labels):
                try:
                    canonical_output(token, "numeric")
                except InvalidInput as exc:
                    raise UnsupportedSource("numeric-literal-output", str(exc)) from exc
        require(self.output_forms != {"numeric", "label"} or numeric_labels, "mixed-numeric-label-output")
        return "numeric" if self.output_forms == {"numeric"} or numeric_labels else "label"


def admit_source(raw: bytes, filename: str = "<source>") -> AdmittedSource:
    text, headers = _prepare(raw)
    try:
        tree = c_parser.CParser().parse(text, filename=filename)
    except Exception as exc:
        raise UnsupportedSource("parse", str(exc)) from exc
    admission = _Admission(tree, headers)
    try:
        kind = admission.run()
    except RecursionError as exc:
        raise UnsupportedSource("ast-depth") from exc
    return AdmittedSource(tree, hashlib.sha256(raw).hexdigest(), raw,
                          tuple("i" + str(i) for i in range(len(admission.input_targets))),
                          tuple(admission.input_targets), kind, tuple(sorted(admission.output_labels)),
                          tuple(admission.if_nodes), tuple(admission.input_calls), headers, admission.node_count)


class _Undefined(Exception):
    def __init__(self, reason: str, node: c_ast.Node | None):
        self.reason, self.line = reason, line_of(node)


class _Returned(Exception):
    pass


class _Interpreter:
    def __init__(self, admitted: AdmittedSource, values: tuple[int, ...]):
        self.source, self.inputs, self.input_index = admitted, values, 0
        self.env: dict[str, int] = {}
        self.output: list[str] = []
        self.trace: list[tuple[int, int]] = []
        self.if_ids = {id(node): i for i, node in enumerate(admitted.if_nodes)}
        self.counters: Counter[str] = Counter()
        self.steps = 0

    def tick(self, node: c_ast.Node | None, kind: str) -> None:
        self.steps += 1; self.counters[kind] += 1
        if self.steps > MAX_STEPS:
            raise _Undefined("step-limit", node)

    def checked(self, value: int, node: c_ast.Node) -> int:
        if not INT_MIN <= value <= INT_MAX:
            raise _Undefined("signed-overflow", node)
        return value

    def arithmetic(self, op: str, a: int, b: int, node: c_ast.Node) -> int:
        self.counters["operator:" + op] += 1
        if op == "+": return self.checked(a + b, node)
        if op == "-": return self.checked(a - b, node)
        if op == "*": return self.checked(a * b, node)
        if op in {"/", "%"}:
            if b == 0: raise _Undefined("division-by-zero", node)
            if a == INT_MIN and b == -1: raise _Undefined("signed-div-overflow", node)
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0): q = -q
            return q if op == "/" else a - q * b
        if op == "<": return int(a < b)
        if op == "<=": return int(a <= b)
        if op == ">": return int(a > b)
        if op == ">=": return int(a >= b)
        if op == "==": return int(a == b)
        if op == "!=": return int(a != b)
        if op == "&": return self.checked(a & b, node)
        if op == "|": return self.checked(a | b, node)
        if op == "^": return self.checked(a ^ b, node)
        raise AssertionError("unadmitted arithmetic operator")

    def expression(self, node: c_ast.Node) -> int | str:
        self.tick(node, "expression")
        if isinstance(node, c_ast.ID):
            if node.name not in self.env: raise _Undefined("uninitialized-read", node)
            return self.env[node.name]
        if isinstance(node, c_ast.Constant):
            return literal_string(node) if node.type == "string" else int(node.value)
        if isinstance(node, c_ast.BinaryOp):
            a = self.expression(node.left)
            if node.op == "&&":
                self.counters["operator:&&"] += 1
                return int(bool(a) and bool(self.expression(node.right)))
            if node.op == "||":
                self.counters["operator:||"] += 1
                return int(bool(a) or bool(self.expression(node.right)))
            return self.arithmetic(node.op, a, self.expression(node.right), node)
        if isinstance(node, c_ast.UnaryOp):
            a = self.expression(node.expr); self.counters["unary:" + node.op] += 1
            if node.op == "+": return a
            if node.op == "-": return self.checked(-a, node)
            if node.op == "!": return int(not a)
            if node.op == "~": return self.checked(~a, node)
        if isinstance(node, c_ast.TernaryOp):
            self.counters["conditional-expression"] += 1
            return self.expression(node.iftrue if self.expression(node.cond) else node.iffalse)
        raise AssertionError("unadmitted expression")

    def statement(self, node: c_ast.Node | None) -> None:
        self.tick(node, "statement")
        if node is None or isinstance(node, c_ast.EmptyStatement): return
        if isinstance(node, c_ast.Compound):
            for child in node.block_items or []: self.statement(child)
            return
        if isinstance(node, c_ast.Decl):
            if node.init is not None: self.env[node.name] = self.expression(node.init)
            return
        if isinstance(node, c_ast.Assignment):
            value = self.expression(node.rvalue); name = node.lvalue.name
            self.env[name] = value if node.op == "=" else self.arithmetic(node.op[:-1], self.env[name], value, node)
            return
        if isinstance(node, c_ast.UnaryOp):
            name = node.expr.name
            self.env[name] = self.arithmetic("+" if "+" in node.op else "-", self.env[name], 1, node)
            return
        if isinstance(node, c_ast.If):
            taken = bool(self.expression(node.cond)); self.trace.append((self.if_ids[id(node)], int(taken)))
            self.statement(node.iftrue if taken else node.iffalse); return
        if isinstance(node, c_ast.Return): raise _Returned()
        if isinstance(node, c_ast.FuncCall):
            name, args = node.name.name, node.args.exprs
            self.counters["call:" + name] += 1
            if name == "scanf":
                for arg in args[1:]:
                    self.env[arg.expr.name] = self.inputs[self.input_index]; self.input_index += 1
            elif name == "printf":
                fmt = literal_string(args[0])
                self.output.append(fmt % self.expression(args[1]) if len(args) == 2 else fmt)
            else:
                self.output.append(self.expression(args[0]) + "\n")
            return
        raise AssertionError("unadmitted statement")

    def run(self) -> Evaluation:
        value = None; reason = None; line = None
        try:
            try:
                self.statement(self.source.tree.ext[0].body)
            except _Returned:
                pass
            if self.input_index != len(self.inputs) or len(self.output) != 1:
                raise AssertionError("admission/interpreter IO disagreement")
            value = canonical_output("".join(self.output), self.source.output_kind)
        except _Undefined as exc:
            reason, line = exc.reason, exc.line
        return Evaluation(reason is None, value, tuple(self.trace), reason, line, dict(self.counters), self.steps)


def evaluate(admitted: AdmittedSource, inputs: tuple[int, ...] | list[int]) -> Evaluation:
    if not isinstance(admitted, AdmittedSource) or admitted.profile_id != PROFILE_ID:
        raise InvalidInput("an admitted source for the current profile is required")
    if not isinstance(inputs, (tuple, list)) or len(inputs) != admitted.input_arity:
        raise InvalidInput("input arity")
    if any(type(v) is not int or not INT_MIN <= v <= INT_MAX for v in inputs):
        raise InvalidInput("input outside signed int32")
    return _Interpreter(admitted, tuple(inputs)).run()
