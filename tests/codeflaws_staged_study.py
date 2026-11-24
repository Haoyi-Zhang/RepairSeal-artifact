"""Deterministic full-index signed-C and upstream test-stage study.

The default command only reads a byte-pinned archive and interprets admitted
closed-language ASTs. Native execution requires --execute-admitted and a new
private --native-work directory. No upstream shell script is ever executed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import signal
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codeflaws_int32_bridge import (PROFILE_ID, AdmittedSource, UnsupportedSource,
    InvalidInput, admit_source, evaluate, parse_input, canonical_output)

ARCHIVE_SHA256 = "2673fc16fa05590c5c1171f5b633594713ae9207346a3d0ba4c4d8b2eea82b11"
ARCHIVE_BYTES = 265695532
INDEX_MEMBER = "codeflaws/codeflaws-defect-detail-info.txt"
SOURCE_NAME = re.compile(r"^codeflaws/([0-9]+-[A-Z0-9]+-bug-[0-9]+-[0-9]+)/([0-9]+-[A-Z0-9]+-[0-9]+\.c)$")
INPUT_NAME = re.compile(r"(?:heldout-)?input-(?:pos|neg)[0-9]+\Z")
CORPUS_SCHEMA = "repairseal-codeflaws-int32-corpus-v1"
STAGE_SCHEMA = "repairseal-codeflaws-upstream-stages-v1"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def verify_archive(path: Path) -> None:
    if not path.is_file() or path.stat().st_size != ARCHIVE_BYTES or file_sha256(path) != ARCHIVE_SHA256:
        raise ValueError("the exact published archive bytes are required")


def _read_regular(tar, member, limit: int) -> bytes:
    if not member.isfile() or not 0 <= member.size <= limit:
        raise ValueError("member type/size: " + member.name)
    raw = tar.extractfile(member).read(limit + 1)
    if len(raw) != member.size:
        raise ValueError("member length: " + member.name)
    return raw


def load_sources(archive: Path):
    verify_archive(archive)
    sources = {}; index = None; licenses = []; seen = set()
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            match = SOURCE_NAME.fullmatch(member.name)
            is_index = member.name == INDEX_MEMBER
            name = PurePosixPath(member.name).name
            is_license = bool(re.fullmatch(r"(?:licen[cs]e|copying|copyright|notice)(?:\..*)?", name, re.I))
            if not (match or is_index or is_license):
                continue
            if member.name in seen:
                raise ValueError("duplicate archive member: " + member.name)
            seen.add(member.name)
            raw = _read_regular(tar, member, 65536 if match else 1048576)
            if match:
                sources[member.name] = raw
            elif is_index:
                index = raw
            else:
                licenses.append({"member": member.name, "sha256": digest(raw), "bytes": len(raw),
                                 "text": raw.decode("utf-8", errors="replace")})
    if index is None:
        raise ValueError("missing official subject index")
    indexed = []
    for line in index.decode("utf-8", errors="strict").splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < 2 or not re.fullmatch(r"[0-9]+-[A-Z0-9]+-bug-[0-9]+-[0-9]+", fields[0]):
            raise ValueError("malformed official index row")
        indexed.append({"id": fields[0], "classification": fields[1]})
    if len({r["id"] for r in indexed}) != len(indexed):
        raise ValueError("duplicate indexed subject")
    return sources, indexed, {"archive_sha256": ARCHIVE_SHA256, "archive_bytes": ARCHIVE_BYTES,
                             "index_member": INDEX_MEMBER, "index_sha256": digest(index),
                             "indexed_subjects": len(indexed), "license_members": licenses,
                             "upstream_sources_redistributed": False}


def expected_members(subject: str) -> tuple[str, str]:
    problem, ids = subject.split("-bug-")
    buggy, accepted = ids.split("-")
    prefix = "codeflaws/" + subject + "/" + problem + "-"
    return prefix + buggy + ".c", prefix + accepted + ".c"


def inspect_sources(sources, indexed):
    cache = {}; rows = []; pairs = []
    for entry in indexed:
        members = expected_members(entry["id"]); programs = []
        for role, member in zip(("original", "reference"), members):
            if member not in sources:
                raise ValueError("indexed source is missing: " + member)
            raw = sources[member]; sha = digest(raw)
            if sha not in cache:
                try:
                    cache[sha] = admit_source(raw, member)
                except UnsupportedSource as exc:
                    cache[sha] = {"code": exc.code, "detail": exc.detail}
            admitted = cache[sha]
            row = {"subject": entry["id"], "classification": entry["classification"], "role": role,
                   "member": member, "sha256": sha, "bytes": len(raw), "admitted": isinstance(admitted, AdmittedSource)}
            if row["admitted"]:
                row.update(input_arity=admitted.input_arity, output_kind=admitted.output_kind,
                           ast_nodes=admitted.ast_nodes)
                programs.append(admitted)
            else:
                row.update(rejection=admitted)
            rows.append(row)
        if len(programs) == 2 and programs[0].input_arity == programs[1].input_arity and programs[0].output_kind == programs[1].output_kind:
            pairs.append(dict(entry, problem=entry["id"].split("-bug-")[0], original_member=members[0],
                              reference_member=members[1], original_sha=digest(sources[members[0]]),
                              reference_sha=digest(sources[members[1]]), input_arity=programs[0].input_arity,
                              output_kind=programs[0].output_kind))
    admitted = {sha: value for sha, value in cache.items() if isinstance(value, AdmittedSource)}
    return rows, pairs, admitted


def read_tests(archive: Path, pairs):
    selected = {p["id"] for p in pairs}; payload = {}; frozen_inputs = defaultdict(list)
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            parts = PurePosixPath(member.name).parts
            if len(parts) != 3 or parts[0] != "codeflaws" or parts[1] not in selected:
                continue
            is_input = INPUT_NAME.fullmatch(parts[2]) is not None
            is_output = INPUT_NAME.fullmatch(parts[2].replace("output-", "input-", 1)) is not None
            if not (is_input or is_output):
                continue
            if is_input:
                frozen_inputs[parts[1]].append(member.name)
            if member.name in payload:
                raise ValueError("duplicate test member")
            try:
                payload[member.name] = _read_regular(tar, member, 4096)
            except ValueError as exc:
                payload[member.name] = {"error": str(exc)}
    subjects = []; statuses = []
    for pair in pairs:
        tests = []; failures = []
        for member in sorted(frozen_inputs[pair["id"]]):
            output = member.replace("/heldout-input-", "/heldout-output-").replace("/input-", "/output-")
            raw, expected_raw = payload.get(member), payload.get(output)
            row = {"subject": pair["id"], "input_member": member, "output_member": output,
                   "split": "heldout" if PurePosixPath(member).name.startswith("heldout-") else "repair"}
            try:
                if not isinstance(raw, bytes) or not isinstance(expected_raw, bytes):
                    raise InvalidInput("missing, invalid, or oversized fixed test member")
                row.update(input_sha256=digest(raw), output_sha256=digest(expected_raw))
                values = parse_input(raw, pair["input_arity"])
                expected = canonical_output(expected_raw, pair["output_kind"])
                test = dict(row, input=list(values), expected=expected)
                tests.append(test); row["eligible"] = True
            except InvalidInput as exc:
                row.update(eligible=False, reason=str(exc)); failures.append(row)
            statuses.append(row)
        if not frozen_inputs[pair["id"]] or not {t["split"] for t in tests} == {"repair", "heldout"}:
            failures.append({"subject": pair["id"], "reason": "missing one upstream test partition"})
        if not failures:
            subjects.append(dict(pair, tests=tests))
    return subjects, statuses, payload


def interpret_subjects(subjects, admitted):
    records = []; cache = {}
    for subject in subjects:
        exclusions = []; role_summaries = {}
        for role in ("original", "reference"):
            sha = subject[role + "_sha"]; mismatches = 0; undefined = Counter(); first_undefined = None
            for test in subject["tests"]:
                key = (sha, tuple(test["input"]))
                if key not in cache:
                    cache[key] = evaluate(admitted[sha], test["input"])
                result = cache[key]
                if not result.defined:
                    undefined[result.undefined_reason] += 1
                    if first_undefined is None:
                        first_undefined = dict(input_member=test["input_member"], input=test["input"],
                                               reason=result.undefined_reason, line=result.undefined_line)
                elif result.value != test["expected"]:
                    mismatches += 1
                records.append(dict(subject=subject["id"], role=role, source_sha256=sha,
                                    input_member=test["input_member"], split=test["split"],
                                    input=test["input"], expected=test["expected"], **result.as_dict()))
            role_summaries[role] = {"all_defined": not undefined, "undefined_test_occurrences": dict(undefined),
                                    "oracle_mismatch_occurrences": mismatches, "first_undefined": first_undefined}
            if undefined:
                exclusions.append({"role": role, "source_sha256": sha, "reasons": dict(undefined), "first": first_undefined})
        # Success/failure against the oracle does not select the cohort.
        subject["eligible"] = not exclusions
        subject["exclusions"] = exclusions
        subject["semantics"] = role_summaries
    return records, cache


def make_corpus(subjects, admitted, source_rows, provenance):
    needed = {s[role + "_sha"] for s in subjects for role in ("original", "reference")}
    aliases = defaultdict(list)
    for row in source_rows:
        if row["sha256"] in needed:
            aliases[row["sha256"]].append(row["member"])
    sources = {}
    for sha in sorted(needed):
        program = admitted[sha]; members = sorted(set(aliases[sha]))
        sources[sha] = {"member": members[0], "aliases": members, "source_sha256": sha,
                        "input_arity": program.input_arity, "input_names": list(program.input_names),
                        "input_targets": list(program.input_targets), "output_kind": program.output_kind,
                        "output_labels": list(program.output_labels), "source_bytes": len(program.raw)}
    return {"schema": CORPUS_SCHEMA, "profile_id": PROFILE_ID, "archive_sha256": ARCHIVE_SHA256,
            "provenance": provenance, "sources": sources, "subjects": subjects,
            "source_payloads": "Not redistributed; read the recorded exact members from the fixed external archive.",
            "semantics": "two's-complement int32 C99 scalar expressions; one canonical output token; fixed original input vectors only",
            "eligibility": "all syntactically admitted source pairs with all upstream test files in the IO profile and both versions defined at every provided input; oracle agreement is not an eligibility filter"}


def staged_requests(corpus, admitted, cache):
    candidates = defaultdict(set); rows = []
    eligible = [s for s in corpus["subjects"] if s["eligible"]]
    for subject in eligible:
        candidates[subject["problem"]].update((subject["original_sha"], subject["reference_sha"]))
    for subject in eligible:
        for sha in sorted(candidates[subject["problem"]]):
            candidate = admitted[sha]
            if candidate.input_arity != subject["input_arity"] or candidate.output_kind != subject["output_kind"]:
                raise ValueError("same-problem candidate interface mismatch")
            counts = {split: Counter() for split in ("repair", "heldout")}; first_failure = {}; undefined = []
            for test in subject["tests"]:
                key = (sha, tuple(test["input"]))
                # Re-evaluate every new cross-subject source/input pair; own-domain
                # definedness is never used as a promise about another test domain.
                if key not in cache:
                    cache[key] = evaluate(candidate, test["input"])
                value = cache[key]
                status = "undefined" if not value.defined else "pass" if value.value == test["expected"] else "mismatch"
                counts[test["split"]][status] += 1
                if status != "pass" and test["split"] not in first_failure:
                    first_failure[test["split"]] = dict(input_member=test["input_member"], input=test["input"],
                                                       expected=test["expected"], **value.as_dict())
                if not value.defined:
                    undefined.append(dict(input_member=test["input_member"], reason=value.undefined_reason))
            passed = {split: bool(counts[split]["pass"]) and not counts[split]["mismatch"] and not counts[split]["undefined"] for split in counts}
            rows.append({"subject": subject["id"], "problem": subject["problem"], "candidate_sha256": sha,
                         "candidate_member": corpus["sources"][sha]["member"], "repair_pass": passed["repair"],
                         "heldout_pass": passed["heldout"], "union_pass": all(passed.values()),
                         "counts": {k: dict(v) for k, v in counts.items()}, "first_failure": first_failure,
                         "undefined": undefined})
    failed = [r for r in rows if r["repair_pass"] and not r["union_pass"]]
    summary = {"eligible_subjects": len(eligible), "distinct_problems": len(candidates),
               "distinct_source_hashes": len(set().union(*candidates.values())),
               "candidate_subject_combinations": len(rows), "repair_pass": sum(r["repair_pass"] for r in rows),
               "both_stages_pass": sum(r["union_pass"] for r in rows), "repair_pass_heldout_fail": len(failed),
               "stage_failure_subjects": len({r["subject"] for r in failed}),
               "stage_failure_candidate_hashes": len({r["candidate_sha256"] for r in failed}),
               "stage_failure_problems": sorted({r["problem"] for r in failed}),
               "undefined_candidate_subject_combinations": sum(bool(r["undefined"]) for r in rows),
               "both_stages_fail": sum(not r["repair_pass"] and not r["heldout_pass"] for r in rows),
               "repair_fail_heldout_pass": sum(not r["repair_pass"] and r["heldout_pass"] for r in rows)}
    return {"schema": STAGE_SCHEMA, "profile_id": PROFILE_ID, "summary": summary, "rows": rows,
            "scope": "Deterministic constructed replay using all same-problem admitted archive sources and the original repair/heldout partitions. No production request logs, manufactured candidates, or synthetic input-axis expansion."}


def run_inspection(archive: Path, output: Path):
    sources, indexed, provenance = load_sources(archive)
    source_rows, pairs, admitted = inspect_sources(sources, indexed)
    all_subjects = {name.split("/")[1] for name in sources}
    provenance["unindexed_archive_subjects"] = sorted(all_subjects - {r["id"] for r in indexed})
    save(output / "archive-provenance.json", provenance)
    save(output / "source-admission.json", {"schema": CORPUS_SCHEMA, "profile_id": PROFILE_ID,
                                           "rows": source_rows, "compatible_pairs": pairs})
    subjects, test_statuses, payload = read_tests(archive, pairs)
    save(output / "test-admission.json", test_statuses)
    observations, cache = interpret_subjects(subjects, admitted)
    corpus = make_corpus(subjects, admitted, source_rows, provenance)
    save(output / "normalized-corpus.json", corpus)
    save(output / "concrete-observations.json", observations)
    stages = staged_requests(corpus, admitted, cache)
    save(output / "staged-requests.json", stages)
    eligible = [s for s in subjects if s["eligible"]]
    summary = {"schema": CORPUS_SCHEMA, "profile_id": PROFILE_ID, "archive_sha256": ARCHIVE_SHA256,
               "indexed_subjects": len(indexed), "indexed_source_occurrences": len(source_rows),
               "syntactically_admitted_source_occurrences": sum(r["admitted"] for r in source_rows),
               "compatible_syntactic_pairs": len(pairs), "complete_io_subjects": len(subjects),
               "all_defined_subjects": len(eligible), "all_defined_problems": len({s["problem"] for s in eligible}),
               "all_defined_classes": dict(Counter(s["classification"] for s in eligible)),
               "test_file_occurrences": sum(len(s["tests"]) for s in eligible),
               "repair_test_occurrences": sum(t["split"] == "repair" for s in eligible for t in s["tests"]),
               "heldout_test_occurrences": sum(t["split"] == "heldout" for s in eligible for t in s["tests"]),
               "subject_distinct_input_vectors": sum(len({tuple(t["input"]) for t in s["tests"]}) for s in eligible),
               "reference_all_oracle_match": sum(s["semantics"]["reference"]["oracle_mismatch_occurrences"] == 0 for s in eligible),
               "original_with_oracle_mismatch": sum(s["semantics"]["original"]["oracle_mismatch_occurrences"] > 0 for s in eligible),
               "excluded_undefined_subjects": [{"id": s["id"], "exclusions": s["exclusions"]} for s in subjects if not s["eligible"]],
               "stage_summary": stages["summary"], "pycparser_version": importlib.metadata.version("pycparser"),
               "native_executed": False, "upstream_scripts_executed": False, "source_payloads_redistributed": False}
    save(output / "summary.json", summary)
    return corpus, admitted, payload, cache, stages, summary


def _native_limits(compiling: bool):
    """Child-only limits; compilation may write its object and executable files."""
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (30 if compiling else 1, 30 if compiling else 1))
    resource.setrlimit(resource.RLIMIT_AS, ((2**31) if compiling else (2**28),) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, ((2**26) if compiling else 0,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (256 if compiling else 32,) * 2)


def bounded_process(command: list[str], raw: bytes, cwd: Path, *, compiling: bool = False):
    timeout = 60.0 if compiling else 2.0
    limit = 65536 if compiling else 4096
    env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "TMPDIR": str(cwd),
           "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=0"}
    started = time.monotonic(); buffers = {"stdout": bytearray(), "stderr": bytearray()}
    seen = Counter(); status = "ok"; process = None
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=cwd, env=env, shell=False,
                                   start_new_session=True, preexec_fn=lambda: _native_limits(compiling))
        try:
            process.stdin.write(raw); process.stdin.close()
        except BrokenPipeError:
            pass
        selector = selectors.DefaultSelector()
        for name in buffers:
            stream = getattr(process, name); os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        deadline = started + timeout
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                status = "timeout"; os.killpg(process.pid, signal.SIGKILL); break
            for key, _events in selector.select(min(remaining, 0.05)):
                block = os.read(key.fileobj.fileno(), 65536)
                if not block:
                    selector.unregister(key.fileobj); key.fileobj.close(); continue
                name = key.data; seen[name] += len(block)
                buffers[name].extend(block[:max(0, limit - len(buffers[name]))])
                if seen[name] > limit:
                    status = "output_limit"; os.killpg(process.pid, signal.SIGKILL); break
            if status != "ok":
                break
        selector.close()
        try:
            process.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            status = "timeout"; os.killpg(process.pid, signal.SIGKILL); process.wait()
        if status == "ok" and process.returncode != 0:
            status = "nonzero"
    except OSError as exc:
        status = "spawn_error"; buffers["stderr"].extend(str(exc).encode()[:limit])
    finally:
        if process is not None:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL); process.wait()
            for stream in (process.stdout, process.stderr, process.stdin):
                if stream is not None and not stream.closed:
                    stream.close()
    captured = {key: bytes(value) for key, value in buffers.items()}
    record = {"command": command, "outcome": status,
              "returncode": process.returncode if process is not None else None,
              "elapsed_seconds": time.monotonic() - started,
              "wall_seconds_limit": timeout, "stream_bytes_limit": limit,
              "stdout_bytes_seen": seen["stdout"], "stderr_bytes_seen": seen["stderr"],
              "stdout_sha256": digest(captured["stdout"]), "stderr_sha256": digest(captured["stderr"]),
              "stdout": captured["stdout"].decode("ascii", errors="backslashreplace"),
              "stderr": captured["stderr"].decode("ascii", errors="backslashreplace"),
              "truncated": any(n > limit for n in seen.values())}
    return record, captured["stdout"], captured["stderr"]


def native_plan(corpus, stages, admitted, payload):
    """Freeze all logical file occurrences, then deduplicate exact source/raw-input bytes."""
    subjects = {s["id"]: s for s in corpus["subjects"]}; cases = {}; occurrences = []
    for request in stages["rows"]:
        subject = subjects[request["subject"]]; sha = request["candidate_sha256"]
        for test in subject["tests"]:
            raw = payload[test["input_member"]]
            if not isinstance(raw, bytes) or digest(raw) != test["input_sha256"]:
                raise ValueError("raw test binding changed")
            values = parse_input(raw, admitted[sha].input_arity)
            if list(values) != test["input"]:
                raise ValueError("raw input/vector mismatch")
            case_id = sha + ":" + test["input_sha256"]
            if case_id not in cases:
                # Never infer cross-subject definedness from a source's own pair.
                concrete = evaluate(admitted[sha], values)
                cases[case_id] = {"id": case_id, "source_sha256": sha,
                                  "input_sha256": test["input_sha256"], "input": list(values),
                                  "raw": raw, "concrete": concrete, "input_aliases": set()}
            cases[case_id]["input_aliases"].add(test["input_member"])
            occurrences.append({"subject": subject["id"], "candidate_sha256": sha,
                                "input_member": test["input_member"], "input_sha256": test["input_sha256"],
                                "output_member": test["output_member"], "output_sha256": test["output_sha256"],
                                "split": test["split"], "native_case_id": case_id,
                                "expected": test["expected"]})
    return cases, occurrences


def run_native(corpus, admitted, payload, _cache, stages, output: Path, work: Path | None, compilers):
    if os.name != "posix" or work is None or len(compilers) != 2:
        raise ValueError("native execution requires POSIX, two explicit compilers, and private work")
    work = work.resolve()
    if work == ROOT or ROOT in work.parents or work.exists() or work.is_symlink():
        raise ValueError("native-work must be a new directory outside the distributable artifact")
    compilers = [p.resolve() for p in compilers]
    if len(set(compilers)) != 2 or any(not p.is_file() for p in compilers):
        raise ValueError("two distinct local compiler executables required")
    cases, occurrences = native_plan(corpus, stages, admitted, payload)
    plan = [{k: v for k, v in case.items() if k not in {"raw", "concrete", "input_aliases"}}
            | {"input_aliases": sorted(case["input_aliases"]), "concrete": case["concrete"].as_dict()}
            for case in cases.values()]
    save(output / "native-plan.json", {"logical_test_occurrences_per_compiler": len(occurrences),
                                        "unique_source_raw_input_cases_per_compiler": len(cases), "cases": plan})
    save(output / "native-test-occurrences.json", occurrences)
    work.mkdir(parents=True)
    source_hashes = sorted({case["source_sha256"] for case in cases.values() if case["concrete"].defined})
    compiler_records = []; compile_records = []; native_rows = []; failures = []
    target_source = ("#include <limits.h>\n#include <stdio.h>\n"
                     "typedef char target[(sizeof(int)==4 && INT_MAX==2147483647 && "
                     "INT_MIN==(-2147483647-1) && ((-1 & 3)==3))?1:-1];\n"
                     "int main(void){puts(\"int32\");return 0;}\n")
    family_seen = set()
    try:
        for index, compiler in enumerate(compilers, 1):
            directory = work / ("compiler-" + str(index)); directory.mkdir()
            version, stdout, _stderr = bounded_process([str(compiler), "--version"], b"", directory, compiling=True)
            version_text = stdout.decode("ascii", errors="replace")
            family = "clang" if "clang" in version_text.lower() else "gcc" if "gcc" in version_text.lower() or "gcc" in compiler.name else None
            if version["outcome"] != "ok" or family is None or family in family_seen:
                raise ValueError("expected one GCC and one Clang compiler")
            family_seen.add(family)
            flags = ["-std=c99", "-O1", "-fno-omit-frame-pointer", "-Werror=implicit-function-declaration", "-Werror=format"]
            if family == "gcc":
                flags += ["-fsanitize=undefined", "-fno-sanitize-recover=all"]
            identity = {"id": family, "executable": str(compiler), "executable_sha256": file_sha256(compiler),
                        "version": version_text.strip(), "flags": flags,
                        "sanitizer": "undefined/halt" if family == "gcc" else "none",
                        "integer_model": "32-bit two's-complement int, compile-time asserted",
                        "target_probe_command": None, "compiled_source_units": 0}
            probe = directory / "target-probe.c"; probe.write_text(target_source)
            probe_bin = directory / "target-probe"
            record, _stdout, _stderr = bounded_process([str(compiler), *flags, str(probe), "-o", str(probe_bin)], b"", directory, compiling=True)
            identity["target_probe_command"] = record["command"]
            if record["outcome"] != "ok":
                raise RuntimeError("compiler/target preflight failed: " + record["stderr"])
            record, stdout, _stderr = bounded_process([str(probe_bin)], b"", directory)
            if record["outcome"] != "ok" or stdout != b"int32\n":
                raise RuntimeError("target preflight run failed")
            if family == "gcc":
                smoke = directory / "ubsan-control.c"
                smoke.write_text('#include <limits.h>\nint main(void){volatile int a=INT_MAX;return a+1;}\n')
                smoke_bin = directory / "ubsan-control"
                built, _stdout, _stderr = bounded_process([str(compiler), *flags, str(smoke), "-o", str(smoke_bin)], b"", directory, compiling=True)
                if built["outcome"] != "ok":
                    raise RuntimeError("UBSan control did not compile")
                control, _stdout, stderr = bounded_process([str(smoke_bin)], b"", directory)
                if control["outcome"] != "nonzero" or b"runtime error:" not in stderr:
                    raise RuntimeError("UBSan control failed to detect signed overflow")
                identity["ubsan_positive_control"] = control
            compiler_records.append(identity)
            binaries = {}
            for sha in source_hashes:
                # Entry point also rechecks the bytes, independent of the caller's object.
                fresh = admit_source(admitted[sha].raw, sha + ".c")
                if fresh.source_sha256 != sha or digest(fresh.raw) != sha:
                    raise ValueError("source binding changed before native compilation")
                path = directory / (sha + ".c"); binary = directory / sha
                path.write_bytes(fresh.raw)
                command = [str(compiler), *flags, str(path), "-o", str(binary)]
                record, _stdout, _stderr = bounded_process(command, b"", directory, compiling=True)
                record.update(compiler=family, source_sha256=sha)
                compile_records.append(record)
                if record["outcome"] != "ok":
                    raise RuntimeError("admitted original failed compilation: " + sha + " " + record["stderr"])
                identity["compiled_source_units"] += 1; binaries[sha] = binary
            print(json.dumps({"native_progress": family, "compiled_sources": len(binaries), "scheduled_cases": len(cases)}), flush=True)
            log = output / ("native-observations-" + family + ".jsonl")
            with log.open("w", encoding="utf-8") as stream:
                for ordinal, case in enumerate(cases.values(), 1):
                    base = {"compiler": family, "sanitizer": identity["sanitizer"], "native_case_id": case["id"],
                            "source_sha256": case["source_sha256"], "input_sha256": case["input_sha256"],
                            "input": case["input"], "input_aliases": sorted(case["input_aliases"]),
                            "interpreted_defined": case["concrete"].defined, "interpreted_value": case["concrete"].value}
                    if not case["concrete"].defined:
                        row = dict(base, outcome="not-run-undefined", native_value=None, agrees=None,
                                   undefined_reason=case["concrete"].undefined_reason)
                    else:
                        process, stdout, stderr = bounded_process([str(binaries[case["source_sha256"]])], case["raw"], directory)
                        native_value = None; outcome = process["outcome"]
                        if outcome == "ok" and stderr:
                            outcome = "unexpected-stderr"
                        if outcome == "ok":
                            try:
                                native_value = canonical_output(stdout, admitted[case["source_sha256"]].output_kind)
                            except InvalidInput:
                                outcome = "output-codec-error"
                        agrees = outcome == "ok" and native_value == case["concrete"].value
                        row = dict(base, outcome=outcome, native_value=native_value, agrees=agrees, process=process)
                        if not agrees:
                            failures.append({"compiler": family, "native_case_id": case["id"], "outcome": outcome})
                    native_rows.append(row)
                    stream.write(json.dumps(row, ensure_ascii=True, allow_nan=False) + "\n")
                    if ordinal % 250 == 0:
                        stream.flush()
                        print(json.dumps({"native_progress": family, "completed": ordinal, "total": len(cases), "failures": len(failures)}), flush=True)
    finally:
        save(output / "native-compilers.json", compiler_records)
        save(output / "native-compilations.json", compile_records)
    summary = {"compilers": len(compiler_records), "distinct_external_source_units": len(source_hashes),
               "compiled_external_source_units": sum(r["compiled_source_units"] for r in compiler_records),
               "logical_test_occurrences_per_compiler": len(occurrences),
               "unique_source_raw_input_cases_per_compiler": len(cases),
               "actual_external_program_executions": sum(r["outcome"] != "not-run-undefined" for r in native_rows),
               "native_interpreter_agreements": sum(r["agrees"] is True for r in native_rows),
               "undefined_not_executed": sum(r["outcome"] == "not-run-undefined" for r in native_rows),
               "failures": failures, "raw_input_bytes_preserved": True,
               "source_bytes_rewritten": False, "upstream_scripts_executed": False,
               "branch_traces_observed_natively": False,
               "cache_key": "compiler identity + source SHA256 + SHA256 of original input-file bytes",
               "scope": "GCC with UBSan and ordinary Clang; resource/codec failures are execution failures, never semantic counterexamples. Duplicate logical file occurrences retain separate alias records."}
    save(output / "native-summary.json", summary)
    if failures:
        raise RuntimeError("native/interpreter disagreements; inspect native-summary.json")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute-admitted", action="store_true")
    parser.add_argument("--native-work", type=Path)
    parser.add_argument("--compiler", type=Path, action="append", default=[])
    args = parser.parse_args()
    archive, output = args.archive.resolve(), args.output.resolve()
    if output.exists() and (output.is_symlink() or any(output.iterdir())):
        raise ValueError("output must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    bindings = {"bridge": file_sha256(ROOT / "src/codeflaws_int32_bridge.py"), "study": file_sha256(Path(__file__))}
    corpus, admitted, payload, cache, stages, summary = run_inspection(archive, output)
    if args.execute_admitted:
        # Defined below with the bounded native runner. Keeping this explicit
        # switch makes inspection safe while external execution remains opt-in.
        summary["native"] = run_native(corpus, admitted, payload, cache, stages, output,
                                       args.native_work, args.compiler)
        summary["native_executed"] = True
    if bindings != {"bridge": file_sha256(ROOT / "src/codeflaws_int32_bridge.py"), "study": file_sha256(Path(__file__))}:
        raise RuntimeError("study implementation changed during execution")
    summary["implementation_bindings"] = bindings
    save(output / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    main()
