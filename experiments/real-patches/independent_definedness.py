#!/usr/bin/env python3
"""A separate path executor for the nine retained uninitialized-read witnesses.

Only the explicitly reviewed source hashes and a small expression grammar are
accepted. This checker does not import scalar_semantics, patch_study or verify.
It records declarations, actual assignments, each taken branch, and the first
read of an automatic int with no preceding initialization. It checks that the
faulting object's address is never taken. Its scope is these supplied witnesses,
not independent complete-domain classification of all patches.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

from pycparser import c_ast as C, c_generator, c_parser

HERE = Path(__file__).resolve().parent
SOURCES = {
    "apr-005": "5a2f8e67f1b60bd16a43bc9dd8956dcb39fe8d7a2c96ee88c2edfbaecbcee3a3",
    "apr-007": "08fd1d32d869394b0d082cbf18d7e36a8b05c1f532969d9ead5802ab26f4f779",
    "apr-008": "0efe8663150b43de881b73532fe6365f1fc7aa0e8eb2ded26bab1a80d4cad257",
    "apr-095": "1a0a3e9b93ca0226f45628a512955ed6ac7743748109fa8d5d4396cba4a059ee",
    "apr-096": "59ab1b0671ab7c774cae0f4300bd173c442af441ccf7883ea4b1c3a07e7fcc81",
    "apr-097": "1d7987767fc686039c8c4b94b6538a449b15c0dcc19b830ff64a45e83023d85b",
    "apr-098": "5d12da92a0db0b194f9ef22aaf35d6be3cf70162546abc685051125445ee8c2f",
    "apr-121": "36f4103ba2e15a1c573ec25e99e2053f4232c4bb5309136353b3d17aacf703f6",
    "apr-122": "8fc104acaa96c050ee0c04bf6a741da3bd0463542415dc1814887f5f5485b4ab",
}
COMMENTS = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(/\*.*?\*/|//[^\r\n]*)', re.S)
MACRO = re.compile(r'\bANGELIX_OUTPUT\s*\(\s*int\s*,\s*((?:\(int\)\s*)?[A-Za-z_][A-Za-z_0-9]*)\s*,\s*"stdout"\s*\)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def parse(raw):
    text = raw.decode("ascii")
    text = COMMENTS.sub(lambda match: match[1] if match[1] else
                        "".join("\n" if char == "\n" else " " for char in match[2]), text)
    # Keep original line positions for the executable path explanation.
    text = "\n".join("" if line.lstrip().startswith("#") else line for line in text.splitlines())
    text = MACRO.sub(lambda match: match[1], text)
    require("ANGELIX_OUTPUT" not in text, "unreviewed identity macro use")
    tree = c_parser.CParser().parse(text)
    require(len(tree.ext) == 1 and isinstance(tree.ext[0], C.FuncDef) and
            tree.ext[0].decl.name == "main", "one main body")
    return tree.ext[0].body


class Uninitialized(Exception):
    def __init__(self, name, line):
        self.name, self.line = name, line


class Returned(Exception):
    pass


def execute_witness(raw, point):
    """Execute only the supported int/branch fragment, failing closed otherwise."""
    require(type(point) is list and all(type(value) is int and -(2**31) <= value < 2**31
                                       for value in point), "int32 witness input")
    body = parse(raw)
    declarations = {}
    addresses = set()
    allowed_ops = {"<", "<=", ">", ">=", "==", "!=", "&&", "||", "+"}
    def integer_type(node):
        while isinstance(node, (C.Typename, C.TypeDecl)):
            node = node.type
        return isinstance(node, C.IdentifierType) and node.names == ["int"]
    def audit(node):
        if node is None:
            return
        if isinstance(node, C.Decl):
            require(integer_type(node.type) and not node.quals and not node.storage,
                    "only automatic int objects")
            require(node.name not in declarations, "no shadowed objects")
            declarations[node.name] = {"line": node.coord.line, "initializer_present": node.init is not None}
        elif isinstance(node, C.Assignment):
            require(node.op == "=" and isinstance(node.lvalue, C.ID), "only simple assignments")
        elif isinstance(node, C.BinaryOp):
            require(node.op in allowed_ops, "unsupported witness operator")
        elif isinstance(node, C.UnaryOp):
            if node.op == "&" and isinstance(node.expr, C.ID):
                addresses.add(node.expr.name)
            require(node.op in {"!", "+", "-"}, "unsupported witness unary operator")
        elif isinstance(node, C.Cast):
            require(integer_type(node.to_type), "identity int cast only")
        elif isinstance(node, C.FuncCall):
            require(isinstance(node.name, C.ID) and node.name.name in {"atoi", "printf"}, "closed external calls")
        elif isinstance(node, (C.For, C.While, C.DoWhile, C.Switch, C.Goto, C.Label)):
            raise ValueError("unreviewed control flow")
        for _, child in node.children():
            audit(child)
    audit(body)
    env = {}
    assignments = []
    branches = []
    generator = c_generator.CGenerator()
    def expr(node):
        if isinstance(node, C.ID):
            require(node.name in declarations, "undeclared object")
            if node.name not in env:
                raise Uninitialized(node.name, node.coord.line)
            return env[node.name]
        if isinstance(node, C.Constant):
            require(node.type == "int" and re.fullmatch(r"0|[1-9][0-9]*", node.value), "simple int literal")
            value = int(node.value)
            require(value < 2**31, "literal range")
            return value
        if isinstance(node, C.Cast):
            return expr(node.expr)
        if isinstance(node, C.UnaryOp):
            value = expr(node.expr)
            value = int(not value) if node.op == "!" else value if node.op == "+" else -value
            require(-(2**31) <= value < 2**31, "arithmetic outside this witness-checker's scope")
            return value
        if isinstance(node, C.BinaryOp):
            left = expr(node.left)
            if node.op == "&&":
                return int(bool(left) and bool(expr(node.right)))
            if node.op == "||":
                return int(bool(left) or bool(expr(node.right)))
            right = expr(node.right)
            if node.op == "+":
                require(-(2**31) <= left + right < 2**31, "guard addition overflow")
                return left + right
            return int({"<": left < right, "<=": left <= right, ">": left > right,
                        ">=": left >= right, "==": left == right, "!=": left != right}[node.op])
        if isinstance(node, C.FuncCall):
            require(node.name.name == "atoi" and node.args and len(node.args.exprs) == 1,
                    "input-only expression call")
            arg = node.args.exprs[0]
            require(isinstance(arg, C.ArrayRef) and isinstance(arg.name, C.ID) and
                    arg.name.name == "argv" and isinstance(arg.subscript, C.Constant), "fixed argv index")
            index = int(arg.subscript.value)
            require(1 <= index <= len(point), "argv bounds")
            return point[index-1]
        raise ValueError("unreviewed expression: " + type(node).__name__)
    def statement(node):
        if node is None or isinstance(node, C.EmptyStatement):
            return
        if isinstance(node, C.Compound):
            for child in node.block_items or []:
                statement(child)
        elif isinstance(node, C.Decl):
            if node.init is not None:
                env[node.name] = expr(node.init)
                assignments.append({"line": node.coord.line, "variable": node.name, "value": env[node.name], "kind": "initializer"})
        elif isinstance(node, C.Assignment):
            value = expr(node.rvalue)
            env[node.lvalue.name] = value
            assignments.append({"line": node.coord.line, "variable": node.lvalue.name, "value": value, "kind": "assignment"})
        elif isinstance(node, C.If):
            condition = bool(expr(node.cond))
            branches.append({"line": node.coord.line, "condition": generator.visit(node.cond), "taken": condition})
            statement(node.iftrue if condition else node.iffalse)
        elif isinstance(node, C.FuncCall):
            require(node.name.name == "printf" and node.args and len(node.args.exprs) == 2,
                    "single numeric output")
            require(ast.literal_eval(node.args.exprs[0].value) == "%d\n", "exact output format")
            expr(node.args.exprs[1])
        elif isinstance(node, C.Return):
            expr(node.expr)
            raise Returned()
        else:
            raise ValueError("unreviewed statement: " + type(node).__name__)
    try:
        statement(body)
    except Returned:
        return {"uninitialized_read": False, "branches": branches, "assignments": assignments}
    except Uninitialized as fault:
        require(fault.name in declarations and fault.name not in addresses and fault.name not in env,
                "faulting object is not an uninitialized non-address-taken automatic int")
        return {"uninitialized_read": True, "variable": fault.name,
                "read_line": fault.line, "read_source_line": raw.decode("ascii").splitlines()[fault.line-1],
                "declaration": declarations[fault.name], "address_taken": False,
                "assigned_values_before_fault": dict(sorted(env.items())),
                "branches": branches, "assignments": assignments}
    return {"uninitialized_read": False, "branches": branches, "assignments": assignments}


def review(root=HERE):
    root = Path(root)
    labels = load(root / "labels.json")
    corpus = {case["case_id"]: case for case in load(root / "corpus.json")}
    selected = {row["case_id"]: row for row in labels if "definedness" in row["labels"]}
    require(set(selected) == set(SOURCES), "all and only the nine independently reviewed O0 cases")
    rows = []
    for case_id, source_id in SOURCES.items():
        require(corpus[case_id]["candidate_sha256"] == source_id, "fixed reviewed candidate identity")
        raw = (root / "sources" / (source_id + ".c")).read_bytes()
        require(digest(raw) == source_id, "reviewed source bytes")
        witness = selected[case_id]["witnesses"]["definedness"]
        result = execute_witness(raw, witness["input_values"])
        require(result["uninitialized_read"] is True and
                witness["candidate_semantic"]["undefined_reason"] == "uninitialized-read:" + result["variable"],
                "primary definedness witness is not independently confirmed")
        rows.append({"case_id": case_id, "candidate_sha256": source_id,
                     "point_id": witness["point_id"], "input": witness["input_values"],
                     "result": result})
    return {"schema": "repairseal-independent-definedness-witness-review-v1",
            "status": "PASS_INDEPENDENT_DEFINEDNESS_WITNESSES", "reviewed_patches": len(rows),
            "confirmed_uninitialized_read_witnesses": sum(row["result"]["uninitialized_read"] for row in rows),
            "method": "separate narrow AST path executor tracks actual automatic-int initializations and reads; no import of the primary interpreter or classifier",
            "human_annotators": 0, "human_agreement": None,
            "scope": "One retained concrete O0 witness per each of the nine O0-labelled patches. This independently confirms existence of each claimed uninitialized read, not all undefined points or complete-domain absence of other failures. pycparser is shared parsing infrastructure.",
            "reviewer_sha256": digest(Path(__file__).read_bytes()),
            "inputs": {name: digest((root / name).read_bytes()) for name in ("labels.json", "corpus.json")},
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = review(args.root)
        target = args.root / "independent-definedness.json"
        if args.write:
            target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            require(json.dumps(load(target), sort_keys=True) == json.dumps(result, sort_keys=True),
                    "retained independent O0 proof differs from re-execution")
        print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({"status": "FAIL_INDEPENDENT_DEFINEDNESS_WITNESSES", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
