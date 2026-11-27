"""Narrow, auditable I/O adaptation for six released IntroClass repairs.

This is not a general C preprocessor. It only accepts the released identity
ANGELIX_OUTPUT definition, ordered atoi(argv[k]) scalar input assignments, and
the exact numeric/prompt formats below. Computation, conditionals, statement
order and variable types are preserved. The result must independently pass the
existing whole-source signed-C admission check. Native comparison on every
declared point validates this adaptation's finite correspondence.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys

from pycparser import c_ast, c_generator, c_parser

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import codeflaws_int32_bridge as bridge


class AdaptationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AdaptationError(message)


def _expand_output(text):
    """Expand the exact function-like identity macro using balanced arguments."""
    output = []; cursor = 0; count = 0
    pattern = re.compile(r'\bANGELIX_OUTPUT\s*\(')
    while True:
        matched = pattern.search(text, cursor)
        if matched is None:
            output.append(text[cursor:]); break
        output.append(text[cursor:matched.start()])
        start = matched.end(); depth = 1; quote = None; escaped = False
        args = []; previous = start; i = start
        while i < len(text) and depth:
            ch = text[i]
            if quote:
                if escaped: escaped = False
                elif ch == "\\": escaped = True
                elif ch == quote: quote = None
            elif ch in ('"', "'"): quote = ch
            elif ch == "(": depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0: args.append(text[previous:i].strip())
            elif ch == "," and depth == 1:
                args.append(text[previous:i].strip()); previous = i + 1
            i += 1
        require(depth == 0 and len(args) == 3, "identity macro argument structure")
        require(args[0] == "int" and args[2] == '"stdout"' and args[1], "identity macro signature")
        require("ANGELIX_OUTPUT" not in args[1], "nested identity macro is outside the adapter")
        # The published macro is an unparenthesized identity. Preserve its
        # actual replacement text rather than silently changing precedence.
        output.append(args[1]); count += 1; cursor = i
    return "".join(output), count


def _lex(raw):
    require(type(raw) is bytes and b"\x00" not in raw, "source bytes")
    require(b"??" not in raw and re.search(rb"\\(?:\r\n|\r|\n)", raw) is None,
            "unsupported preprocessing phase")
    text = raw.decode("ascii")
    text = bridge.COMMENT_OR_STRING.sub(
        lambda m: m[1] if m[1] else "".join("\n" if c == "\n" else " " for c in m[2]), text)
    lines = []; headers = []; macro_lines = []
    for line in text.splitlines():
        if not line.lstrip().startswith("#"):
            lines.append(line); continue
        include = re.fullmatch(r"\s*#\s*include\s*<(stdio|stdlib|math)\.h>\s*", line)
        if include:
            require(not "".join(lines).strip(), "include after source tokens")
            headers.append(include[1]); continue
        macro_lines.append(re.sub(r"\s+", " ", line.strip()))
        require(not "".join(lines).strip(), "macro after source tokens")
    require("stdio" in headers, "stdio header required")
    if macro_lines:
        require(macro_lines == ["#ifndef ANGELIX_OUTPUT",
                                "#define ANGELIX_OUTPUT(type, expr, id) expr", "#endif"],
                "only the exact released identity macro block is accepted")
    body = "\n".join(lines)
    if "ANGELIX_OUTPUT" in body:
        require(bool(macro_lines), "unbound output macro")
    body, expanded = _expand_output(body)
    return body, {"headers": headers, "identity_macro_expansions": expanded}


def _integer_type(typ):
    while isinstance(typ, (c_ast.Typename, c_ast.TypeDecl)):
        typ = typ.type
    return isinstance(typ, c_ast.IdentifierType) and typ.names == ["int"]


def normalize(raw, family, reference=False):
    require(family in {"median", "smallest"}, "family")
    arity = 3 if family == "median" else 4
    source, report = _lex(raw)
    tree = c_parser.CParser().parse(source)
    require(len(tree.ext) == 1 and isinstance(tree.ext[0], c_ast.FuncDef), "one main translation unit")
    main = tree.ext[0]
    require(main.decl.name == "main", "main function required")
    require(isinstance(main.decl.type, c_ast.FuncDecl) and _integer_type(main.decl.type.type),
            "original main must return int")
    parameters = main.decl.type.args.params if main.decl.type.args else []
    if reference:
        require(not parameters, "published teacher main has no parameters")
    else:
        require(len(parameters) == 2 and isinstance(parameters[0], c_ast.Decl)
                and parameters[0].name == "argc" and _integer_type(parameters[0].type)
                and isinstance(parameters[1], c_ast.Decl) and parameters[1].name == "argv"
                and bridge._argv_type(parameters[1]), "original main argc/argv signature")
    # Identity int casts are safe here only because the closed signed admission
    # later rejects all non-int operands, wide literals and other casts.
    report.update(identity_int_casts=0, argv_inputs=[], removed_fixed_prompt=False,
                  reformatted_reference_output=False, family=family, arity=arity)
    prompt = f"Please enter {arity} numbers separated by spaces > "
    suffix = f"%d is the {family}\n"
    items = []; input_phase = True; scanf_count = 0
    for statement in main.body.block_items or []:
        if (isinstance(statement, c_ast.FuncCall) and isinstance(statement.name, c_ast.ID)
                and statement.name.name == "printf" and statement.args
                and len(statement.args.exprs) == 1):
            fmt = statement.args.exprs[0]
            require(reference and isinstance(fmt, c_ast.Constant) and fmt.type == "string"
                    and ast.literal_eval(fmt.value) == prompt and input_phase,
                    "only the exact reference input prompt may be omitted")
            require(not report["removed_fixed_prompt"], "duplicate reference prompt")
            report["removed_fixed_prompt"] = True
            continue
        if (isinstance(statement, c_ast.Assignment) and isinstance(statement.rvalue, c_ast.FuncCall)
                and isinstance(statement.rvalue.name, c_ast.ID) and statement.rvalue.name.name == "atoi"):
            require(not reference and input_phase and statement.op == "="
                    and isinstance(statement.lvalue, c_ast.ID), "ordered scalar argv assignment")
            args = statement.rvalue.args.exprs if statement.rvalue.args else []
            require(len(args) == 1 and isinstance(args[0], c_ast.ArrayRef)
                    and isinstance(args[0].name, c_ast.ID) and args[0].name.name == "argv"
                    and isinstance(args[0].subscript, c_ast.Constant)
                    and args[0].subscript.type == "int", "literal argv input index")
            expected_index = len(report["argv_inputs"]) + 1
            require(args[0].subscript.value == str(expected_index), "argv order must be 1 through arity")
            target = statement.lvalue.name
            report["argv_inputs"].append({"index": expected_index, "target": target})
            items.append(c_ast.FuncCall(c_ast.ID("scanf"), c_ast.ExprList([
                c_ast.Constant("string", '"%d"'), c_ast.UnaryOp("&", c_ast.ID(target))])))
            continue
        if isinstance(statement, c_ast.Decl):
            require(_integer_type(statement.type), "all local objects must have type int")
            if statement.init is not None: input_phase = False
        elif (isinstance(statement, c_ast.FuncCall) and isinstance(statement.name, c_ast.ID)
              and statement.name.name == "scanf"):
            require(reference and input_phase, "only the reference has existing initial scanf")
            scanf_count += 1
        elif not isinstance(statement, c_ast.EmptyStatement):
            input_phase = False
        items.append(statement)
    if reference:
        require(scanf_count == 1 and report["removed_fixed_prompt"], "reference input shell")
    else:
        require(len(report["argv_inputs"]) == arity, "complete argv input shell")
    main.body.block_items = items

    def rewrite(node):
        if isinstance(node, c_ast.Cast):
            require(_integer_type(node.to_type), "nonidentity cast")
            report["identity_int_casts"] += 1
            return rewrite(node.expr)
        if (isinstance(node, c_ast.FuncCall) and isinstance(node.name, c_ast.ID)
                and node.name.name == "printf"):
            args = node.args.exprs if node.args else []
            require(len(args) == 2 and isinstance(args[0], c_ast.Constant)
                    and args[0].type == "string", "single numeric output")
            fmt = ast.literal_eval(args[0].value)
            require(fmt == "%d\n" or (reference and fmt == suffix), "exact scalar output format")
            if fmt == suffix:
                report["reformatted_reference_output"] = True
            args[0] = c_ast.Constant("string", json.dumps("%d\n"))
        for slot in node.__slots__:
            if slot in {"coord", "__weakref__"}: continue
            value = getattr(node, slot, None)
            if isinstance(value, c_ast.Node): setattr(node, slot, rewrite(value))
            elif isinstance(value, list):
                setattr(node, slot, [rewrite(x) if isinstance(x, c_ast.Node) else x for x in value])
        return node
    main.body = rewrite(main.body)
    if reference:
        require(report["reformatted_reference_output"], "reference output shell")
    normalized = "#include <stdio.h>\nint main(void)\n" + c_generator.CGenerator().visit(main.body) + "\n"
    admitted = bridge.admit_source(normalized.encode("ascii"))
    require(admitted.input_arity == arity and admitted.output_kind == "numeric", "adapted interface")
    report.update(raw_sha256=hashlib.sha256(raw).hexdigest(),
                  normalized_sha256=hashlib.sha256(normalized.encode()).hexdigest(),
                  original_input_channel="stdin" if reference else "argv",
                  original_output_codec="fixed-reference-prompt-and-suffix" if reference else "exact-decimal-newline",
                  reference_prompt=prompt if reference else "",
                  reference_suffix=f" is the {family}\n" if reference else "",
                  normalized_output_codec="canonical numeric token")
    return normalized, report


def decode_original(raw, mapping):
    text = raw.decode("ascii")
    pattern = re.escape(mapping["reference_prompt"]) + r"(-?(?:0|[1-9][0-9]*))" + re.escape(mapping["reference_suffix"])
    if mapping["original_output_codec"] == "exact-decimal-newline":
        pattern = r"(-?(?:0|[1-9][0-9]*))\n"
    matched = re.fullmatch(pattern, text)
    require(matched is not None and str(int(matched[1])) == matched[1], "original output codec")
    value = int(matched[1])
    require(bridge.INT_MIN <= value <= bridge.INT_MAX, "original output int32 range")
    return str(value)
