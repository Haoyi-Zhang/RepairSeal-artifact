#!/usr/bin/env python3
"""Independent structural and concrete review of six fixed IntroClass repairs.

The adapter, native runner, signed bridge and circuit receiver are not imported.
Reviewed raw-source identities select separately written control-flow models.
A second AST traversal compares all computation nodes and ordered statements
after explicitly accounting for input/output shells.  The models then check
every retained raw/normalized GCC/Clang execution and every semantic value and
branch trace.  This is a computational review, not a human sign-off or a proof
for arbitrary C programs.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from pycparser import c_ast as C, c_parser


HERE = Path(__file__).resolve().parent
ARTIFACT = HERE.parents[1]
PATCHES = ARTIFACT / "experiments/real-patches"
CASE_SOURCES = {
    "apr-043": ("median", "9053c0838e6608983a10ec8f5d3c7cef0fc81deb69181c0aa4596e555ca637d0", "40a5a239d6478a964d11210129202ff413a64291e6290e8269048d2e4af8d4ec"),
    "apr-046": ("median", "d82a6b552a442e241cb35c8fe7aa33315efa990d76dcc3abf243ab3e1dbeb72f", "149a8a5fbb67c35e930136165c8153aa32d8033f08d8b8e00f3463be5bade837"),
    "apr-069": ("median", "507dbc460c4196b74ca0f3c2e2dba597bd3018f27695233d8933e33c8ae2398a", "82bfa47a55903d17f34150217bec6cc51eebeb7ec6a316fb31e23e0e692ab289"),
    "apr-070": ("median", "a214b35ef181635655214aeffb38b11cf1d9115079e3ef89a7de89680e9fda75", "054e9df95ba7b83cc970131e33c8c200d1139c31f5068e1061bb91416e314c2e"),
    "apr-072": ("smallest", "60f94f186ed17612fa0dad01e8ca704ebc19ec464b86eed755b1f4964405f1ef", "10985f694b7a31840113671e0451066d9678ccf160158cbb3eb682208436df27"),
    "apr-073": ("smallest", "60f94f186ed17612fa0dad01e8ca704ebc19ec464b86eed755b1f4964405f1ef", "5c2a509c0f949d306af92033bcb231c5293605796847b192d4126d507324045a"),
}
REFERENCES = {
    "median": "e805c04dbe96129bc40dcd1586aa6d9d70d4284544629202a47ce9eb51b4d50f",
    "smallest": "e80241d9eee5ef6b7ff3fc002a1866454154da3079fcb04655fbc8b00529cde7",
}
MODEL_ROLES = {sha: (case_id, "original", family)
               for case_id, (family, sha, _candidate) in CASE_SOURCES.items()}
MODEL_ROLES.update({sha: (case_id, "candidate", family)
                    for case_id, (family, _original, sha) in CASE_SOURCES.items()})
MODEL_ROLES.update({sha: (None, "reference", family) for family, sha in REFERENCES.items()})
COMMENTS = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(/\*.*?\*/|//[^\r\n]*)', re.S)
SIMPLE_MACRO = re.compile(r'\bANGELIX_OUTPUT\s*\(\s*int\s*,\s*((?:\(int\)\s*)?[A-Za-z_][A-Za-z_0-9]*)\s*,\s*"stdout"\s*\)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode()


def pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, "duplicate JSON member")
        result[key] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def lines(path):
    with Path(path).open() as stream:
        return [json.loads(line, object_pairs_hook=pairs) for line in stream if line.strip()]


def exact(left, right):
    return canonical(left) == canonical(right)


def keyed(rows, fields):
    result = {}
    for row in rows:
        key = tuple(tuple(row[field]) if isinstance(row[field], list) else row[field] for field in fields)
        require(key not in result, "duplicate execution/observation key")
        result[key] = row
    return result


def model(source_id, point):
    """Separately derived branch models for reviewed, hash-fixed sources."""
    require(source_id in MODEL_ROLES, "source has no independently reviewed branch model")
    case_id, role, family = MODEL_ROLES[source_id]
    require(len(point) == (3 if family == "median" else 4) and
            all(type(value) is int and -(2**31) <= value < 2**31 for value in point),
            "declared signed input vector")
    trace = []
    def branch(site, condition):
        trace.append([site, int(condition)])
        return condition
    if role == "reference":
        if family == "median":
            a, b, c = point
            if branch(0, a < b):
                upper, lower = b, a
            else:
                upper, lower = a, b
            if branch(1, upper < c):
                value = upper
            elif branch(2, c > lower):
                value = c
            else:
                value = lower
            require(value == sorted(point)[1], "independent median-reference derivation")
        else:
            a, b, c, d = point
            left = a if branch(0, a < b) else b
            right = d if branch(1, d < c) else c
            value = left if branch(2, left < right) else right
            require(value == min(point), "independent minimum-reference derivation")
    elif family == "median":
        a, b, c = point
        first = (a > b and a < c) or (a < b and a > c)
        second = (b > a and b < c) or (b < a and b > c)
        if role == "candidate":
            if case_id == "apr-043":
                first = (a >= b and a < c) or (a < b and a > c)
            elif case_id == "apr-046":
                second = (c > a and b < c) or (b > c and b < a)
            elif case_id == "apr-069":
                second = (b >= a and c > b) or (b < a and b > c)
            elif case_id == "apr-070":
                first = (a < b and a > c) or (a >= b and a < c)
        value = a if branch(0, first) else b if branch(1, second) else c
    else:
        a, b, c, d = point
        value = a
        if branch(0, a > b):
            value = b
        if branch(1, b > c):
            value = c
        third = c > d if role == "original" else c > c if case_id == "apr-072" else d < d
        if branch(2, third):
            value = b if role == "candidate" and case_id == "apr-073" else d
        elif branch(3, a > d):
            value = d
    return str(value), trace


def parse_for_review(raw, normalized=False):
    text = raw.decode("ascii")
    text = COMMENTS.sub(lambda match: match[1] if match[1] else
                        "".join("\n" if char == "\n" else " " for char in match[2]), text)
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    text, macro_count = SIMPLE_MACRO.subn(lambda match: match[1], text)
    require("ANGELIX_OUTPUT" not in text, "independent review only admits simple identity macro arguments")
    tree = c_parser.CParser().parse(text)
    require(len(tree.ext) == 1 and isinstance(tree.ext[0], C.FuncDef), "single reviewed main")
    main = tree.ext[0]
    require(main.decl.name == "main" and main.decl.type.type.type.names == ["int"],
            "reviewed main return type")
    return main, macro_count


def structural_signature(main, family, raw_source, reference):
    """Second AST traversal preserves every computational child and its order."""
    arity = 3 if family == "median" else 4
    stats = {"identity_int_casts": 0, "omitted_fixed_prompt": 0,
             "input_targets": [], "if_nodes": 0}
    declared = set()
    def is_int(node):
        while isinstance(node, (C.Typename, C.TypeDecl)):
            node = node.type
        return isinstance(node, C.IdentifierType) and node.names == ["int"]
    def sign(node, top=False):
        if node is None:
            return None
        if isinstance(node, C.Compound):
            items = []
            for item in node.block_items or []:
                value = sign(item, top=top)
                if value is not None:
                    items.append(value)
            return ["Compound", items]
        if isinstance(node, C.Decl):
            require(is_int(node.type) and not node.quals and not node.storage,
                    "all reviewed data objects are automatic signed int")
            require(node.name not in declared, "reviewed declarations have no shadowing")
            declared.add(node.name)
        if isinstance(node, C.Cast):
            require(raw_source and is_int(node.to_type) and isinstance(node.expr, C.ID)
                    and node.expr.name in declared, "only independently verified int-to-int identifier casts")
            stats["identity_int_casts"] += 1
            return sign(node.expr)
        if (isinstance(node, C.Assignment) and isinstance(node.rvalue, C.FuncCall)
                and isinstance(node.rvalue.name, C.ID) and node.rvalue.name.name == "atoi"):
            require(raw_source and not reference and top and node.op == "=" and
                    isinstance(node.lvalue, C.ID), "raw ordered argv input assignment")
            args = node.rvalue.args.exprs
            require(len(args) == 1 and isinstance(args[0], C.ArrayRef) and
                    isinstance(args[0].name, C.ID) and args[0].name.name == "argv" and
                    isinstance(args[0].subscript, C.Constant) and
                    args[0].subscript.value == str(len(stats["input_targets"]) + 1),
                    "exact argv input index")
            stats["input_targets"].append(node.lvalue.name)
            return ["Input", [node.lvalue.name]]
        if isinstance(node, C.FuncCall):
            require(isinstance(node.name, C.ID), "direct call")
            args = node.args.exprs if node.args else []
            require(args and isinstance(args[0], C.Constant) and args[0].type == "string",
                    "literal input/output format")
            fmt = ast.literal_eval(args[0].value)
            if node.name.name == "scanf":
                require(top and (reference or not raw_source), "initial scanf input shell")
                require(re.fullmatch(r"\s*(?:%d\s*)+", fmt) and fmt.count("%d") == len(args)-1,
                        "scanf exact decimal arity")
                targets = []
                for arg in args[1:]:
                    require(isinstance(arg, C.UnaryOp) and arg.op == "&" and
                            isinstance(arg.expr, C.ID) and arg.expr.name in declared,
                            "scanf target is declared signed int")
                    targets.append(arg.expr.name)
                stats["input_targets"].extend(targets)
                return ["Input", targets]
            require(node.name.name == "printf", "no computational external call")
            if len(args) == 1:
                require(raw_source and reference and top and
                        fmt == f"Please enter {arity} numbers separated by spaces > ",
                        "only the reviewed fixed teacher prompt is omitted")
                stats["omitted_fixed_prompt"] += 1
                return None
            require(len(args) == 2 and
                    (fmt == "%d\n" or raw_source and reference and fmt == f"%d is the {family}\n"),
                    "complete reviewed numeric output codec")
            return ["Output", sign(args[1])]
        if isinstance(node, C.If):
            stats["if_nodes"] += 1
        if isinstance(node, C.ID):
            require(node.name not in {"argv", "argc"}, "argument objects only serve the input shell")
        return [type(node).__name__, [[name, getattr(node, name)] for name in node.attr_names],
                [[name, sign(child)] for name, child in node.children()]]
    result = sign(main.body, top=True)
    require(len(stats["input_targets"]) == arity and len(set(stats["input_targets"])) == arity,
            "one ordered read of every independent scalar input")
    require(stats["omitted_fixed_prompt"] == int(raw_source and reference), "teacher prompt coverage")
    return result, stats


def validate_process(process):
    require(process["outcome"] == "ok" and type(process["returncode"]) is int and
            process["returncode"] == 0 and process["truncated"] is False,
            "successful complete native execution")
    for stream in ("stdout", "stderr"):
        require(type(process[stream]) is str and sha(process[stream].encode()) == process[stream + "_sha256"]
                and type(process[stream + "_bytes"]) is int and
                len(process[stream].encode()) == process[stream + "_bytes"], "native stream binding")
    require(process["stderr"] == "", "no hidden native diagnostic")


def review(data):
    data = Path(data)
    protocol = load(data / "protocol.json")
    require(protocol["selected_case_ids"] == list(CASE_SOURCES), "fixed six-case selection")
    for relative, expected in protocol["source_bindings"].items():
        require(sha((ARTIFACT / relative).read_bytes()) == expected,
                "executed source binding changed: " + relative)
    mappings = load(data / "mappings.json")
    require(set(mappings) == set(MODEL_ROLES), "review covers every raw and normalized source")
    source_rows = []
    for ident, (_case_id, role, family) in sorted(MODEL_ROLES.items()):
        mapping = mappings[ident]
        raw = (PATCHES / "sources" / (ident + ".c")).read_bytes()
        normalized = (data / mapping["normalized_path"]).read_bytes()
        require(sha(raw) == ident and sha(normalized) == mapping["normalized_sha256"], "source bytes")
        raw_main, macros = parse_for_review(raw)
        new_main, new_macros = parse_for_review(normalized, normalized=True)
        old_shape, old_stats = structural_signature(raw_main, family, True, role == "reference")
        new_shape, new_stats = structural_signature(new_main, family, False, role == "reference")
        require(exact(old_shape, new_shape), "computation AST or statement order changed: " + ident)
        require(macros == mapping["identity_macro_expansions"] and new_macros == 0 and
                old_stats["identity_int_casts"] == mapping["identity_int_casts"], "adaptation operation counts")
        require(old_stats["input_targets"] == new_stats["input_targets"], "input target ordering")
        require(mapping["original_input_channel"] == ("stdin" if role == "reference" else "argv"),
                "input channel declaration")
        source_rows.append({"raw_sha256": ident, "normalized_sha256": sha(normalized),
                            "family": family, "role": role, "computation_ast_equal": True,
                            "computation_ast_sha256": sha(canonical(old_shape)),
                            "raw_structure": old_stats, "normalized_structure": new_stats,
                            "domain_points": len(protocol["points"][family])})
    semantic = keyed(lines(data / "semantic-observations.jsonl"), ("raw_source_sha256", "input"))
    native = keyed(lines(data / "native-gcc.jsonl") + lines(data / "native-clang.jsonl"),
                   ("raw_source_sha256", "input", "compiler", "variant"))
    expected_semantic = {(ident, tuple(point)) for ident, (_, _, family) in MODEL_ROLES.items()
                         for point in protocol["points"][family]}
    require(set(semantic) == expected_semantic, "complete semantic point-set closure")
    expected_native = {(ident, point, compiler, variant) for ident, point in expected_semantic
                       for compiler in ("gcc", "clang") for variant in ("original", "normalized")}
    require(set(native) == expected_native, "complete two-compiler two-variant native closure")
    for ident, point in expected_semantic:
        value, trace = model(ident, list(point))
        observation = semantic[(ident, point)]
        require(observation["defined"] is True and observation["value"] == value and
                exact(observation["trace"], trace), "independent model value or branch trace differs")
        require(exact(observation["symbolic"], {"defined": True, "value": value, "trace": trace}),
                "symbolic observation differs from independent source model")
        _, role, family = MODEL_ROLES[ident]
        for compiler in ("gcc", "clang"):
            for variant in ("original", "normalized"):
                row = native[(ident, point, compiler, variant)]
                process = row["process"]
                validate_process(process)
                expected_stdout = value + "\n"
                if role == "reference" and variant == "original":
                    expected_stdout = f"Please enter {len(point)} numbers separated by spaces > " + value + f" is the {family}\n"
                require(process["stdout"] == expected_stdout and row["value"] == value and
                        row["expected_value"] == value and row["agrees"] is True,
                        "full native stdout differs from independent source model/codec")
                argv_input = role != "reference" and variant == "original"
                stdin = b"" if argv_input else (" ".join(map(str, point)) + "\n").encode()
                require(row["stdin_sha256"] == sha(stdin), "native input stream binding")
                require(process["command"][1:] == (list(map(str, point)) if argv_input else []),
                        "native argv inputs")
    requests = keyed(load(data / "requests.json"), ("case_id",))
    require(set(requests) == {(case_id,) for case_id in CASE_SOURCES}, "all requested certificate cases")
    case_rows = []
    for case_id, (family, original, candidate) in CASE_SOURCES.items():
        request = requests[(case_id,)]
        points = protocol["points"][family]
        bad = []
        for point in points:
            value, trace = model(candidate, point)
            reference, _ = model(REFERENCES[family], point)
            if value != reference:
                bad.append((trace, point))
        require(bool(bad), "reviewed candidate has no real finite counterexample")
        trace, point = min(bad)
        expected_witness = {"obligation": "repair", "trace": trace, "input": point}
        require(exact(request["witness"], expected_witness) and request["status"] == "REFUTED" and
                type(request["mismatch_points"]) is int and request["mismatch_points"] == len(bad),
                "complete canonical result differs from independent control-flow model")
        for arm in ("full", "direct", "direct_record", "compact"):
            require(request[arm]["status"] == "REFUTED" and exact(request[arm]["witness"], expected_witness),
                    "receiving arm result differs from independent model")
        checked = 0
        for test in protocol["given_tests"][family]:
            answer = str(sorted(test["input_values"])[1] if family == "median" else min(test["input_values"]))
            require(test["expected_stdout"] == answer + "\n", "published test's numeric oracle")
            for compiler in ("gcc", "clang"):
                row = native[(candidate, tuple(test["input_values"]), compiler, "original")]
                require(row["process"]["stdout"] == test["expected_stdout"], "original candidate fails a supplied test")
                checked += 1
        require(checked > 0, "vacuous supplied-test acceptance")
        case_rows.append({"case_id": case_id, "family": family, "domain_points": len(points),
                          "mismatch_points": len(bad), "canonical_witness": expected_witness,
                          "candidate_value": model(candidate, point)[0],
                          "reference_value": model(REFERENCES[family], point)[0],
                          "original_value": model(original, point)[0],
                          "given_test_compiler_checks": checked, "all_given_tests_pass": True})
    return {
        "schema": "repairseal-independent-introclass-normalization-review-v1",
        "status": "PASS_INDEPENDENT_NORMALIZATION_REVIEW",
        "method": "separate whole-body AST correspondence and hash-fixed separately written control-flow models; no import of normalization, bridge, circuit or collection implementations",
        "human_annotators": 0, "human_agreement": None,
        "boundaries": ["finite declared inputs and the thirteen exact source identities only",
                       "pycparser is shared parsing infrastructure; the AST comparison and concrete models are separate implementations",
                       "all scalar computations in these reviewed sources are int comparisons and assignments; int casts are applied only to declared int identifiers",
                       "argv strings and stdin tokens are canonical decimal encodings of values in int32 range",
                       "the complete teacher prompt/suffix and exact candidate decimal-newline outputs are checked; no arbitrary stripping",
                       "the signed request uses reference-everywhere; preservation classification remains in the separate real-patch study"],
        "review_findings_resolved": ["identity macro expansion now preserves the original unparenthesized replacement text",
                                     "the original main return and argument signatures are checked before input adaptation"],
        "reviewed_patches": len(case_rows), "reviewed_sources": len(source_rows),
        "structural_correspondence_agreements": len(source_rows),
        "independent_value_and_trace_agreements": len(semantic),
        "independent_native_output_agreements": len(native),
        "canonical_counterexample_agreements": len(case_rows),
        "given_test_compiler_checks": sum(row["given_test_compiler_checks"] for row in case_rows),
        "reviewer_sha256": sha(Path(__file__).read_bytes()),
        "reviewed_implementation_sha256": {name: sha((HERE / name).read_bytes()) for name in ("normalize.py", "run.py")},
        "input_record_sha256": {name: sha((data / name).read_bytes()) for name in
                                 ("protocol.json", "mappings.json", "requests.json", "semantic-observations.jsonl",
                                  "native-gcc.jsonl", "native-clang.jsonl")},
        "sources": source_rows, "cases": case_rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = review(args.data)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({key: value for key, value in result.items() if key not in {"sources", "cases"}}, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"status": "FAIL_INDEPENDENT_NORMALIZATION_REVIEW", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
