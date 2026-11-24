#!/usr/bin/env python3
"""Reconcile retained witness-study records without rerunning external tools."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from pycparser import c_ast, c_parser

if not __debug__:
    raise SystemExit("Witness-record verification requires assertions enabled; -O and -OO are rejected.")

URI = "http://graphml.graphdrawing.org/xmlns"
NS = {"g": URI}
Q = "{" + URI + "}"
ARMS = ("direct", "raw", "context", "standard", "located", "input", "trivial")
CONTEXT_KEYS = {"witness-type", "sourcecodelang", "producer", "specification", "programfile",
                "programhash", "architecture", "creationtime"}


def read(path):
    return json.loads(path.read_text())


def cpa_status(invocation, text):
    terminal = re.findall(r"^Verification result: (TRUE|FALSE|UNKNOWN)\b", text, re.M)
    if invocation["timed_out"]:
        return "TIMEOUT"
    if invocation["exit_code"] != 0:
        return "ERROR"
    if len(terminal) == 1:
        return terminal[0]
    if any(token in text for token in ("Invalid configuration:", "Error:", "Exception")):
        return "ERROR"
    return "UNRESOLVED"


def structure(element, exclude_assumptions=False):
    children = []
    for child in element:
        if exclude_assumptions and child.tag == Q + "data" and child.get("key", "").startswith("assumption"):
            continue
        children.append(structure(child, exclude_assumptions))
    return (element.tag, tuple(sorted(element.attrib.items())), (element.text or "").strip(), tuple(children))


def graph(path):
    return ET.parse(path).getroot().find(Q + "graph")


def envelope(path):
    root = ET.parse(path).getroot()
    assert root.tag == Q + "graphml"
    graphs = root.findall(Q + "graph")
    assert len(graphs) == 1
    assert all(child.tag in {Q + "key", Q + "graph"} for child in root)
    keys = {}
    for declaration in root.findall(Q + "key"):
        identity = declaration.get("id")
        assert identity is not None and identity not in keys, "duplicate GraphML key declaration"
        keys[identity] = structure(declaration)
    metadata = {}
    for item in graphs[0].findall(Q + "data"):
        key = item.get("key")
        assert key is not None and key not in metadata, "duplicate graph metadata"
        metadata[key] = structure(item)
    return {"root_attributes": tuple(sorted(root.attrib.items())),
            "graph_attributes": tuple(sorted(graphs[0].attrib.items())),
            "keys": keys, "metadata": metadata}


def declaration(key, domain="graph"):
    names = {"sourcecodelang": "sourcecodeLanguage", "programfile": "programFile", "programhash": "programHash"}
    return structure(ET.Element(Q + "key", {"id": key, "for": domain, "attr.type": "string",
                                           "attr.name": names.get(key, key)}))


def check_envelopes(directory, expected):
    names = ("raw", "context", "standard", "located", "trivial")
    if (directory / "input.graphml").is_file():
        names += ("input",)
    headers = {name: envelope(directory / (name + ".graphml")) for name in names}
    raw, context = headers["raw"], headers["context"]
    for field in ("root_attributes", "graph_attributes"):
        assert all(header[field] == raw[field] for header in headers.values())
    assert set(context["keys"]) == set(raw["keys"]) | CONTEXT_KEYS
    for key, value in raw["keys"].items():
        assert context["keys"][key] == value
    for key in CONTEXT_KEYS - set(raw["keys"]):
        assert context["keys"][key] == declaration(key)
    assert set(context["metadata"]) == set(raw["metadata"]) | CONTEXT_KEYS
    for key, value in raw["metadata"].items():
        assert context["metadata"][key] == value
    required = {"sourcecodelang": "C", "architecture": "32bit", "programfile": "program.c",
                "programhash": hashlib.sha256((directory / "program.c").read_bytes()).hexdigest(),
                "specification": (directory / "property.prp").read_text().strip(),
                "witness-type": "correctness_witness" if expected == "ACCEPT" else "violation_witness"}
    if "producer" not in raw["metadata"]:
        required["producer"] = "CBMC (context adapter)"
    for key, value in required.items():
        item = ET.Element(Q + "data", {"key": key})
        item.text = value
        assert context["metadata"][key] == structure(item)
    if "creationtime" not in raw["metadata"]:
        assert datetime.fromisoformat(context["metadata"]["creationtime"][2]).utcoffset() is not None
    expected_standard_keys = dict(context["keys"])
    expected_standard_keys.setdefault("assumption.resultfunction", declaration("assumption.resultfunction", "edge"))
    assert headers["standard"]["keys"] == headers["located"]["keys"] == expected_standard_keys
    assert headers["trivial"]["keys"] == context["keys"]
    if "input" in headers:
        assert headers["input"]["keys"] == context["keys"]
    for name in names:
        if name != "raw":
            assert headers[name]["metadata"] == context["metadata"]


def check_arm_inventory(row):
    definitive = row["producer"]["status"] in {"ACCEPT", "REFUTED"}
    if definitive:
        assert set(row["arms"]) == set(ARMS), "definitive producer row must retain every receiving arm"
    else:
        assert not row["arms"], "unresolved producer must not acquire an inferred witness result"


def parsed_source(source):
    lexical = re.sub(r"/\*.*?\*/|//[^\n]*", lambda match: "\n" * match[0].count("\n"), source, flags=re.S)
    return c_parser.CParser().parse(lexical)


def input_sites(source):
    ast = parsed_source(source)
    main = next(node for node in ast.ext if isinstance(node, c_ast.FuncDef) and node.decl.name == "main")
    return [(node.init.coord.line, node.name) for node in main.body.block_items
            if isinstance(node, c_ast.Decl) and isinstance(node.init, c_ast.FuncCall)
            and isinstance(node.init.name, c_ast.ID) and node.init.name.name == "__VERIFIER_nondet_uint"]


def walk_ast(node):
    yield node
    for _, child in node.children():
        yield from walk_ast(child)


def unique_source_calls(source):
    calls = {}
    for node in walk_ast(parsed_source(source)):
        expression = node.init if isinstance(node, c_ast.Decl) else node.rvalue if isinstance(node, c_ast.Assignment) else None
        if not isinstance(expression, c_ast.FuncCall) or not isinstance(expression.name, c_ast.ID):
            continue
        if sum(isinstance(child, c_ast.FuncCall) for child in walk_ast(expression)) == 1:
            calls.setdefault(expression.coord.line, []).append(expression.name.name)
    return {line: names[0] for line, names in calls.items() if len(names) == 1}


def edge_fields(edge):
    fields = {}
    for child in edge:
        assert child.tag == Q + "data" and len(child) == 0
        key = child.get("key")
        assert key is not None and key not in fields, "duplicate edge field cannot be silently collapsed"
        fields[key] = (tuple(sorted(child.attrib.items())), child.text)
    return fields


def check_path_adapter(before, after, mode, source):
    """Allow only the declared annotation rewrites; preserve all other fields."""
    assert mode in {"standard", "located"}
    calls = unique_source_calls(source) if mode == "located" else {}
    old_edges, new_edges = before.findall(Q + "edge"), after.findall(Q + "edge")
    assert len(old_edges) == len(new_edges)
    changes = []
    for old_edge, new_edge in zip(old_edges, new_edges):
        assert old_edge.attrib == new_edge.attrib
        old = edge_fields(old_edge)
        expected = dict(old)
        assumption = old.get("assumption")
        if assumption is not None:
            annotation = assumption[1] or ""
            if mode == "standard":
                match = re.fullmatch(r"return_value_([A-Za-z_][A-Za-z_0-9]*) = ([0-9]+u);", annotation)
                if match:
                    assert "assumption.resultfunction" not in old
                    replacement = "\\result == " + match[2] + ";"
                    expected["assumption"] = (assumption[0], replacement)
                    expected["assumption.resultfunction"] = ((("key", "assumption.resultfunction"),), match[1])
                    changes.append({"source": old_edge.get("source"), "target": old_edge.get("target"),
                                    "before": annotation, "after": replacement, "function": match[1]})
            else:
                line_text = old.get("startline", ((), ""))[1] or ""
                line = int(line_text) if line_text.isdigit() else None
                match = re.fullmatch(r"\\result (?:=|==) ([0-9]+u);", annotation)
                if match and line in calls:
                    assert old.get("originfile", ((), None))[1] == "program.c", "located rewrite must refer to the parsed source file"
                    replacement = "\\result == " + match[1] + ";"
                    prior = old.get("assumption.resultfunction", ((("key", "assumption.resultfunction"),), None))
                    expected["assumption"] = (assumption[0], replacement)
                    expected["assumption.resultfunction"] = (prior[0], calls[line])
                    if annotation != replacement or prior[1] != calls[line]:
                        changes.append({"source": old_edge.get("source"), "target": old_edge.get("target"),
                                        "line": line, "before": annotation, "after": replacement,
                                        "before_function": prior[1], "after_function": calls[line],
                                        "basis": "unique call in parsed C initializer or assignment"})
        assert edge_fields(new_edge) == expected, "undeclared path-annotation change"
    return changes


def check_cpa_record(directory, arm, result, witness_type, protocol, executable):
    invocation = read(directory / (arm + ".invocation.json"))
    assert all(result[key] == value for key, value in invocation.items())
    expected_command = [executable, "--heap", "768M", "--32", "--stats", "--no-output-files",
                        "--timelimit", f"{protocol['cpu_limit_seconds']}s", "--output-path", arm + "-output",
                        "--spec", "property.prp"]
    expected_command += (["--predicateAnalysis"] if arm == "direct" else
                         ["--witnessValidation", "--witness", arm + ".graphml"])
    expected_command += ["program.c"]
    assert invocation["argv"] == expected_command
    assert invocation["cwd"] == "." and invocation["wall_limit_seconds"] == protocol["timeout_seconds"]
    stdout = (directory / (arm + ".stdout.txt")).read_bytes()
    stderr = (directory / (arm + ".stderr.txt")).read_bytes()
    text = (stdout + b"\n" + stderr).decode("utf-8", errors="replace")
    status = cpa_status(invocation, text)
    assert status == result["status"]
    assert result["terminal_results"] == re.findall(r"^Verification result: (TRUE|FALSE|UNKNOWN)\b", text, re.M)
    assert result["warnings"] == [line for line in text.splitlines() if "WARNING" in line]
    ignored = [line for line in text.splitlines()
               if re.search(r"unknown variables|ignor(?:e|ing).*(?:assump|variable|invariant)", line, re.I)]
    assert ignored == result["ignored_semantic_annotations"]
    assert result["witness_type"] == witness_type
    desired = {"correctness_witness": "TRUE", "violation_witness": "FALSE"}.get(witness_type)
    outcome = status if arm == "direct" else ("CONFIRMED" if status == desired else "UNCONFIRMED" if status in {"TRUE", "FALSE"} else status)
    assert outcome == result["outcome"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--interrupted", action="store_true",
                        help="Audit only complete retained case records before an interrupted study is continued; never certifies completeness.")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a new file; completed evidence is never overwritten")
    root = args.study.resolve()
    protocol = read(root / "protocol.json")
    if args.interrupted:
        assert not (root / "summary.json").exists(), "a complete study uses the ordinary verifier"
        rows = sorted((read(path) for path in (root / "cases").glob("*/case-summary.json")), key=lambda row: row["index"])
        controls = []
        summary = None
    else:
        summary = read(root / "summary.json")
        rows, controls = read(root / "cases.json"), read(root / "controls.json")
    assert protocol["pilot_limit"] is None, "the formal verifier does not certify a pilot"
    assert protocol["planned_requests"] == 804
    assert protocol["arms"] == list(ARMS)
    assert protocol["population"] == {"core": 380, "grammar": 400, "natural": 24}
    assert len(protocol["requests"]) == 804
    if args.interrupted:
        indices = [row["index"] for row in rows]
        assert 0 < len(rows) < 804 and len(indices) == len(set(indices))
        assert all(0 <= index < 804 for index in indices)
    else:
        assert len(rows) == 804
        assert [row["index"] for row in rows] == list(range(804))
        assert Counter(row["population"] for row in rows) == {"core": 380, "grammar": 400, "natural": 24}
        assert summary["outcome"] == "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES"
        assert summary["source_inputs_and_tools_unchanged"] is True
        assert summary["producer_disagreements"] == summary["direct_cpa_disagreements"] == []
    if (root / "executed-sources").is_dir():
        for name, binding in protocol["source_files"].items():
            assert hashlib.sha256((root / "executed-sources" / name).read_bytes()).hexdigest() == binding
    tools = {}
    for tool in ("cbmc", "cpachecker", "gcc"):
        probe = read(root / (tool + "-environment.invocation.json"))
        assert probe["exit_code"] == 0 and probe["timed_out"] is False
        assert probe["argv"][1:] == ["--version"]
        tools[tool] = probe["argv"][0]
        assert tools[tool] in protocol["external_tool_files"]
    totals = Counter()
    outcome_counts = {arm: Counter() for arm in ARMS}
    producers = Counter()
    per_type = {arm: {"ACCEPT": Counter(), "REFUTED": Counter()} for arm in ARMS}
    for row in rows:
        directory = root / "cases" / f"{row['index']:04d}"
        declared = protocol["requests"][row["index"]]
        assert (declared["population"], declared["path"]) == (row["population"], row["input_file"])
        check_arm_inventory(row)
        assert read(directory / "case-summary.json") == row
        request = read(directory / "request.json")
        assert hashlib.sha256((directory / "request.json").read_bytes()).hexdigest() == declared["identity"]
        assert request["id"] == row["request_id"]
        for role in ("original", "candidate", "reference"):
            assert (directory / (role + ".c")).read_bytes() == request[role].encode("utf-8")
        assert (directory / "repair_guard.txt").read_bytes() == request["repair_guard"].encode("utf-8")
        assert (directory / "property.prp").read_text() == "CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )\n"
        native = read(directory / "native-correspondence.json")
        n = math.prod(len(values) for values in request["inputs"].values())
        assert n == native["points"] == len(native["expected"]) == len(native["observed"])
        assert native["expected"] == native["observed"] and native["mismatches"] == []
        assert all(type(value) is int and value in {0, 1} for value in native["observed"])
        assert native["refuting_points"] == sum(native["observed"])
        assert row["native_correspondence"] == {key: value for key, value in native.items()
                                                  if key not in {"expected", "observed"}}
        native_invocation = read(directory / "native-compile.invocation.json")
        assert native_invocation["exit_code"] == 0 and native_invocation["timed_out"] is False
        assert native_invocation["argv"] == [tools["gcc"], "-std=c11", "-O0", "-fPIC", "-shared", "-Werror",
                                               "native-wrapper.c", "-o", "native-product.so"]
        expected = "REFUTED" if any(native["observed"]) else "ACCEPT"
        assert read(directory / "receiver-result.json")["status"] == row["receiver_status"] == expected
        producer = read(directory / "producer-result.json")
        assert producer == row["producer"]
        producer_invocation = read(directory / "producer.invocation.json")
        assert all(producer[key] == value for key, value in producer_invocation.items())
        assert producer["argv"] == [tools["cbmc"], "--32", "--c11", "--no-standard-checks", "--graphml-witness",
                                    "raw.graphml", "program.c"]
        assert producer["cwd"] == "." and producer["wall_limit_seconds"] == protocol["timeout_seconds"]
        text = (directory / "producer.stdout.txt").read_text()
        if producer["status"] in {"ACCEPT", "REFUTED"}:
            assert producer["timed_out"] is False
            assert producer["status"] == expected
            assert (producer["exit_code"], "VERIFICATION SUCCESSFUL" in text, "VERIFICATION FAILED" in text) == (
                (0, True, False) if expected == "ACCEPT" else (10, False, True))
        producers[producer["status"]] += 1
        totals["native_points"] += n
        totals["native_compilations"] += 1
        if not row["arms"]:
            continue
        check_envelopes(directory, expected)
        raw, context = graph(directory / "raw.graphml"), graph(directory / "context.graphml")
        for kind in ("node", "edge"):
            assert [structure(e) for e in raw.findall(Q + kind)] == [structure(e) for e in context.findall(Q + kind)]
        expected_binding = hashlib.sha256((directory / "program.c").read_bytes()).hexdigest()
        for name in ("context", "standard", "located", "trivial"):
            g = graph(directory / (name + ".graphml"))
            assert g.find("g:data[@key='programhash']", NS).text == expected_binding
            assert g.find("g:data[@key='specification']", NS).text == (directory / "property.prp").read_text().strip()
            assert g.find("g:data[@key='witness-type']", NS).text == ("correctness_witness" if expected == "ACCEPT" else "violation_witness")
        for name in ("standard", "located"):
            g = graph(directory / (name + ".graphml"))
            assert [structure(e) for e in context.findall(Q + "node")] == [structure(e) for e in g.findall(Q + "node")]
            assert [structure(e, True) for e in context.findall(Q + "edge")] == [structure(e, True) for e in g.findall(Q + "edge")]
        source = (directory / "program.c").read_text()
        standard = graph(directory / "standard.graphml")
        located = graph(directory / "located.graphml")
        standard_changes = check_path_adapter(context, standard, "standard", source)
        located_changes = check_path_adapter(standard, located, "located", source)
        assert standard_changes == read(directory / "adapter-changes.json")
        assert located_changes == read(directory / "location-changes.json")
        assert (len(standard_changes), len(located_changes)) == (row["adapter_changes"], row["location_changes"])
        trivial = graph(directory / "trivial.graphml")
        trivial_nodes, trivial_edges = trivial.findall(Q + "node"), trivial.findall(Q + "edge")
        assert len(trivial_nodes) == len(trivial_edges) == 1
        assert trivial_nodes[0].get("id") == "all"
        node_data = {child.get("key"): child.text for child in trivial_nodes[0]}
        assert node_data == ({"entry": "true", "violation": "true"} if expected == "REFUTED" else {"entry": "true"})
        assert len(trivial_nodes[0]) == len(node_data)
        assert (trivial_edges[0].get("source"), trivial_edges[0].get("target"), len(trivial_edges[0])) == ("all", "all", 0)
        for arm, result in row["arms"].items():
            assert result == read(directory / (arm + "-result.json"))
            outcome_counts[arm][result["outcome"]] += 1
            per_type[arm][expected][result["outcome"]] += 1
            if result["status"] == "NOT_APPLICABLE":
                assert arm == "input" and expected == "ACCEPT" and not (directory / "input.graphml").exists()
                continue
            if result["status"] == "ADAPTER_UNAVAILABLE":
                assert arm == "input" and expected == "REFUTED"
                assert read(directory / "input-projection-error.json")["reason"] == result["reason"]
                continue
            witness_type = None if arm == "direct" else ("correctness_witness" if expected == "ACCEPT" else "violation_witness")
            check_cpa_record(directory, arm, result, witness_type, protocol, tools["cpachecker"])
            if arm == "direct" and result["status"] in {"TRUE", "FALSE"}:
                assert result["status"] == ("TRUE" if expected == "ACCEPT" else "FALSE")
            totals["receiving_processes"] += 1
            totals["ignored_annotation_runs"] += bool(result["ignored_semantic_annotations"])
        if row["arms"]["input"]["status"] not in {"NOT_APPLICABLE", "ADAPTER_UNAVAILABLE"}:
            projection = read(directory / "input-projection.json")
            assert projection["input_order"] == list(request["inputs"])
            sites = input_sites((directory / "program.c").read_text())
            assert [name for _, name in sites] == projection["input_order"]
            assert [line for line, _ in sites] == projection["source_lines"]
            for (line, _), value in zip(sites, projection["values"]):
                candidates = set()
                for raw_edge in raw.findall(Q + "edge"):
                    source_line = raw_edge.find("g:data[@key='startline']", NS)
                    if source_line is None or source_line.text != str(line):
                        continue
                    for annotation in raw_edge.findall("g:data[@key='assumption']", NS):
                        match = re.fullmatch(r"(?:return_value___VERIFIER_nondet_uint(?:\$[0-9]+)?|\\result) (?:=|==) ([0-9]+)u;",
                                             annotation.text or "")
                        if match:
                            candidates.add(int(match[1]))
                assert candidates == {value}, "projected input must be uniquely present in the raw producer graph"
            points = list(itertools.product(*request["inputs"].values()))
            index = projection["native_point_index"]
            assert list(points[index]) == projection["values"] and native["observed"][index] == 1
            g = graph(directory / "input.graphml")
            assert g.find("g:data[@key='programhash']", NS).text == expected_binding
            assert g.find("g:data[@key='specification']", NS).text == (directory / "property.prp").read_text().strip()
            assert g.find("g:data[@key='witness-type']", NS).text == "violation_witness"
            edges = g.findall(Q + "edge")
            assert len(g.findall(Q + "node")) == len(projection["values"]) + 1
            assert len(edges) == len(projection["values"]) + 1
            nodes = {node.get("id"): node for node in g.findall(Q + "node")}
            assert set(nodes) == {f"input{i}" for i in range(len(projection["values"]) + 1)}
            assert nodes["input0"].find("g:data[@key='entry']", NS).text == "true"
            assert nodes[f"input{len(projection['values'])}"].find("g:data[@key='violation']", NS).text == "true"
            for number, (edge, value, source_line) in enumerate(zip(edges, projection["values"], projection["source_lines"])):
                assert (edge.get("source"), edge.get("target")) == (f"input{number}", f"input{number+1}")
                assert edge.find("g:data[@key='assumption']", NS).text == f"\\result == {value}u;"
                assert edge.find("g:data[@key='assumption.resultfunction']", NS).text == "__VERIFIER_nondet_uint"
                assert edge.find("g:data[@key='startline']", NS).text == str(source_line)
                assert edge.find("g:data[@key='assumption.scope']", NS).text == "main"
                assert edge.find("g:data[@key='originfile']", NS).text == "program.c"
            final_state = f"input{len(projection['values'])}"
            assert (edges[-1].get("source"), edges[-1].get("target"), len(edges[-1])) == (final_state, final_state, 0)
            totals["input_projections_native_refuted"] += 1
    if args.interrupted:
        result = {"outcome": "PASS_INTERRUPTED_WITNESS_RECORDS", "requests": len(rows),
                  "planned_requests": 804, "completed_indices": [row["index"] for row in rows],
                  "checked": dict(totals), "producer_statuses": dict(producers),
                  "arm_outcomes": {arm: dict(counts) for arm, counts in outcome_counts.items()},
                  "scope": "Only the listed complete case records were reconciled. This result does not certify completion, pending subjects, or the study-level controls."}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps({key: value for key, value in result.items() if key != "completed_indices"}, indent=2))
        return
    seeds = {}
    for row in rows:
        if row["producer"]["status"] in {"ACCEPT", "REFUTED"}:
            seeds.setdefault((row["population"], row["producer"]["status"]), row["index"])
    expected_controls = Counter((index, kind) for index in seeds.values()
                                for kind in ("malformed", "foreign-context", "contradiction"))
    assert Counter((control["case"], control["type"]) for control in controls) == expected_controls
    for control in controls:
        directory = root / "cases" / f"{control['case']:04d}"
        arm = control["type"]
        row = rows[control["case"]]
        witness_type = "correctness_witness" if row["producer"]["status"] == "ACCEPT" else "violation_witness"
        assert control["population"] == row["population"]
        assert control["declared_witness_type"] == witness_type
        check_cpa_record(directory, arm, control["result"], witness_type, protocol, tools["cpachecker"])
        assert control["result"] == read(directory / (arm + "-result.json"))
        if arm == "malformed":
            try:
                ET.parse(directory / "malformed.graphml")
            except ET.ParseError:
                pass
            else:
                raise AssertionError("malformed-XML control unexpectedly parses")
        elif arm == "foreign-context":
            before_header = envelope(directory / "located.graphml")
            changed_header = envelope(directory / "foreign-context.graphml")
            for field in ("root_attributes", "graph_attributes", "keys"):
                assert changed_header[field] == before_header[field]
            changed = graph(directory / "foreign-context.graphml")
            binding = changed.find("g:data[@key='programhash']", NS)
            assert binding.text == "0" * 64
            expected_binding = hashlib.sha256((directory / "program.c").read_bytes()).hexdigest()
            assert binding.text != expected_binding
            binding.text = expected_binding
            assert structure(changed) == structure(graph(directory / "located.graphml"))
        elif arm == "contradiction":
            assert envelope(directory / "contradiction.graphml") == envelope(directory / "located.graphml")
            g = graph(directory / "contradiction.graphml")
            nodes = g.findall(Q + "node")
            assert len(nodes) == 2 and len(g.findall(Q + "edge")) == 2
            entries = [node for node in nodes if node.find("g:data[@key='entry']", NS) is not None]
            assert len(entries) == 1 and entries[0].get("id") == "entry"
            assert entries[0].find("g:data[@key='entry']", NS).text == "true"
            assert entries[0].find("g:data[@key='violation']", NS) is None
            target = next(node for node in nodes if node.get("id") == "target")
            connection = next(edge for edge in g.findall(Q + "edge")
                              if edge.get("source") == "entry" and edge.get("target") == "target")
            assert int(connection.find("g:data[@key='startline']", NS).text) == control["target_line"]
            assert min(line for line, _ in input_sites((directory / "program.c").read_text())) == control["target_line"]
            loop = next(edge for edge in g.findall(Q + "edge")
                        if edge.get("source") == "target" and edge.get("target") == "target")
            assert len(loop) == 0
            if control["declared_witness_type"] == "violation_witness":
                assert target.find("g:data[@key='violation']", NS).text == "true"
                assert connection.find("g:data[@key='assumption']", NS).text == "0 != 0;"
                assert connection.find("g:data[@key='assumption.scope']", NS).text == "main"
            else:
                assert target.find("g:data[@key='invariant']", NS).text == "0 != 0"
                assert target.find("g:data[@key='invariant.scope']", NS).text == "main"
        totals["control_processes"] += 1
    assert len(controls) == 18
    assert summary["control_runs"] == len(controls)
    for kind in ("malformed", "foreign-context", "contradiction"):
        assert dict(Counter(control["result"]["outcome"] for control in controls if control["type"] == kind)) == summary["controls_by_type"][kind]
    for population in ("core", "grammar", "natural", "all"):
        selected = rows if population == "all" else [row for row in rows if row["population"] == population]
        group = summary["groups"][population]
        assert group["requests"] == len(selected)
        assert group["producer"] == dict(Counter(row["producer"]["status"] for row in selected))
        assert group["native_points"] == sum(row["native_correspondence"]["points"] for row in selected)
        assert group["native_mismatches"] == 0
        for arm in ARMS:
            results = [row["arms"][arm] for row in selected if arm in row["arms"]]
            counts = group["arms"][arm]
            assert counts["runs"] == sum("argv" in result for result in results)
            assert counts["not_applicable"] == sum(result["status"] == "NOT_APPLICABLE" for result in results)
            assert counts["adapter_unavailable"] == sum(result["status"] == "ADAPTER_UNAVAILABLE" for result in results)
            assert counts["status"] == dict(Counter(result["status"] for result in results))
            assert counts["outcome"] == dict(Counter(result["outcome"] for result in results))
            assert counts["runs_with_ignored_annotations"] == sum(bool(result["ignored_semantic_annotations"]) for result in results)
            assert counts["reported_confirmations_without_ignored_annotation_warning"] == sum(
                result["outcome"] == "CONFIRMED" and not result["ignored_semantic_annotations"] for result in results)
            for witness_type in ("correctness_witness", "violation_witness"):
                assert counts["by_witness_type"][witness_type] == dict(Counter(
                    result["outcome"] for result in results if result["witness_type"] == witness_type))
    for arm in ARMS:
        assert dict(outcome_counts[arm]) == summary["groups"]["all"]["arms"][arm]["outcome"]
    assert dict(producers) == summary["groups"]["all"]["producer"]
    assert totals["native_points"] == summary["groups"]["all"]["native_points"]
    result = {"outcome": "PASS_RETAINED_WITNESS_RECORDS", "requests": len(rows),
              "checked": dict(totals), "producer_statuses": dict(producers),
              "arm_outcomes": {arm: dict(counts) for arm, counts in outcome_counts.items()},
              "arm_outcomes_by_claim": {arm: {typ: dict(counts) for typ, counts in groups.items()} for arm, groups in per_type.items()},
              "scope": "Retained command/output reconciliation, exact original input retention, native-vector agreement, context/adapter graph structure, standard input-constraint reconstruction; this audit does not rerun external tools."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
