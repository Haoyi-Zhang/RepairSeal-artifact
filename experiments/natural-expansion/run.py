"""Fresh full-source scalar case expansion; no source payload is published.

The frozen protocol contains all source/test bindings and finite input points.
Fresh reproduction requires the original hash-pinned external archive. Offline
verification recomputes the summary from retained process/semantic records.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tarfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "src"), str(ROOT / "tests")]
import codeflaws_int32_bridge as bridge
import codeflaws_staged_study as upstream
import int32_circuit as symbolic
import int32_refutation as compact
import proof_dag_checker as core
from domains import declared_points, legal

CORPUS_PATH = ROOT / "data/source-programs/normalized-corpus.json"
EXTRA_SUBJECTS = ["171-B-bug-1463121-1463124", "675-A-bug-18264119-18264212"]
BOUND_SOURCES = [
    "src/codeflaws_int32_bridge.py", "src/int32_circuit.py", "src/int32_refutation.py",
    "src/proof_dag_checker.py", "src/demand_evaluator.py",
    "tests/codeflaws_staged_study.py", "experiments/natural-expansion/run.py",
    "experiments/natural-expansion/domains.py", "experiments/natural-expansion/problem-sources.json",
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n")


def save_lines(path, rows):
    with path.open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n")


def read_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def selection(corpus):
    by_problem = defaultdict(list)
    for subject in corpus["subjects"]:
        if subject["eligible"] and subject["problem"] not in {"4-A", "84-A"}:
            by_problem[subject["problem"]].append(subject)
    def problem_key(problem):
        number, letter = problem.split("-")
        return (by_problem[problem][0]["input_arity"], int(number), letter)
    def subject_key(subject):
        return tuple(map(int, subject["id"].split("-bug-")[1].split("-")))
    chosen = [(min(by_problem[p], key=subject_key), "deterministic-expansion")
              for p in sorted(by_problem, key=problem_key)[:20]]
    indexed = {s["id"]: s for s in corpus["subjects"]}
    chosen.extend((indexed[s], "targeted-prior-record-definedness-followup") for s in EXTRA_SUBJECTS)
    return chosen


def make_protocol():
    corpus = json.loads(CORPUS_PATH.read_text())
    cases = []
    for subject, reason in selection(corpus):
        points = declared_points(subject)
        if len(points) > 4096:
            raise ValueError("declared domain exceeds unchanged admission bound")
        cases.append({
            "subject": subject["id"], "problem": subject["problem"],
            "selection": reason, "input_arity": subject["input_arity"],
            "original_sha256": subject["original_sha"], "reference_sha256": subject["reference_sha"],
            "original_member": subject["original_member"], "reference_member": subject["reference_member"],
            "output_kind": subject["output_kind"], "points": points,
            "given_tests": subject["tests"],
        })
    return {
        "schema": "repairseal-natural-expansion-protocol-v1",
        "archive_sha256": corpus["archive_sha256"], "archive_bytes": upstream.ARCHIVE_BYTES,
        "selection_rule": "Exclude the two previously illustrated problems 4-A and 84-A; sort eligible problems by input arity, numeric contest id, and letter; choose the smallest numeric original/reference id pair per problem; retain the first 20 problems. Separately include two prior-record UB cases, explicitly labelled targeted follow-ups.",
        "domain_rule": "Union all provided repair and held-out vectors with the fixed task-legal points in domains.py. Domain design used the delivered records, including known overflow boundaries, before this new execution. This is an exploratory follow-up, not blind preregistration. No first-eight-test truncation or replacement/removal after observing the new run.",
        "policy": "reference-everywhere", "profile": symbolic.PROFILE,
        "source_bindings": {name: file_hash(ROOT / name) for name in BOUND_SOURCES},
        "corpus_sha256": file_hash(CORPUS_PATH), "cases": cases,
        "candidate_provenance": "The original and accepted source versions are published Codeflaws submissions. Originals are unchanged negative candidates, not outputs of an automatic repair tool; accepted versions are the supplied corrections.",
        "correspondence": "Automatic whole-source admission, independent concrete AST versus typed circuit, and plain GCC/Clang execution on every declared point. This is computational cross-validation, not two-person annotation.",
    }


def load_archive(archive, protocol):
    upstream.verify_archive(archive)
    needed = {}
    for case in protocol["cases"]:
        for role in ("original", "reference"):
            needed[case[role + "_member"]] = (case[role + "_sha256"], bridge.MAX_SOURCE_BYTES)
        for test in case["given_tests"]:
            needed[test["input_member"]] = (test["input_sha256"], 4096)
            needed[test["output_member"]] = (test["output_sha256"], 4096)
    payloads = {}
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            if member.name not in needed:
                continue
            sha, limit = needed[member.name]
            if member.name in payloads:
                raise ValueError("duplicate selected archive member")
            raw = upstream._read_regular(tar, member, limit)
            if digest(raw) != sha:
                raise ValueError("archive member hash mismatch: " + member.name)
            payloads[member.name] = raw
    if set(payloads) != set(needed):
        raise ValueError("missing selected archive members")
    sources = {}; admitted = {}
    for case in protocol["cases"]:
        for role in ("original", "reference"):
            sha = case[role + "_sha256"]; raw = payloads[case[role + "_member"]]
            sources[sha] = raw
            if sha not in admitted:
                admitted[sha] = bridge.admit_source(raw, case[role + "_member"])
        for test in case["given_tests"]:
            if list(bridge.parse_input(payloads[test["input_member"]], case["input_arity"])) != test["input"]:
                raise ValueError("test vector mismatch")
            if bridge.canonical_output(payloads[test["output_member"]], case["output_kind"]) != test["expected"]:
                raise ValueError("test oracle mismatch")
    return sources, admitted, payloads


def semantic_observations(protocol, admitted):
    needed = defaultdict(set)
    for case in protocol["cases"]:
        for role in ("original", "reference"):
            needed[case[role + "_sha256"]].update(tuple(p) for p in case["points"])
    rows = []; index = {}
    for sha, points_set in sorted(needed.items()):
        program = admitted[sha]; points = sorted(points_set)
        circuit = core.Circuit()
        labels = {v: i for i, v in enumerate(program.output_labels)}
        compiled = symbolic.SignedCompiler(circuit, program, labels).compile()
        vectors = symbolic._vectors(circuit, program.input_names, points)
        for ordinal, point in enumerate(points):
            observed = bridge.evaluate(program, point)
            defined = vectors[compiled.defined][ordinal]
            calculated = {
                "defined": defined,
                "value": symbolic.decode(vectors[compiled.output][ordinal], program.output_kind, labels) if defined else None,
                "trace": [[site, int(bool(vectors[guard][ordinal]))] for site, reachable, guard in compiled.events if vectors[reachable][ordinal]],
            }
            concrete = {"defined": observed.defined, "value": observed.value, "trace": [list(x) for x in observed.trace]}
            if not core.exact_equal(calculated, concrete):
                raise AssertionError((sha, point, "independent concrete/circuit mismatch"))
            row = {"source_sha256": sha, "input": list(point), **concrete,
                   "undefined_reason": observed.undefined_reason, "undefined_line": observed.undefined_line,
                   "symbolic": calculated, "symbolic_nodes": len(circuit.nodes), "agrees": True}
            rows.append(row); index[sha, point] = row
    return rows, index


def concrete_decision(case, role, observed):
    sha = case[role + "_sha256"]
    for obligation in ("defined", "repair"):
        bad = []
        for point in case["points"]:
            q = observed[sha, tuple(point)]
            t = observed[case["reference_sha256"], tuple(point)]
            fails = (not q["defined"]) if obligation == "defined" else (not q["defined"] or not t["defined"] or q["value"] != t["value"])
            if fails:
                bad.append((q["trace"], point))
        if bad:
            trace, point = min(bad)
            return {"status": "REFUTED", "witness": {"obligation": obligation, "trace": trace, "input": point}}
    return {"status": "ACCEPT", "witness": None}


def certificate_records(protocol, sources, observed, output):
    records = []
    for case in protocol["cases"]:
        for role in ("original", "reference"):
            task = {"kind": symbolic.PROFILE, "id": case["subject"] + "-" + role,
                    "policy": "reference-everywhere", "points": case["points"],
                    "sources": {"original": sources[case["original_sha256"]].decode(),
                                "candidate": sources[case[role + "_sha256"]].decode(),
                                "reference": sources[case["reference_sha256"]].decode()}}
            expected = concrete_decision(case, role, observed)
            packet = symbolic.make_evidence(task)
            full = symbolic.verify_evidence(task, packet)
            direct = symbolic.evaluate_direct(task)
            recorded, direct_packet = symbolic.evaluate_with_record(task)
            for result in (full, direct, recorded):
                if {k: result[k] for k in ("status", "witness")} != expected:
                    raise AssertionError((task["id"], "receiver/concrete disagreement"))
            if not core.exact_equal(packet, direct_packet):
                raise AssertionError("full and directly materialized records differ")
            packet_path = "packets/" + task["id"] + ".json"
            save(output / packet_path, packet)
            certificate = point_result = None
            if expected["status"] == "REFUTED":
                certificate = compact.produce(task, expected["witness"])
                point_result = compact.check(task, certificate)
                if {k: point_result[k] for k in ("status", "witness")} != expected:
                    raise AssertionError("compact/concrete disagreement")
            records.append({"id": task["id"], "subject": case["subject"], "problem": case["problem"],
                            "candidate_role": role, "candidate_sha256": case[role + "_sha256"],
                            "domain_points": len(case["points"]), "task_sha256": symbolic.task_identity(task),
                            **expected, "full": full, "direct": direct, "direct_record": recorded,
                            "complete_records_identical": True,
                            "packet_path": packet_path, "packet_sha256": file_hash(output / packet_path),
                            "compact_certificate": certificate, "compact": point_result})
        print(json.dumps({"semantic_case_complete": case["subject"], "points": len(case["points"])}), flush=True)
    return records


def bounded_process(command, raw, directory, *, compiling=False):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C", "LC_ALL": "C",
           "TMPDIR": str(directory), "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=0"}
    if os.environ.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    started = time.monotonic(); proc = None; outcome = "ok"
    timeout = 60 if compiling else 2
    try:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=directory, env=env, shell=False, start_new_session=True,
                                preexec_fn=lambda: upstream._native_limits(compiling))
        try:
            stdout, stderr = proc.communicate(raw, timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL); stdout, stderr = proc.communicate(); outcome = "timeout"
        if outcome == "ok" and proc.returncode:
            outcome = "nonzero"
    except OSError as exc:
        stdout, stderr = b"", str(exc).encode(); outcome = "spawn_error"
    limit = 65536 if compiling else 4096
    truncated = len(stdout) > limit or len(stderr) > limit
    if truncated:
        outcome = "output_limit"
    record = {"command": command, "outcome": outcome, "returncode": None if proc is None else proc.returncode,
              "elapsed_seconds": time.monotonic() - started, "wall_seconds_limit": timeout,
              "stdout": stdout[:limit].decode("ascii", errors="backslashreplace"),
              "stderr": stderr[:limit].decode("ascii", errors="backslashreplace"),
              "stdout_sha256": digest(stdout[:limit]), "stderr_sha256": digest(stderr[:limit]),
              "stdout_bytes": len(stdout), "stderr_bytes": len(stderr), "truncated": truncated}
    return record, stdout, stderr


def normalize_paths(value, work):
    if isinstance(value, str): return value.replace(str(work), "<NATIVE_WORK>")
    if isinstance(value, list): return [normalize_paths(x, work) for x in value]
    # Preserve raw captured streams exactly, including paths printed by UBSan.
    if isinstance(value, dict): return {k: v if k in {"stdout", "stderr"} else normalize_paths(v, work) for k, v in value.items()}
    return value


def native_records(protocol, sources, admitted, payloads, observed, output, work, compiler_paths):
    if work.exists() or ROOT == work or ROOT in work.parents:
        raise ValueError("native-work must be a new directory outside artifact")
    work.mkdir(parents=True)
    cases = {}; occurrences = []
    for case in protocol["cases"]:
        for role in ("original", "reference"):
            sha = case[role + "_sha256"]
            for test in case["given_tests"]:
                raw = payloads[test["input_member"]]; case_id = sha + ":" + digest(raw)
                cases[case_id] = {"id": case_id, "source_sha256": sha, "input": test["input"], "raw": raw}
                occurrences.append({"subject": case["subject"], "candidate_role": role,
                                    "source_sha256": sha, "native_case_id": case_id,
                                    "input": test["input"], "expected": test["expected"],
                                    "split": test["split"], "input_member": test["input_member"],
                                    "input_sha256": test["input_sha256"], "output_sha256": test["output_sha256"]})
            for point in case["points"]:
                raw = (" ".join(map(str, point)) + "\n").encode()
                case_id = sha + ":" + digest(raw)
                cases.setdefault(case_id, {"id": case_id, "source_sha256": sha, "input": point, "raw": raw})
    save(output / "test-occurrences.json", occurrences)
    save(output / "native-plan.json", [{k: v for k, v in c.items() if k != "raw"}
                                       | {"input_sha256": digest(c["raw"])} for c in cases.values()])
    compiler_records = []; compilations = []; rows = []; controls = []; families = set()
    target = '#include <limits.h>\n#include <stdio.h>\ntypedef char model[(sizeof(int)==4 && INT_MAX==2147483647 && INT_MIN==(-2147483647-1) && ((-1&3)==3))?1:-1];\nint main(void){puts("int32");return 0;}\n'
    for compiler_path in compiler_paths:
        compiler = compiler_path.resolve()
        directory = work / ("compiler-" + str(len(families))); directory.mkdir()
        record, stdout, _ = bounded_process([str(compiler), "--version"], b"", directory, compiling=True)
        version = stdout.decode("ascii", errors="replace")
        family = "clang" if "clang" in version.lower() else "gcc" if "gcc" in version.lower() else None
        if record["outcome"] != "ok" or family is None or family in families:
            raise ValueError("one executable each from GCC and Clang is required")
        families.add(family)
        base_flags = ["-std=c99", "-O1", "-Werror=implicit-function-declaration", "-Werror=format"]
        identity = {"family": family, "executable": str(compiler), "executable_sha256": file_hash(compiler),
                    "version": version.strip(), "ordinary_flags": base_flags,
                    "sanitizer_flags": base_flags + ["-fsanitize=undefined", "-fno-sanitize-recover=all"],
                    "target": "32-bit two's-complement int, compile-time and runtime asserted"}
        compiler_records.append(identity)
        probe = directory / "probe.c"; probe.write_text(target)
        probe_bin = directory / "probe"
        built, _, _ = bounded_process([str(compiler), *base_flags, str(probe), "-o", str(probe_bin)], b"", directory, compiling=True)
        ran, stdout, _ = bounded_process([str(probe_bin)], b"", directory)
        controls.extend([{"compiler": family, "control": "int32-compile", **built}, {"compiler": family, "control": "int32-run", **ran}])
        if built["outcome"] != "ok" or ran["outcome"] != "ok" or stdout != b"int32\n":
            raise RuntimeError("int32 compiler probe failed")
        smoke = directory / "ubsan-control.c"; smoke.write_text('#include <limits.h>\nint main(void){volatile int a=INT_MAX;return a+1;}\n')
        smoke_bin = directory / "ubsan-control"
        built, _, _ = bounded_process([str(compiler), *identity["sanitizer_flags"], str(smoke), "-o", str(smoke_bin)], b"", directory, compiling=True)
        ran, _, stderr = bounded_process([str(smoke_bin)], b"", directory)
        controls.extend([{"compiler": family, "control": "ubsan-compile", **built}, {"compiler": family, "control": "ubsan-run", **ran}])
        if built["outcome"] != "ok" or ran["outcome"] != "nonzero" or b"runtime error:" not in stderr:
            raise RuntimeError("UBSan positive control failed")
        binaries = {}
        for sha, raw in sorted(sources.items()):
            source_file = directory / (sha + ".c"); source_file.write_bytes(raw)
            if digest(source_file.read_bytes()) != sha:
                raise ValueError("native source bytes changed")
            need_sanitizer = any(not o["defined"] for (s, _p), o in observed.items() if s == sha)
            for mode in (["ordinary", "ubsan"] if need_sanitizer else ["ordinary"]):
                binary = directory / (sha + "-" + mode)
                flags = identity["ordinary_flags"] if mode == "ordinary" else identity["sanitizer_flags"]
                built, _, _ = bounded_process([str(compiler), *flags, str(source_file), "-o", str(binary)], b"", directory, compiling=True)
                built.update(compiler=family, source_sha256=sha, mode=mode,
                             binary_sha256=file_hash(binary) if built["outcome"] == "ok" else None)
                compilations.append(built)
                if built["outcome"] != "ok":
                    raise RuntimeError((family, sha, mode, built["stderr"]))
                binaries[sha, mode] = binary
        log = output / ("native-" + family + ".jsonl")
        with log.open("w") as stream:
            for ordinal, case in enumerate(cases.values(), 1):
                sha = case["source_sha256"]; semantic = observed[sha, tuple(case["input"])]
                for mode in (["ordinary"] if semantic["defined"] else ["ordinary", "ubsan"]):
                    process, stdout, stderr = bounded_process([str(binaries[sha, mode])], case["raw"], directory)
                    native_value = None
                    if process["outcome"] == "ok" and not stderr:
                        try: native_value = bridge.canonical_output(stdout, admitted[sha].output_kind)
                        except bridge.InvalidInput: process["outcome"] = "output-codec-error"
                    semantic_agrees = None if not semantic["defined"] else (process["outcome"] == "ok" and not stderr and native_value == semantic["value"])
                    ubsan_detected = mode == "ubsan" and process["outcome"] == "nonzero" and b"runtime error:" in stderr
                    row = {"compiler": family, "mode": mode, "native_case_id": case["id"],
                           "source_sha256": sha, "input": case["input"], "input_sha256": digest(case["raw"]),
                           "model_defined": semantic["defined"], "model_value": semantic["value"],
                           "native_value": native_value, "semantic_agrees": semantic_agrees,
                           "ubsan_detected": ubsan_detected, "process": normalize_paths(process, work)}
                    rows.append(row)
                    stream.write(json.dumps(row, ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n")
                    if semantic_agrees is False:
                        raise AssertionError((family, sha, case["input"], "defined native mismatch"))
                    if mode == "ubsan" and not ubsan_detected:
                        raise AssertionError((family, sha, case["input"], "undefined observation not diagnosed by UBSan"))
                if ordinal % 500 == 0:
                    stream.flush(); print(json.dumps({"native_compiler": family, "completed": ordinal, "total": len(cases)}), flush=True)
    save(output / "compilers.json", normalize_paths(compiler_records, work))
    save(output / "compilations.json", normalize_paths(compilations, work))
    save(output / "native-controls.json", normalize_paths(controls, work))
    return rows


def recompute(output):
    protocol = json.loads((output / "protocol.json").read_text())
    observations = read_lines(output / "semantic-observations.jsonl")
    observed = {(r["source_sha256"], tuple(r["input"])): r for r in observations}
    requests = json.loads((output / "requests.json").read_text())
    occurrences = json.loads((output / "test-occurrences.json").read_text())
    native = read_lines(output / "native-gcc.jsonl") + read_lines(output / "native-clang.jsonl")
    native_index = {(r["compiler"], r["mode"], r["native_case_id"]): r for r in native}
    rows = []
    protocol_cases = {c["subject"]: c for c in protocol["cases"]}
    for req in requests:
        case = protocol_cases[req["subject"]]
        reference_undefined = [p for p in case["points"] if not observed[case["reference_sha256"], tuple(p)]["defined"]]
        candidate_undefined = [p for p in case["points"] if not observed[req["candidate_sha256"], tuple(p)]["defined"]]
        given = [t for t in occurrences if t["subject"] == req["subject"] and t["candidate_role"] == req["candidate_role"]]
        test_counts = {}
        for compiler in ("gcc", "clang"):
            counts = Counter()
            for test in given:
                r = native_index[compiler, "ordinary", test["native_case_id"]]
                matched = r["process"]["outcome"] == "ok" and not r["process"]["stderr"] and r["native_value"] == test["expected"]
                counts[test["split"] + ("_pass" if matched else "_fail")] += 1
            test_counts[compiler] = dict(sorted(counts.items()))
        all_pass = bool(given) and all(not any(k.endswith("_fail") and v for k, v in c.items()) for c in test_counts.values())
        valid_refutation = req["status"] == "REFUTED" and (req["witness"]["obligation"] == "defined" or not reference_undefined)
        rows.append({"subject": req["subject"], "problem": req["problem"], "candidate_role": req["candidate_role"],
                     "candidate_sha256": req["candidate_sha256"], "domain_points": req["domain_points"],
                     "status": req["status"], "witness": req["witness"], "given_test_occurrences": len(given),
                     "reference_defined_on_declared_domain": not reference_undefined,
                     "reference_undefined_points": len(reference_undefined),
                     "reference_first_undefined_input": reference_undefined[0] if reference_undefined else None,
                     "candidate_undefined_points": len(candidate_undefined),
                     "ordinary_tests": test_counts, "all_given_tests_pass_both_compilers": all_pass,
                     "tests_pass_but_wrong": all_pass and valid_refutation})
    return {
        "schema": "repairseal-natural-expansion-summary-v1", "outcome": "PASS",
        "selection_pairs": sum(c["selection"] == "deterministic-expansion" for c in protocol["cases"]),
        "targeted_definedness_pairs": sum(c["selection"] != "deterministic-expansion" for c in protocol["cases"]),
        "total_pairs": len(protocol["cases"]), "distinct_problems": len({c["problem"] for c in protocol["cases"]}),
        "source_versions": len({c[k] for c in protocol["cases"] for k in ("original_sha256", "reference_sha256")}),
        "requests": len(requests), "statuses": dict(Counter(r["status"] for r in requests)),
        "failure_obligations": dict(Counter(r["witness"]["obligation"] for r in requests if r["witness"])),
        "full_direct_concrete_agreements": sum({k: r["full"][k] for k in ("status", "witness")} == {k: r["direct"][k] for k in ("status", "witness")} == {k: r[k] for k in ("status", "witness")} for r in requests),
        "identical_complete_records": sum(r["complete_records_identical"] for r in requests),
        "compact_confirmations": sum(r["compact"] is not None for r in requests),
        "source_input_observations": len(observations),
        "concrete_symbolic_agreements": sum(r["agrees"] for r in observations),
        "undefined_source_input_observations": sum(not r["defined"] for r in observations),
        "given_test_occurrences_per_compiler": len(occurrences),
        "native_process_executions": len(native),
        "ordinary_process_executions": sum(r["mode"] == "ordinary" for r in native),
        "defined_native_agreements": sum(r["semantic_agrees"] is True for r in native),
        "defined_native_disagreements": sum(r["semantic_agrees"] is False for r in native),
        "ubsan_process_executions": sum(r["mode"] == "ubsan" for r in native),
        "ubsan_confirmations": sum(r["ubsan_detected"] for r in native),
        "all_given_tests_pass_both_compilers": sum(r["all_given_tests_pass_both_compilers"] for r in rows),
        "tests_pass_but_wrong": sum(r["tests_pass_but_wrong"] for r in rows),
        "pairs_with_undefined_reference_on_declared_domain": len({r["subject"] for r in rows if not r["reference_defined_on_declared_domain"]}),
        "computational_annotation_agreement": {"compared": len(observations), "agreed": sum(r["agrees"] for r in observations),
                                                 "human_raters": 0, "scope": "Independent concrete interpreter versus symbolic compiler; source grammar is shared. Native checks compare defined output observations; no native trace is claimed."},
        "cases": rows,
        "scope": "Finite-domain exact-source observations. No automatic-repair-tool provenance is claimed for Codeflaws submissions. Native UB executions are observations of particular compilers, never a defined C value. All provided repair and held-out tests are included. No inference beyond declared points or to independent benchmark samples.",
    }


def run(args):
    output = args.output.resolve()
    if output.exists():
        raise ValueError("output must not exist")
    output.mkdir(parents=True)
    protocol = make_protocol()
    save(output / "protocol.json", protocol)
    save(output / "execution.json", {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                                     "python": sys.version, "platform": platform.platform(),
                                     "command": ["python", "-B", "experiments/natural-expansion/run.py", "--archive", "<PINNED_ARCHIVE>", "--output", "<OUTPUT>", "--native-work", "<NATIVE_WORK>", "--gcc", str(args.gcc), "--clang", str(args.clang)]})
    sources, admitted, payloads = load_archive(args.archive.resolve(), protocol)
    observation_rows, observed = semantic_observations(protocol, admitted)
    save_lines(output / "semantic-observations.jsonl", observation_rows)
    requests = certificate_records(protocol, sources, observed, output)
    save(output / "requests.json", requests)
    native_records(protocol, sources, admitted, payloads, observed, output, args.native_work.resolve(), [args.gcc, args.clang])
    if protocol["source_bindings"] != {name: file_hash(ROOT / name) for name in BOUND_SOURCES}:
        raise RuntimeError("implementation changed while running")
    summary = recompute(output)
    save(output / "summary.json", summary)
    manifest = {str(p.relative_to(output)): file_hash(p) for p in sorted(output.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    save(output / "manifest.json", {"schema": "repairseal-natural-expansion-file-inventory-v1", "files": manifest})
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--native-work", type=Path)
    parser.add_argument("--gcc", type=Path, default=Path(shutil.which("gcc") or "/usr/bin/gcc"))
    parser.add_argument("--clang", type=Path, default=Path(shutil.which("clang") or "/usr/bin/clang"))
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if args.plan_only:
        save(args.output, make_protocol())
        print(json.dumps({"status": "PLANNED", "path": str(args.output)}))
    else:
        if args.archive is None or args.native_work is None:
            parser.error("--archive and --native-work are required for fresh execution")
        run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
