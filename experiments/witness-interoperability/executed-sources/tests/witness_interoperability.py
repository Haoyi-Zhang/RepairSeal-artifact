#!/usr/bin/env python3
"""Run CBMC-produced GraphML through the independent CPAchecker validator.

The experiment compares Boolean finite repair obligations.  It does not ask
either external tool for RepairSeal's canonical diagnostic.  Partial unsigned
operations are made explicit in a C product using an independent pycparser AST;
the raw input functions are retained alongside that product.  Every product is
also compiled and checked at every declared input against the receiver roots.

This script never downloads tools.  It creates a new experiment directory and
retains each command, stdout, stderr, source, witness and classified outcome.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import itertools
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
from cbmc_comparison import population_files
from demand_evaluator import evaluate_demand
from pycparser import c_ast, c_generator, c_parser

GRAPHML = "http://graphml.graphdrawing.org/xmlns"
Q = "{" + GRAPHML + "}"
NS = {"g": GRAPHML}
ET.register_namespace("", GRAPHML)
PROPERTY = "CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )\n"
PARTIAL = {"/": "div", "%": "rem", "<<": "shl", ">>": "shr"}
CBMC_FLAGS = ["--32", "--c11", "--no-standard-checks", "--graphml-witness", "raw.graphml"]
ARMS = ("direct", "raw", "context", "standard", "located", "input", "trivial")


def dump(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def content_identity(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lexical_copy(source: str) -> str:
    # Match C physical line endings before removing comments.  The original
    # source itself is retained verbatim in its own file.
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"/\*.*?\*/|//[^\n]*", " ", source, flags=re.S)


class CheckedGenerator(c_generator.CGenerator):
    """Only the four partial operators change; C controls evaluation order."""

    def visit_BinaryOp(self, node):
        if node.op in PARTIAL:
            return (f"__repairseal_{PARTIAL[node.op]}("
                    f"{self.visit(node.left)}, {self.visit(node.right)})")
        return super().visit_BinaryOp(node)


def emit_product(request: dict) -> str:
    domains, names = core.validate_request_fields(request)
    core.build_expected(request)  # The study population must be admitted first.
    lines = [
        "/* Checked C product of the retained receiver-owned source functions. */",
        "extern unsigned __VERIFIER_nondet_uint(void);",
        "extern void __VERIFIER_error(void);",
    ]
    for op, suffix in PARTIAL.items():
        bad = "y == 0u" if op in {"/", "%"} else "y >= 32u"
        lines += [
            f"static unsigned __repairseal_{suffix}(unsigned x, unsigned y) {{",
            f"  if ({bad}) {{ __VERIFIER_error(); return 0u; }}",
            f"  return x {op} y;",
            "}",
        ]
    generator = CheckedGenerator()
    for role in core.ROLES:
        ast = c_parser.CParser().parse(lexical_copy(request[role]))
        if len(ast.ext) != 1 or not isinstance(ast.ext[0], c_ast.FuncDef):
            raise ValueError("exactly one admitted function required")
        function = ast.ext[0]
        function.decl.name = f"__repairseal_{role}"
        function.decl.type.type.declname = function.decl.name
        lines.append(generator.visit(ast))
    lines += ["int main(void) { "]
    for name in names:
        membership = " || ".join(f"{name} == {value}u" for value in domains[name])
        lines += [f"  unsigned {name} = __VERIFIER_nondet_uint();",
                  f"  if (!({membership})) return 0;"]
    args = ", ".join(names)
    lines += [
        f"  unsigned __repairseal_q = __repairseal_candidate({args});",
        f"  if ({lexical_copy(request['repair_guard'])}) {{",
        f"    unsigned __repairseal_t = __repairseal_reference({args});",
        "    if (__repairseal_q != __repairseal_t) __VERIFIER_error();",
        "  } else {",
        f"    unsigned __repairseal_p = __repairseal_original({args});",
        "    if (__repairseal_q != __repairseal_p) __VERIFIER_error();",
        "  }",
        "  return 0;",
        "}",
    ]
    return "\n".join(lines) + "\n"


def run_process(argv, cwd: Path, prefix: str, timeout: float, env=None):
    started = time.perf_counter()
    p = subprocess.Popen([str(a) for a in argv], cwd=cwd, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = p.communicate()
    record = {"argv": [str(a) for a in argv], "cwd": ".", "exit_code": p.returncode,
              "timed_out": timed_out, "wall_seconds": time.perf_counter() - started,
              "wall_limit_seconds": timeout}
    (cwd / f"{prefix}.stdout.txt").write_bytes(stdout)
    (cwd / f"{prefix}.stderr.txt").write_bytes(stderr)
    dump(cwd / f"{prefix}.invocation.json", record)
    return record, (stdout + b"\n" + stderr).decode("utf-8", errors="replace")


def classify_cpa(record, text: str, witness_type=None):
    statuses = re.findall(r"^Verification result: (TRUE|FALSE|UNKNOWN)\b", text, re.M)
    warnings = [line for line in text.splitlines() if "WARNING" in line]
    ignored = [line for line in text.splitlines()
               if re.search(r"unknown variables|ignor(?:e|ing).*(?:assump|variable|invariant)", line, re.I)]
    if record["timed_out"]:
        status = "TIMEOUT"
    elif record["exit_code"] != 0:
        status = "ERROR"
    elif len(statuses) == 1:
        status = statuses[0]
    elif "Invalid configuration:" in text or "Error:" in text or "Exception" in text:
        status = "ERROR"
    else:
        status = "UNRESOLVED"
    desired = {"violation_witness": "FALSE", "correctness_witness": "TRUE"}.get(witness_type)
    outcome = ("CONFIRMED" if status == desired else
               "UNCONFIRMED" if status in {"TRUE", "FALSE"} else status) if desired else status
    return {**record, "status": status, "outcome": outcome, "witness_type": witness_type,
            "terminal_results": statuses, "warnings": warnings,
            "ignored_semantic_annotations": ignored}


def parse_cbmc(record, text):
    if record["timed_out"]:
        return "TIMEOUT"
    if record["exit_code"] == 0 and "VERIFICATION SUCCESSFUL" in text:
        return "ACCEPT"
    if record["exit_code"] == 10 and "VERIFICATION FAILED" in text:
        return "REFUTED"
    return "ERROR"


def context_tree(raw: Path, program: Path, witness_type: str):
    tree = ET.parse(raw)
    graph = tree.getroot().find(Q + "graph")
    if graph is None:
        raise ValueError("GraphML graph missing")
    metadata = {
        "witness-type": witness_type, "sourcecodelang": "C",
        "producer": "CBMC (context adapter)", "specification": PROPERTY.strip(),
        "programfile": program.name, "programhash": content_identity(program),
        "architecture": "32bit", "creationtime": datetime.now(timezone.utc).isoformat(),
    }
    declarations = {element.get("id"): element for element in tree.getroot().findall(Q + "key")}
    if len(declarations) != len(tree.getroot().findall(Q + "key")):
        raise ValueError("duplicate GraphML key declarations")
    attribute_names = {"sourcecodelang": "sourcecodeLanguage", "programfile": "programFile",
                       "programhash": "programHash"}
    for key in metadata:
        if key not in declarations:
            tree.getroot().insert(0, ET.Element(Q + "key", {
                "id": key, "for": "graph", "attr.type": "string",
                "attr.name": attribute_names.get(key, key)}))
        elif declarations[key].get("for") != "graph":
            raise ValueError(f"conflicting GraphML key domain: {key}")
    existing = {e.get("key"): e for e in graph.findall(Q + "data")}
    for key, value in metadata.items():
        if key in existing:
            if existing[key].text != value and key not in {"producer", "creationtime"}:
                raise ValueError(f"producer metadata conflicts with context: {key}")
        else:
            ET.SubElement(graph, Q + "data", {"key": key}).text = value
    return tree


def standardize_return_assumptions(tree):
    """Translate only CBMC return-value temporary equalities, preserving values.

    No path edge, location, branch, ordinary variable constraint or invariant is
    removed.  Correctness invariants containing internal CBMC expressions are
    intentionally left untouched: a syntax error remains an observed outcome.
    """
    changes = []
    result_key = tree.getroot().find("g:key[@id='assumption.resultfunction']", NS)
    if result_key is None:
        tree.getroot().insert(0, ET.Element(Q + "key", {"id": "assumption.resultfunction",
                            "for": "edge", "attr.type": "string", "attr.name": "assumption.resultfunction"}))
    elif result_key.get("for") != "edge":
        raise ValueError("conflicting GraphML return-function key domain")
    for edge in tree.getroot().findall("g:graph/g:edge", NS):
        for data in edge.findall("g:data[@key='assumption']", NS):
            old = data.text or ""
            match = re.fullmatch(r"return_value_([A-Za-z_][A-Za-z_0-9]*) = ([0-9]+u);", old)
            if not match:
                continue
            if edge.find("g:data[@key='assumption.resultfunction']", NS) is not None:
                raise ValueError("conflicting return-function annotation")
            data.text = "\\result == " + match[2] + ";"
            ET.SubElement(edge, Q + "data", {"key": "assumption.resultfunction"}).text = match[1]
            changes.append({"source": edge.get("source"), "target": edge.get("target"),
                            "before": old, "after": data.text, "function": match[1]})
    return changes


def save_tree(tree, path):
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def call_initializers(program: str):
    """Map source lines having exactly one call in an initializer/assignment.

    This map is parsed from the emitted C, not inferred from the producer's
    claimed scope.  Nested calls and multiple calls at one line are excluded.
    """
    ast = c_parser.CParser().parse(lexical_copy(program))
    candidates = {}

    class Calls(c_ast.NodeVisitor):
        def __init__(self):
            self.calls = []
        def visit_FuncCall(self, node):
            self.calls.append(node)
            self.generic_visit(node)

    class Assignments(c_ast.NodeVisitor):
        def record(self, expression):
            if not isinstance(expression, c_ast.FuncCall) or not isinstance(expression.name, c_ast.ID):
                return
            collector = Calls()
            collector.visit(expression)
            if len(collector.calls) == 1:
                candidates.setdefault(expression.coord.line, []).append(expression.name.name)
        def visit_Decl(self, node):
            self.record(node.init)
            self.generic_visit(node)
        def visit_Assignment(self, node):
            self.record(node.rvalue)
            self.generic_visit(node)
    Assignments().visit(ast)
    return {line: names[0] for line, names in candidates.items() if len(names) == 1}


def locate_return_assumptions(tree, program: str):
    """Bind a return constraint to the uniquely located source call.

    An existing CBMC resultfunction may name the caller instead of the callee.
    Only a single call used as a declaration initializer or assignment RHS can
    resolve it here.  Other annotations stay untouched, including ambiguities.
    """
    calls = call_initializers(program)
    changes = []
    for edge in tree.getroot().findall("g:graph/g:edge", NS):
        line_data = edge.find("g:data[@key='startline']", NS)
        if line_data is None or not (line_data.text or "").isdigit():
            continue
        line = int(line_data.text)
        if line not in calls:
            continue
        for data in edge.findall("g:data[@key='assumption']", NS):
            old = data.text or ""
            match = re.fullmatch(r"\\result (?:=|==) ([0-9]+u);", old)
            if not match:
                continue
            function = edge.find("g:data[@key='assumption.resultfunction']", NS)
            before_function = function.text if function is not None else None
            if function is None:
                function = ET.SubElement(edge, Q + "data", {"key": "assumption.resultfunction"})
            function.text = calls[line]
            data.text = "\\result == " + match[1] + ";"
            if old != data.text or before_function != function.text:
                changes.append({"source": edge.get("source"), "target": edge.get("target"),
                                "line": line, "before": old, "after": data.text,
                                "before_function": before_function, "after_function": function.text,
                                "basis": "unique call in parsed C initializer or assignment"})
    return changes


def trivial_tree(context):
    tree = copy.deepcopy(context)
    graph = tree.getroot().find(Q + "graph")
    assert graph is not None
    witness_type = graph.find("g:data[@key='witness-type']", NS).text
    for child in list(graph):
        if child.tag in {Q + "node", Q + "edge"}:
            graph.remove(child)
    node = ET.SubElement(graph, Q + "node", {"id": "all"})
    ET.SubElement(node, Q + "data", {"key": "entry"}).text = "true"
    if witness_type == "violation_witness":
        ET.SubElement(node, Q + "data", {"key": "violation"}).text = "true"
    ET.SubElement(graph, Q + "edge", {"source": "all", "target": "all"})
    return tree


def input_projection(context, program: str, request: dict, native_record: dict):
    """Project the producer's counterexample onto its concrete input values.

    This is a separate witness representation, not an in-place repair of the
    path witness.  Values come from the producer graph at independently parsed
    input initialization sites; the receiver's canonical witness is not used.
    """
    ast = c_parser.CParser().parse(lexical_copy(program))
    main = next(node for node in ast.ext if isinstance(node, c_ast.FuncDef) and node.decl.name == "main")
    sites = [(node.init.coord.line, node.name) for node in main.body.block_items
             if isinstance(node, c_ast.Decl) and isinstance(node.init, c_ast.FuncCall)
             and isinstance(node.init.name, c_ast.ID) and node.init.name.name == "__VERIFIER_nondet_uint"]
    if [name for _, name in sites] != list(request["inputs"]):
        raise ValueError("input source sites do not match the declared input order")
    by_line = {line: set() for line, _ in sites}
    for edge in context.getroot().findall("g:graph/g:edge", NS):
        source_line = edge.find("g:data[@key='startline']", NS)
        if source_line is None or not (source_line.text or "").isdigit():
            continue
        line = int(source_line.text)
        if line not in by_line:
            continue
        for annotation in edge.findall("g:data[@key='assumption']", NS):
            match = re.fullmatch(r"(?:return_value___VERIFIER_nondet_uint(?:\$[0-9]+)?|\\result) (?:=|==) ([0-9]+)u;",
                                 annotation.text or "")
            if match:
                by_line[line].add(int(match[1]))
    if any(len(values) != 1 for values in by_line.values()):
        raise ValueError("producer did not supply a unique concrete value for every input")
    point = [next(iter(by_line[line])) for line, _ in sites]
    if any(value not in request["inputs"][name] for (_, name), value in zip(sites, point)):
        raise ValueError("producer input lies outside the request domain")
    _, _, points = core.validate_request(request)
    index = points.index(point)
    if native_record["observed"][index] != 1 or native_record["expected"][index] != 1:
        raise AssertionError("producer input did not refute the independently executed product")
    tree = copy.deepcopy(context)
    graph = tree.getroot().find(Q + "graph")
    for child in list(graph):
        if child.tag in {Q + "node", Q + "edge"}:
            graph.remove(child)
    for i in range(len(sites) + 1):
        node = ET.SubElement(graph, Q + "node", {"id": f"input{i}"})
        if i == 0:
            ET.SubElement(node, Q + "data", {"key": "entry"}).text = "true"
        if i == len(sites):
            ET.SubElement(node, Q + "data", {"key": "violation"}).text = "true"
    for i, ((line, _name), value) in enumerate(zip(sites, point)):
        edge = ET.SubElement(graph, Q + "edge", {"source": f"input{i}", "target": f"input{i+1}"})
        for key, text in {"originfile": "program.c", "startline": str(line), "assumption.scope": "main",
                          "assumption": f"\\result == {value}u;",
                          "assumption.resultfunction": "__VERIFIER_nondet_uint"}.items():
            ET.SubElement(edge, Q + "data", {"key": key}).text = text
    ET.SubElement(graph, Q + "edge", {"source": f"input{len(sites)}", "target": f"input{len(sites)}"})
    return tree, {"input_order": list(request["inputs"]), "values": point,
                  "source_lines": [line for line, _ in sites], "native_point_index": index,
                  "native_refutation_checked": True,
                  "representation": "producer input constraints; intra-procedural path annotations erased explicitly"}


def native_correspondence(request, directory, compiler):
    # Each root is evaluated at every point, including points beyond the first
    # counterexample.  No minimum-witness comparison is claimed here.
    _domains, names, points = core.validate_request(request)
    circuit, _programs, _guard, roots = core.build_expected(request)
    positions = {name: i for i, name in enumerate(names)}
    expected = []
    for point in points:
        values = []
        for node in circuit.nodes:
            op = node[0]
            if op in {"u", "b"}:
                value = node[1]
            elif op == "input":
                value = point[positions[node[1]]]
            else:
                value = core.local_value(op, tuple(values[c] for c in node[1:]))
            values.append(value)
        expected.append(int(not all(values[root] for root in roots)))
    wrapper = r'''#define main __repairseal_main
#include "program.c"
#undef main
_Static_assert(sizeof(unsigned) == 4, "32-bit unsigned required");
static unsigned __repairseal_values[8];
static unsigned __repairseal_position;
static int __repairseal_failed;
unsigned __VERIFIER_nondet_uint(void) {
  return __repairseal_values[__repairseal_position++];
}
void __VERIFIER_error(void) { __repairseal_failed = 1; }
int repairseal_point(const unsigned *values, unsigned count) {
  for(unsigned i=0; i<count; ++i) __repairseal_values[i] = values[i];
  __repairseal_position = 0u;
  __repairseal_failed = 0;
  __repairseal_main();
  return __repairseal_failed;
}
'''
    (directory / "native-wrapper.c").write_text(wrapper)
    record, text = run_process([compiler, "-std=c11", "-O0", "-fPIC", "-shared",
                                "-Werror", "native-wrapper.c", "-o", "native-product.so"],
                               directory, "native-compile", 30)
    if record["exit_code"] != 0:
        raise RuntimeError(f"native product compilation failed: {text}")
    library = ctypes.CDLL(str(directory / "native-product.so"))
    function = library.repairseal_point
    function.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.c_uint]
    function.restype = ctypes.c_int
    observed = [function((ctypes.c_uint * len(point))(*point), len(point)) for point in points]
    result = {"points": len(points), "refuting_points": sum(expected),
              "mismatches": [i for i, (a, b) in enumerate(zip(expected, observed)) if a != b],
              "expected": expected, "observed": observed}
    dump(directory / "native-correspondence.json", result)
    # The binary is reproducible from the retained source/command and is not
    # needed in the portable artifact.  CDLL stays valid for this process.
    (directory / "native-product.so").unlink()
    if result["mismatches"]:
        raise AssertionError("checked product and receiver disagree at finite input")
    return {key: value for key, value in result.items() if key not in {"expected", "observed"}}


def cpa_run(args, directory, arm, witness_type, witness_file=None):
    output = directory / (arm + "-output")
    command = [str(args.cpachecker), "--heap", "768M", "--32", "--stats", "--no-output-files",
               "--timelimit", f"{args.cpu_limit}s", "--output-path", output.name,
               "--spec", "property.prp"]
    if witness_file is not None:
        command += ["--witnessValidation", "--witness", witness_file]
    else:
        command += ["--predicateAnalysis"]
    command += ["program.c"]
    record, text = run_process(command, directory, arm, args.timeout)
    result = classify_cpa(record, text, witness_type if witness_file else None)
    dump(directory / (arm + "-result.json"), result)
    return result


def check_case(index, population, path, args, output, environment):
    directory = output / "cases" / f"{index:04d}"
    directory.mkdir(parents=True)
    request = core.load_json_file(path)
    dump(directory / "request.json", request)
    for role in core.ROLES:
        (directory / f"{role}.c").write_bytes(request[role].encode("utf-8"))
    (directory / "repair_guard.txt").write_bytes(request["repair_guard"].encode("utf-8"))
    (directory / "property.prp").write_text(PROPERTY)
    (directory / "program.c").write_text(emit_product(request))
    direct = evaluate_demand(request)
    dump(directory / "receiver-result.json", direct)
    native = native_correspondence(request, directory, args.gcc)
    record, text = run_process([args.cbmc, *CBMC_FLAGS, "program.c"], directory,
                               "producer", args.timeout, environment)
    producer = {**record, "status": parse_cbmc(record, text)}
    dump(directory / "producer-result.json", producer)
    row = {"index": index, "population": population, "request_id": request["id"],
           "input_file": str(path.relative_to(ROOT)), "receiver_status": direct["status"],
           "producer": producer, "native_correspondence": native, "arms": {}}
    if producer["status"] not in {"ACCEPT", "REFUTED"}:
        dump(directory / "case-summary.json", row)
        return row
    if producer["status"] != direct["status"]:
        raise AssertionError(f"producer mismatch in case {index}")
    witness_type = "correctness_witness" if producer["status"] == "ACCEPT" else "violation_witness"
    tree = context_tree(directory / "raw.graphml", directory / "program.c", witness_type)
    save_tree(tree, directory / "context.graphml")
    standard = copy.deepcopy(tree)
    changes = standardize_return_assumptions(standard)
    save_tree(standard, directory / "standard.graphml")
    located = copy.deepcopy(standard)
    location_changes = locate_return_assumptions(located, (directory / "program.c").read_text())
    save_tree(located, directory / "located.graphml")
    save_tree(trivial_tree(tree), directory / "trivial.graphml")
    projection_error = None
    if witness_type == "violation_witness":
        try:
            projected, input_record = input_projection(tree, (directory / "program.c").read_text(), request,
                                                       json.loads((directory / "native-correspondence.json").read_text()))
            save_tree(projected, directory / "input.graphml")
            dump(directory / "input-projection.json", input_record)
        except ValueError as error:
            # A producer format outside the adapter is a recorded outcome;
            # disagreement at an actually extracted point remains fatal.
            projection_error = str(error)
            dump(directory / "input-projection-error.json", {"reason": projection_error})
    dump(directory / "adapter-changes.json", changes)
    dump(directory / "location-changes.json", location_changes)
    row["adapter_changes"] = len(changes)
    row["location_changes"] = len(location_changes)
    # Rotate arm order deterministically; timing is only an execution log.
    order = list(ARMS[index % len(ARMS):] + ARMS[:index % len(ARMS)])
    for arm in order:
        if arm == "input" and witness_type == "correctness_witness":
            row["arms"][arm] = {"status": "NOT_APPLICABLE", "outcome": "NOT_APPLICABLE",
                                "witness_type": witness_type, "ignored_semantic_annotations": [],
                                "reason": "a concrete input is an existential refutation, not a universal acceptance proof"}
            dump(directory / (arm + "-result.json"), row["arms"][arm])
            continue
        if arm == "input" and projection_error is not None:
            row["arms"][arm] = {"status": "ADAPTER_UNAVAILABLE", "outcome": "ADAPTER_UNAVAILABLE",
                                "witness_type": witness_type, "ignored_semantic_annotations": [],
                                "reason": projection_error}
            dump(directory / (arm + "-result.json"), row["arms"][arm])
            continue
        row["arms"][arm] = cpa_run(args, directory, arm, witness_type,
                                    None if arm == "direct" else arm + ".graphml")
    row["arm_order"] = order
    dump(directory / "case-summary.json", row)
    return row


def run_controls(rows, args, output):
    # First request in each population/producer-status stratum, selected from
    # the declared ordering rather than from successful validator outcomes.
    seeds = {}
    for row in rows:
        if row["producer"]["status"] in {"ACCEPT", "REFUTED"}:
            seeds.setdefault((row["population"], row["producer"]["status"]), row)
    controls = []
    for key, row in seeds.items():
        directory = output / "cases" / f"{row['index']:04d}"
        base = ET.parse(directory / "located.graphml")
        witness_type = "correctness_witness" if key[1] == "ACCEPT" else "violation_witness"
        changed = copy.deepcopy(base)
        changed.getroot().find("g:graph/g:data[@key='programhash']", NS).text = "0" * 64
        save_tree(changed, directory / "foreign-context.graphml")
        (directory / "malformed.graphml").write_text("<graphml><not-closed>")
        for arm in ("foreign-context", "malformed"):
            result = cpa_run(args, directory, arm, witness_type, arm + ".graphml")
            controls.append({"case": row["index"], "population": key[0], "type": arm,
                             "declared_witness_type": witness_type, "result": result})
        # Start from the well-formed, unrestricted control rather than from a
        # possibly unparsable producer invariant.  This isolates contradictory
        # content from producer-format compatibility.
        contradiction = trivial_tree(base)
        graph = contradiction.getroot().find(Q + "graph")
        calls = call_initializers((directory / "program.c").read_text())
        target_line = min(line for line, name in calls.items() if name == "__VERIFIER_nondet_uint")
        for element in list(graph):
            if element.tag in {Q + "node", Q + "edge"}:
                graph.remove(element)
        entry = ET.SubElement(graph, Q + "node", {"id": "entry"})
        ET.SubElement(entry, Q + "data", {"key": "entry"}).text = "true"
        target = ET.SubElement(graph, Q + "node", {"id": "target"})
        edge = ET.SubElement(graph, Q + "edge", {"source": "entry", "target": "target"})
        ET.SubElement(edge, Q + "data", {"key": "originfile"}).text = "program.c"
        ET.SubElement(edge, Q + "data", {"key": "startline"}).text = str(target_line)
        if witness_type == "violation_witness":
            # Entry is not a violation node; the only transition reaching the
            # violation node is impossible.  An initial violation node would
            # invalidate this control by accepting the empty witness path.
            ET.SubElement(target, Q + "data", {"key": "violation"}).text = "true"
            ET.SubElement(edge, Q + "data", {"key": "assumption"}).text = "0 != 0;"
            ET.SubElement(edge, Q + "data", {"key": "assumption.scope"}).text = "main"
        else:
            # The first input initialization is reached on every main path;
            # its successor carries a false invariant in the correct scope.
            ET.SubElement(target, Q + "data", {"key": "invariant"}).text = "0 != 0"
            ET.SubElement(target, Q + "data", {"key": "invariant.scope"}).text = "main"
        ET.SubElement(graph, Q + "edge", {"source": "target", "target": "target"})
        save_tree(contradiction, directory / "contradiction.graphml")
        result = cpa_run(args, directory, "contradiction", witness_type, "contradiction.graphml")
        controls.append({"case": row["index"], "population": key[0], "type": "contradiction",
                         "declared_witness_type": witness_type, "target_line": target_line, "result": result})
    dump(output / "controls.json", controls)
    return controls


def summarize(rows, controls):
    groups = {}
    for population in ("core", "grammar", "natural", "all"):
        selected = rows if population == "all" else [r for r in rows if r["population"] == population]
        groups[population] = {
            "requests": len(selected),
            "producer": dict(Counter(r["producer"]["status"] for r in selected)),
            "native_points": sum(r["native_correspondence"]["points"] for r in selected),
            "native_mismatches": sum(len(r["native_correspondence"]["mismatches"]) for r in selected),
            "arms": {},
        }
        for arm in ARMS:
            values = [r["arms"][arm] for r in selected if arm in r["arms"]]
            groups[population]["arms"][arm] = {
                "runs": sum("argv" in r for r in values),
                "not_applicable": sum(r["status"] == "NOT_APPLICABLE" for r in values),
                "adapter_unavailable": sum(r["status"] == "ADAPTER_UNAVAILABLE" for r in values),
                "status": dict(Counter(r["status"] for r in values)),
                "outcome": dict(Counter(r["outcome"] for r in values)),
                "runs_with_ignored_annotations": sum(bool(r["ignored_semantic_annotations"]) for r in values),
                "reported_confirmations_without_ignored_annotation_warning": sum(
                    r["outcome"] == "CONFIRMED" and not r["ignored_semantic_annotations"] for r in values),
                "by_witness_type": {typ: dict(Counter(v["outcome"] for v in values if v["witness_type"] == typ))
                                    for typ in ("correctness_witness", "violation_witness")},
            }
    disagreements = [r["index"] for r in rows if r["producer"]["status"] in {"ACCEPT", "REFUTED"}
                     and r["producer"]["status"] != r["receiver_status"]]
    direct_disagreements = [r["index"] for r in rows if r["arms"].get("direct", {}).get("status") in {"TRUE", "FALSE"}
                           and (r["arms"]["direct"]["status"] == "TRUE") != (r["receiver_status"] == "ACCEPT")]
    return {"groups": groups, "producer_disagreements": disagreements,
            "direct_cpa_disagreements": direct_disagreements,
            "control_runs": len(controls),
            "controls_by_type": {kind: dict(Counter(c["result"]["outcome"] for c in controls if c["type"] == kind))
                                 for kind in ("foreign-context", "malformed", "contradiction")},
            "measurement": "One process call per arm/case; wall times are execution logs, not a matched timing estimate.",
            "output_contract": "Boolean definedness and guarded equality only; no canonical diagnostic comparison.",
            "validation_interpretation": "CONFIRMED is the tool-reported kind-specific Boolean result, not a claim that every annotation was checked. Ignored-annotation warnings and negative controls are retained separately. TRUE from a violation validator means unconfirmed witness, not a new unrestricted safety proof.",
            "outcome": "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cbmc", type=Path, required=True)
    parser.add_argument("--cpachecker", type=Path, required=True)
    parser.add_argument("--gcc", type=Path, default=Path("/usr/bin/gcc"))
    parser.add_argument("--library-dir", type=Path, action="append", default=[])
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--cpu-limit", type=int, default=30)
    parser.add_argument("--limit", type=int, help="Explicit pilot prefix; omitted for all 804 requests.")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 4 or args.timeout <= 0 or args.cpu_limit <= 0:
        parser.error("jobs 1..4 and positive time limits required")
    for name in ("output", "cbmc", "cpachecker", "gcc"):
        setattr(args, name, getattr(args, name).resolve())
    if args.output.exists():
        parser.error("output must be new")
    for name in ("cbmc", "cpachecker", "gcc"):
        p = getattr(args, name)
        if not p.is_file() or not os.access(p, os.X_OK):
            parser.error(f"{name} is not an executable file")
    cases = population_files(["core", "grammar", "natural"], ROOT / "proof-data",
                             ROOT / "revision_audit/round2/natural-domains-final")
    if args.limit is not None:
        if args.limit <= 0:
            parser.error("pilot limit must be positive")
        cases = cases[:args.limit]
    environment = dict(os.environ)
    if args.library_dir:
        environment["LD_LIBRARY_PATH"] = os.pathsep.join(str(p.resolve()) for p in args.library_dir)
    args.output.mkdir(parents=True)
    source_names = ["tests/witness_interoperability.py", "src/proof_dag_checker.py",
                    "src/demand_evaluator.py", "tests/cbmc_comparison.py", "tests/scientific_driver.py"]
    source_before = {name: content_identity(ROOT / name) for name in source_names}
    input_before = {str(path.relative_to(ROOT)): content_identity(path) for _, path in cases}
    validator_root = args.cpachecker.parent.parent
    tool_files = [args.cbmc, args.cpachecker, args.gcc]
    tool_files += sorted(validator_root.glob("*.jar"))
    tool_files += sorted((validator_root / "config").rglob("*.properties"))
    tool_files += sorted((validator_root / "config").rglob("*.spc"))
    tool_files += sorted((validator_root / "lib").rglob("*.jar"))
    tool_files += sorted((validator_root / "lib").rglob("*.so"))
    tool_before = {str(path): content_identity(path) for path in tool_files}
    protocol = {
        "population": {"core": 380, "grammar": 400, "natural": 24}, "pilot_limit": args.limit,
        "planned_requests": len(cases), "arms": list(ARMS), "jobs": args.jobs,
        "timeout_seconds": args.timeout, "cpu_limit_seconds": args.cpu_limit,
        "selection": "All requests in the existing unsigned CBMC comparison, in its declared ordering.",
        "source_transform": "Independent pycparser AST; replace /,% with zero-divisor guards and shifts with count<32 guards; retain all other expressions/control flow; finite input membership through main return branches.",
        "source_roles": "Candidate always executes; reference only under repair guard, original only otherwise.",
        "native_validation": "Compile each checked product with GCC and compare every declared input against all receiver obligation roots.",
        "witness_context": "Add required graph metadata only; preserve nodes, edges, locations and semantic annotations.",
        "standard_adapter": "Replace exact CBMC return_value_FUNCTION = UINTu equalities with standard result-function annotations. No invariant removal or path weakening.",
        "located_adapter": "Additionally bind a result constraint to the uniquely parsed source call in an initializer/assignment at its reported line. All modifications logged; ambiguous locations left unchanged.",
        "input_projection": "Violation-only additional representation: extract producer concrete inputs at independently parsed nondeterministic input sites; require native refutation at that exact point; retain those standard input constraints and erase intra-procedural path annotations explicitly. Acceptance cases are NOT_APPLICABLE.",
        "trivial_control": "Same witness type/context, one entry state with an unrestricted self-loop; no semantic annotations.",
        "negative_controls": "First case of each population/producer-result stratum; malformed XML, wrong source binding and contradictory annotations at first nondeterministic initialization; program/property unchanged. Contradictory violation witness has distinct entry/violation states and a false-only connecting edge.",
        "output_contract": "Boolean finite obligation, not canonical witness or materialized record.",
        "timing_interpretation": "Execution logs only. Direct predicate analysis and automatic witness configurations differ; no wall-time speedup claim.",
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "pycparser_distribution": importlib.metadata.version("pycparser")},
        "source_files": source_before, "external_tool_files": tool_before,
        "requests": [{"population": pop, "path": str(path.relative_to(ROOT)), "identity": content_identity(path)}
                     for pop, path in cases],
    }
    dump(args.output / "protocol.json", protocol)
    for name in ("cbmc", "cpachecker", "gcc"):
        rec, text = run_process([getattr(args, name), "--version"], args.output, name + "-environment", 20,
                                environment if name == "cbmc" else None)
        if rec["exit_code"] != 0:
            raise RuntimeError(f"{name} environment probe failed: {text}")
    rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(check_case, i, population, path, args, args.output, environment)
                   for i, (population, path) in enumerate(cases)]
        for future in as_completed(futures):
            try:
                rows.append(future.result())
            except BaseException:
                for remaining in futures:
                    remaining.cancel()
                dump(args.output / "completed-before-failure.json", sorted(rows, key=lambda row: row["index"]))
                raise
            if len(rows) % 20 == 0 or len(rows) == len(cases):
                dump(args.output / "progress.json", {"completed_indices": sorted(r["index"] for r in rows),
                                                       "planned_requests": len(cases)})
                print(json.dumps({"completed": len(rows), "planned": len(cases),
                                  "standard": dict(Counter(r["arms"].get("standard", {}).get("outcome", "MISSING") for r in rows))}), flush=True)
    rows.sort(key=lambda r: r["index"])
    dump(args.output / "cases.json", rows)
    controls = run_controls(rows, args, args.output)
    summary = summarize(rows, controls)
    summary["source_inputs_and_tools_unchanged"] = (
        source_before == {name: content_identity(ROOT / name) for name in source_names}
        and input_before == {str(path.relative_to(ROOT)): content_identity(path) for _, path in cases}
        and tool_before == {str(path): content_identity(path) for path in tool_files})
    if not summary["source_inputs_and_tools_unchanged"]:
        summary["outcome"] = "FAILED_CHANGED_EXECUTION_INPUT"
    dump(args.output / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    if summary["producer_disagreements"] or summary["direct_cpa_disagreements"] or not summary["source_inputs_and_tools_unchanged"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
