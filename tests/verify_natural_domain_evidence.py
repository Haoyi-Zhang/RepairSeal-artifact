"""Reconcile retained native observations without executing external sources."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
from codeflaws_cases import CASES
from natural_domain_study import observation, task_reference
from natural_domain_native import macro_harness
from proof_dag_checker import exact_equal, load_json_strict


def load(path):
    return load_json_strict(path.read_text(encoding="utf-8"))


def equal(expected, actual, label):
    if not exact_equal(expected, actual):
        raise ValueError(label)


def verify(directory):
    summary = load(directory / "summary.json")
    protocol = load(directory / "protocol.json")
    binding_check = load(directory / "source-binding-check.json")
    equal("PASS", summary.get("outcome"), "study did not pass")
    equal(True, summary.get("archive_reverified"), "original archive was not reverified")
    bindings = summary["source_bindings"]
    equal(bindings, protocol["source_bindings"], "protocol source identities")
    equal(dict(before=bindings, after=bindings, unchanged=True), binding_check, "source identity changed during native study")
    for name, expected in bindings.items():
        equal(expected, hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), "stale native evidence source: " + name)
    compilers = load(directory / "native-compilers.json")
    ids = [row["id"] for row in compilers]
    equal(["compiler-" + str(i + 1) for i in range(len(compilers))], ids, "compiler identity inventory")
    if not 1 <= len(ids) <= 2 or len({row["executable"] for row in compilers}) != len(ids):
        raise ValueError("compiler population")
    macro_axes = next(row["axes"] for row in protocol["domains"] if row["case"] == "CEIL_DIV" and row["domain"] == "boundary-grid")
    harness, points = macro_harness(macro_axes)
    equal(harness, (directory / "macro-native-harness.c").read_text(), "native harness differs from registered axes")
    harness_hash = hashlib.sha256(harness.encode()).hexdigest()
    for row in compilers:
        for key, expected in (("integer_model", {"__SIZEOF_INT__": 4, "__INT_MAX__": 2147483647}),
                              ("compiled_source_units", 4), ("source_compile_flags", ["-std=c11", "-O0"]),
                              ("macro_compile_flags", ["-std=c11", "-O2"]), ("macro_compile_returncode", 0),
                              ("macro_run_returncode", 0), ("macro_harness_sha256", harness_hash)):
            equal(expected, row.get(key), "compiler premise or harness receipt: " + key)
        if type(row.get("version_first_line")) is not str or not row["version_first_line"]:
            raise ValueError("compiler version receipt")
    axes = {case: set() for case in CASES}
    for row in protocol["domains"]:
        if row["case"] in CASES:
            axes[row["case"]].update(next(iter(row["axes"].values())))
    expected_keys = {(compiler, case, candidate, value) for compiler in ids
                     for case, axis in axes.items() for candidate in ("original", "supplied") for value in axis}
    native = load(directory / "codeflaws-native-observations.json")
    seen = set()
    for row in native:
        key = row["compiler"], row["case"], row["candidate"], row["input"]
        if key in seen or key not in expected_keys or type(row["input"]) is not int:
            raise ValueError("native Codeflaws observation coverage")
        seen.add(key)
        compiler, case, candidate, value = key
        expected = observation(case, candidate, [value])[1]
        source_role = "buggy" if candidate == "original" else "supplied"
        wanted = dict(compiler=compiler, case=case, candidate=candidate, input=value,
                      source_sha256=CASES[case]["sources"][source_role][1],
                      expected_model=expected, observed=expected, outcome="ok", model_agreement=True,
                      matches_task_reference=expected == task_reference(case, value))
        equal(wanted, {key: value for key, value in row.items() if key != "process_index"}, "native Codeflaws observation differs")
        if type(row.get("process_index")) is not int or row["process_index"] <= 0:
            raise ValueError("native process identity")
    if seen != expected_keys:
        raise ValueError("missing native Codeflaws observations")
    macros = load(directory / "macro-native-observations.json")
    expected_keys = {(compiler, m, n) for compiler in ids for m, n in points}; seen = set()
    for row in macros:
        m, n = row["input"]; key = row["compiler"], m, n
        if key in seen or key not in expected_keys:
            raise ValueError("macro observation coverage")
        seen.add(key)
        old = ((m + n - 1) % (2**32)) // n; new = (m + n - 1) // n
        wanted = dict(compiler=key[0], input=[m, n], old_macro=old, new_macro=new,
                      old_lowered=old, new_lowered=new, model_agreement=True)
        if any(type(x) is not int for x in row["input"]):
            raise ValueError("macro input type")
        equal(wanted, row, "macro observation differs")
    if seen != expected_keys:
        raise ValueError("missing macro observations")
    counts = dict(compilers=len(ids), distinct_external_translation_units=4,
                  compiled_external_translation_units=4 * len(ids),
                  codeflaws_distinct_inputs={case: len(axis) for case, axis in axes.items()},
                  codeflaws_process_executions=len(native), codeflaws_model_agreements=len(native),
                  macro_input_rows=len(macros), macro_scalar_observations=4 * len(macros),
                  macro_model_agreements=len(macros), native_branch_traces_measured=False,
                  upstream_application_executed=False,
                  scope="Distinct normalized legal-input executions; no raw test-payload reexecution or benchmark-wide inference")
    equal(counts, summary["native"], "native summary count or scope differs")
    equal(counts, load(directory / "native-summary.json"), "native sidecar count or scope differs")
    return dict(outcome="PASS_NATIVE_EVIDENCE_RECONCILIATION", codeflaws_rows=len(native),
                macro_rows=len(macros), external_sources_executed_by_this_check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    print(json.dumps(verify(parser.parse_args().results), indent=2))
