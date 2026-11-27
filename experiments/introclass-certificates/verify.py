"""Offline source, vector, refutation and native-receipt verification."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("repairseal_intro_certificate_collection", HERE / "run.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)


def require(value, message):
    if not value:
        raise ValueError(message)


def safe_file(root, name):
    path = root / name
    require(type(name) is str and not Path(name).is_absolute() and ".." not in Path(name).parts
            and path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(), "unsafe record path")
    return path


def verify(root: Path | None = None, records: Path | None = None):
    root = ROOT if root is None else Path(root)
    output = root / "experiments/introclass-certificates/records" if records is None else Path(records)
    errors = []; checks = 0; result = None
    try:
        manifest = json.loads((output / "manifest.json").read_text())["files"]
        actual_files = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file() and p.name != "manifest.json"}
        require(set(manifest) == actual_files, "manifest completeness")
        for name, expected in manifest.items():
            require(study.file_hash(safe_file(output, name)) == expected, "record hash: " + name)
            checks += 1
        protocol = json.loads((output / "protocol.json").read_text())
        require(study.core.exact_equal(protocol, study.declaration()), "fixed case selection, domains, tests or source bindings")
        mappings = json.loads((output / "mappings.json").read_text())
        expected_sources = {c[role + "_sha256"] for c in protocol["cases"] for role in ("original", "candidate", "reference")}
        require(set(mappings) == expected_sources, "mapped source coverage")
        observations = study.read_lines(output / "semantic-observations.jsonl")
        observed = {(r["raw_source_sha256"], tuple(r["input"])): r for r in observations}
        expected_observations = {(sha, tuple(p)) for sha, m in mappings.items() for p in protocol["points"][m["family"]]}
        require(set(observed) == expected_observations and len(observed) == len(observations), "semantic point coverage")
        for sha, mapping in mappings.items():
            raw = (study.PATCHES / "sources" / (sha + ".c")).read_bytes()
            require(study.digest(raw) == sha, "published source identity")
            text, derived = study.adapter.normalize(raw, mapping["family"], mapping["reference"])
            derived["reference"] = mapping["reference"]; derived["normalized_path"] = "normalized/" + sha + ".c"
            require(study.core.exact_equal(derived, mapping), "normalization correspondence map")
            require(safe_file(output, mapping["normalized_path"]).read_text() == text, "normalized source replay")
            admitted = study.bridge.admit_source(text.encode())
            for point in protocol["points"][mapping["family"]]:
                retained = observed[sha, tuple(point)]
                value = study.bridge.evaluate(admitted, point)
                expected = {"defined": value.defined, "value": value.value, "trace": [list(t) for t in value.trace]}
                symbolic = study.symbolic.evaluate_program(admitted, point)
                calculated = {"defined": symbolic["defined"], "value": symbolic["value"], "trace": [list(t) for t in symbolic["trace"]]}
                require(value.defined and study.core.exact_equal(expected, calculated), "independent concrete versus circuit replay")
                require(study.core.exact_equal({k: retained[k] for k in expected}, expected)
                        and study.core.exact_equal(retained["symbolic"], calculated), "semantic observation replay")
                require(retained["normalized_source_sha256"] == mapping["normalized_sha256"], "observation source binding")
                if mapping["reference"]:
                    require(retained["reference_math_agreement"] is True and value.value == study.mathematical(mapping["family"], point), "reference mathematical oracle")
            checks += 1
        requests = json.loads((output / "requests.json").read_text())
        require([r["case_id"] for r in requests] == protocol["selected_case_ids"], "request coverage and order")
        for case, row in zip(protocol["cases"], requests):
            task = json.loads(safe_file(output, row["request_path"]).read_text())
            packet = json.loads(safe_file(output, row["full_path"]).read_text())
            certificate = json.loads(safe_file(output, row["compact_path"]).read_text())
            expected_task = {"kind": study.symbolic.PROFILE, "id": "introclass-" + case["case_id"],
                             "policy": "reference-everywhere", "points": protocol["points"][case["family"]],
                             "sources": {role: safe_file(output, mappings[case[role + "_sha256"]]["normalized_path"]).read_text()
                                         for role in ("original", "candidate", "reference")}}
            require(study.core.exact_equal(task, expected_task), "complete source and domain request binding")
            bad = [(observed[case["candidate_sha256"], tuple(p)]["trace"], p) for p in task["points"]
                   if observed[case["candidate_sha256"], tuple(p)]["value"] != observed[case["reference_sha256"], tuple(p)]["value"]]
            require(bool(bad), "genuine repair counterexample")
            trace, point = min(bad)
            expected = {"status": "REFUTED", "witness": {"obligation": "repair", "trace": trace, "input": point}}
            full = study.symbolic.verify_evidence(task, packet)
            direct = study.symbolic.evaluate_direct(task)
            direct_record, reproduced_packet = study.symbolic.evaluate_with_record(task)
            confirmation = study.compact.check(task, certificate)
            require(study.core.exact_equal(packet, reproduced_packet), "identical complete materialized records")
            for name, arm in (("full", full), ("direct", direct), ("direct_record", direct_record), ("compact", confirmation)):
                require(study.core.exact_equal(arm, row[name]), "fresh offline receiver replay: " + name)
                require({k: arm[k] for k in ("status", "witness")} == expected, "canonical result agreement: " + name)
            require(confirmation["checked_points"] == 1 and confirmation["checked_cells"] == confirmation["checked_nodes"], "point-local compact checking")
            require(row["task_sha256"] == study.symbolic.task_identity(task) and row["domain_points"] == len(task["points"])
                    and row["mismatch_points"] == len(bad), "request identity and counts")
            for role in ("original", "candidate", "reference"):
                require(row[role + "_at_witness"] == observed[case[role + "_sha256"], tuple(point)]["value"], "witness concrete value")
            checks += 1
        native = study.read_lines(output / "native-gcc.jsonl") + study.read_lines(output / "native-clang.jsonl")
        index = {(r["compiler"], r["raw_source_sha256"], r["variant"], tuple(r["input"])): r for r in native}
        expected_native = {(compiler, sha, variant, point) for compiler in ("gcc", "clang")
                           for variant in ("original", "normalized") for sha, point in expected_observations}
        require(set(index) == expected_native and len(index) == len(native), "complete original/normalized two-compiler native coverage")
        for row in native:
            process = row["process"]; mapping = mappings[row["raw_source_sha256"]]
            native_helper = study.native_helper
            for name in ("stdout", "stderr"):
                raw = process[name].encode("ascii")
                require(study.digest(raw) == process[name + "_sha256"] and len(raw) == process[name + "_bytes"], "native original stream identity")
            require(process["outcome"] == "ok" and process["returncode"] == 0 and not process["stderr"] and not process["truncated"], "native success")
            stdout = process["stdout"].encode()
            actual = (study.adapter.decode_original(stdout, mapping) if row["variant"] == "original"
                      else study.bridge.canonical_output(stdout, "numeric"))
            expected = observed[row["raw_source_sha256"], tuple(row["input"])]["value"]
            require(actual == expected == row["expected_value"] == row["value"] and row["agrees"] is True, "finite native source correspondence")
            stdin = (" ".join(map(str, row["input"])) + "\n").encode()
            if row["variant"] == "original" and mapping["original_input_channel"] == "argv": stdin = b""
            require(row["stdin_sha256"] == study.digest(stdin), "native input binding")
        compilations = json.loads((output / "compilations.json").read_text())
        compile_keys = {(r["compiler"], r["raw_source_sha256"], r["variant"]) for r in compilations}
        require(compile_keys == {(c, s, v) for c in ("gcc", "clang") for s in mappings for v in ("original", "normalized")}
                and len(compile_keys) == len(compilations), "compile coverage")
        for row in compilations:
            require(row["process"]["outcome"] == "ok" and row["process"]["returncode"] == 0 and row["binary_sha256"], "compile success")
            expected_sha = row["raw_source_sha256"] if row["variant"] == "original" else mappings[row["raw_source_sha256"]]["normalized_sha256"]
            require(row["compiled_source_sha256"] == expected_sha, "compiled raw source binding")
        identities = json.loads((output / "compilers.json").read_text())
        require({r["family"] for r in identities} == {"gcc", "clang"} and len(identities) == 2, "compiler identities")
        result = study.recompute(output)
        require(study.core.exact_equal(result, json.loads((output / "summary.json").read_text())), "summary recomputation")
        require(result["tests_pass_but_wrong"] == len(study.SELECTED), "all complete test unions passed and real violations confirmed")
    except (AssertionError, ValueError, KeyError, TypeError, IndexError, OSError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "checks": checks,
            "recomputed": result, "scope": "Offline exact-source adaptation replay, actual receiver execution, retained native-receipt verification; no fresh compiler execution in this verifier."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(); result = verify(records=args.records)
    if args.output: study.save(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != "recomputed"}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__": raise SystemExit(main())
