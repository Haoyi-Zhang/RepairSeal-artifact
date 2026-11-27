#!/usr/bin/env python3
"""Verify exact RepairSeal result fields and their provenance.

This checker deliberately parses named records.  It does not pass merely because
an expected number appears somewhere in a text file.  Optional fresh directories
let an evaluator bind newly generated functional, demand, and header outputs to
the same expected-result contract.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

ARTIFACT = Path(__file__).resolve().parent  # works whatever the checkout folder is named
ROOT = ARTIFACT.parent
EXPECTED_PATH = ARTIFACT / "expected-results.json"


def load(path: Path) -> Any:
    def pairs(values):
        out = {}
        for key, value in values:
            if key in out:
                raise ValueError(f"duplicate key {key!r} in {path}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError(f"non-finite JSON number {value} in {path}")))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def get(value: Any, dotted: str) -> Any:
    for token in dotted.split("."):
        value = value[int(token)] if token.isdigit() else value[token]
    return value


def equal(actual: Any, expected: Any) -> bool:
    if type(expected) is float:
        return type(actual) in (int, float) and math.isclose(
            float(actual), expected, rel_tol=1e-12, abs_tol=1e-12)
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return (actual.keys() == expected.keys()
                and all(equal(actual[key], value) for key, value in expected.items()))
    if type(expected) is list:
        return len(actual) == len(expected) and all(equal(a, e) for a, e in zip(actual, expected))
    return actual == expected


class Audit:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def check(self, name: str, actual: Any, expected: Any, source: Path,
              field: str, provenance: str) -> None:
        ok = equal(actual, expected)
        self.records.append({
            "name": name,
            "provenance": provenance,
            "source": (str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source)),
            "field": field,
            "expected": expected,
            "actual": actual,
            "status": "PASS" if ok else "FAIL",
        })

    def file_hash_inventory(self, directory: Path, summary_name: str = "summary.json") -> None:
        summary_path = directory / summary_name
        summary = load(summary_path)
        records = summary.get("records", {})
        for name, expected_hash in records.items():
            path = directory / name
            actual = sha256(path) if path.is_file() else None
            self.check(f"record-hash:{directory.name}/{name}", actual, expected_hash,
                       summary_path, f"records.{name}", "record-binding")

    @property
    def failures(self) -> list[dict[str, Any]]:
        return [row for row in self.records if row["status"] != "PASS"]


def verify_packaged(expected: dict[str, Any], audit: Audit) -> None:
    fresh = expected["fresh_current"]
    retained = expected["retained_recomputed"]

    unsigned_path = ARTIFACT / "data/unsigned-demand/summary.json"
    unsigned = load(unsigned_path)
    audit.check("complete_decision_requests", unsigned["canonical_corpus_results"],
                fresh["complete_decision_requests"], unsigned_path,
                "canonical_corpus_results", "packaged-deterministic-record")
    pruned = sum(unsigned["corpora"][name]["cells"]["pruned"] for name in ("core", "grammar"))
    demand = sum(unsigned["corpora"][name]["cells"]["demand"] for name in ("core", "grammar"))
    audit.check("pruned_live_node_semantic_values", pruned,
                fresh["pruned_live_node_semantic_values"], unsigned_path,
                "sum(corpora.*.cells.pruned)", "packaged-deterministic-record")
    audit.check("support_keyed_semantic_values", demand,
                fresh["support_keyed_semantic_values"], unsigned_path,
                "sum(corpora.*.cells.demand)", "packaged-deterministic-record")
    audit.file_hash_inventory(unsigned_path.parent)

    contract_path = ARTIFACT / "data/contract-study/summary.json"
    contract = load(contract_path)
    transport = contract["transport"]
    mappings = {
        "controlled_transport_targets": ("new_requests", fresh["controlled_transport_targets"]),
        "covered_transport_targets": ("covered_requests", fresh["covered_transport_targets"]),
        "fallback_transport_targets": ("fallback_requests", fresh["fallback_transport_targets"]),
        "covered_new_semantic_cells_per_arm": (
            "covered_new_semantic_cells_per_arm", fresh["covered_new_semantic_cells_per_arm"]),
    }
    for name, (field, value) in mappings.items():
        audit.check(name, transport[field], value, contract_path,
                    f"transport.{field}", "packaged-deterministic-record")
    audit.check("contract_same_canonical_results", contract["same_canonical_results"],
                fresh["complete_decision_requests"], contract_path,
                "same_canonical_results", "packaged-deterministic-record")
    audit.file_hash_inventory(contract_path.parent)

    witness_path = ARTIFACT / "experiments/witness-interoperability/search-statistics.json"
    witness = load(witness_path)["groups"]["all"]
    for name, field in (
        ("witness_planned_refutations", "planned_refutations"),
        ("witness_matched_confirmations", "both_confirmed"),
    ):
        audit.check(name, witness[field], retained[name], witness_path,
                    f"groups.all.{field}", "retained-output-recomputation")
    for metric, prefix in (("iterations", "witness_iterations"),
                           ("abstraction_computations", "witness_abstractions")):
        values = witness["metrics"][metric]
        audit.check(prefix + "_lower", values["input_lower"], retained[prefix + "_lower"],
                    witness_path, f"groups.all.metrics.{metric}.input_lower",
                    "retained-output-recomputation")
        audit.check(prefix + "_equal", values["equal"], retained[prefix + "_equal"],
                    witness_path, f"groups.all.metrics.{metric}.equal",
                    "retained-output-recomputation")

    coverage_path = ARTIFACT / "experiments/signed-coverage/summary.json"
    coverage = load(coverage_path)["groups"]["all"]
    coverage_fields = {
        "signed_combinations": "combinations",
        "repair_accepted": "accepted_repair",
        "coverage_authorized": "covered_accepted",
    }
    for name, field in coverage_fields.items():
        audit.check(name, coverage[field], retained[name], coverage_path,
                    f"groups.all.{field}", "retained-output-recomputation")
    audit.check("union_accepted", coverage["union_status"]["ACCEPT"],
                retained["union_accepted"], coverage_path,
                "groups.all.union_status.ACCEPT", "retained-output-recomputation")
    audit.check("repair_accept_union_refute",
                coverage["uncovered_accepted_union_status"]["REFUTED"],
                retained["repair_accept_union_refute"], coverage_path,
                "groups.all.uncovered_accepted_union_status.REFUTED",
                "retained-output-recomputation")

    receiving_path = ARTIFACT / "data/receiving-time/analysis.json"
    receiving = load(receiving_path)
    for group in ("repair", "union"):
        suffix = group
        audit.check(f"receiving_time_{suffix}_requests", receiving[group]["requests"],
                    retained[f"receiving_time_{suffix}_requests"], receiving_path,
                    f"{group}.requests", "retained-output-recomputation")
        audit.check(f"demand_slower_than_live_{suffix}",
                    receiving[group]["demand_slower_than_live"],
                    retained[f"demand_slower_than_live_{suffix}"], receiving_path,
                    f"{group}.demand_slower_than_live", "retained-output-recomputation")
        audit.check(f"median_demand_over_live_{suffix}",
                    receiving[group]["demand_over_live"]["p50"],
                    retained[f"median_demand_over_live_{suffix}"], receiving_path,
                    f"{group}.demand_over_live.p50", "retained-output-recomputation")

    overhead_path = ARTIFACT / "experiments/counter-overhead/analysis.json"
    overhead = load(overhead_path)
    for group in ("repair", "union"):
        name = f"median_uninstrumented_support_over_live_{group}"
        audit.check(name,
                    overhead[group]["ratios"]["support_uninstrumented_over_live"]["p50"],
                    retained[name], overhead_path,
                    f"{group}.ratios.support_uninstrumented_over_live.p50",
                    "retained-output-recomputation")


def verify_fresh(args: argparse.Namespace, expected: dict[str, Any], audit: Audit) -> None:
    fresh = expected["fresh_current"]
    if args.fresh_demand:
        path = args.fresh_demand / "summary.json"
        data = load(path)
        audit.check("fresh:complete_decision_requests", data["canonical_corpus_results"],
                    fresh["complete_decision_requests"], path,
                    "canonical_corpus_results", "fresh-current-execution")
        audit.check("fresh:pruned_live_node_semantic_values",
                    sum(data["corpora"][name]["cells"]["pruned"] for name in ("core", "grammar")),
                    fresh["pruned_live_node_semantic_values"], path,
                    "sum(corpora.*.cells.pruned)", "fresh-current-execution")
        audit.check("fresh:support_keyed_semantic_values",
                    sum(data["corpora"][name]["cells"]["demand"] for name in ("core", "grammar")),
                    fresh["support_keyed_semantic_values"], path,
                    "sum(corpora.*.cells.demand)", "fresh-current-execution")
        audit.file_hash_inventory(args.fresh_demand)
    if args.fresh_functional:
        path = args.fresh_functional / "complete-reproduction.json"
        data = load(path)
        audit.check("fresh:functional_core_outcome", data["core_outcome"],
                    fresh["functional_core_outcome"], path, "core_outcome",
                    "fresh-current-execution")
        for key, expected_value in (
            ("disk_requests_reloaded", 780),
            ("disk_full_certificates_validated", 380),
            ("disk_compact_certificates_validated", 285),
            ("disk_grammar_results_validated", 400),
            ("full_vector_tamper_controls", 6000),
            ("full_vector_tamper_rejections", 6000),
        ):
            audit.check(f"fresh:functional:{key}", data[key], expected_value, path,
                        key, "fresh-current-execution")
    if args.fresh_headers:
        path = args.fresh_headers / "report.json"
        data = load(path)
        for key, expected_key in (
            ("case_count", "header_cases"),
            ("compiler_count", "header_compilers"),
            ("native_compilations", "header_native_compilations"),
            ("native_executions", "header_native_executions"),
        ):
            audit.check(f"fresh:headers:{key}", data[key], fresh[expected_key], path,
                        key, "fresh-current-execution")


def verify_update(expected: dict[str, Any], audit: Audit) -> None:
    """Anchor new inventories, then compare independently recomputed fields."""
    specification = expected["review_update"]
    module_path = ARTIFACT / "verify_update_results.py"
    audit.check("update:driver-hash", sha256(module_path), expected["review_update_driver_sha256"],
                EXPECTED_PATH, "review_update_driver_sha256", "new-experiment-content-binding")
    module_spec = importlib.util.spec_from_file_location("repairseal_update_expected_contract", module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    audit.check("update:study-coverage", sorted(specification), sorted(module.STUDIES),
                EXPECTED_PATH, "review_update.keys", "new-experiment-coverage")
    for name, entry in specification.items():
        summary_path = ARTIFACT / entry["summary_file"]
        for label, path_key, hash_key in (("summary", "summary_file", "summary_sha256"),
                                        ("inventory", "inventory_file", "inventory_sha256"),
                                        ("verifier", "verifier_file", "verifier_sha256")):
            path = ARTIFACT / entry[path_key]
            audit.check(f"update:{name}:{label}-hash", sha256(path) if path.is_file() else None,
                        entry[hash_key], EXPECTED_PATH, f"review_update.{name}.{hash_key}",
                        "new-experiment-content-binding")
        try:
            result = module.recompute_study(name, ARTIFACT)
        except (AssertionError, ValueError, TypeError, KeyError, IndexError, OSError) as exc:
            result = {"status": "FAIL", "errors": [str(exc)], "recomputed": None}
        audit.check(f"update:{name}:offline-replay", result["status"], "PASS", summary_path,
                    "independent-offline-reduction.status", "new-record-recomputation")
        audit.check(f"update:{name}:offline-errors", result["errors"], [], summary_path,
                    "independent-offline-reduction.errors", "new-record-recomputation")
        for field, wanted in entry["fields"].items():
            try:
                actual = get(result["recomputed"], field)
            except (KeyError, TypeError, IndexError):
                actual = None
            audit.check(f"update:{name}:{field}", actual, wanted, summary_path, field,
                        "new-record-recomputation")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", type=Path,
                        default=ARTIFACT / "evaluation-output/latest-key-result-trace")
    result.add_argument("--fresh-demand", type=Path)
    result.add_argument("--fresh-functional", type=Path)
    result.add_argument("--fresh-headers", type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    expected = load(EXPECTED_PATH)
    audit = Audit()
    verify_packaged(expected, audit)
    verify_update(expected, audit)
    verify_fresh(args, expected, audit)
    failures = audit.failures
    result = {
        "schema": "repairseal-key-result-audit-v2",
        "status": "PASS_KEY_RESULT_SOURCE_TRACE" if not failures else "FAIL_KEY_RESULT_SOURCE_TRACE",
        "checks": len(audit.records),
        "failures": failures,
        "records": audit.records,
        "external_only": expected["external_only"],
        "interpretation": (
            "PASS binds exact named fields and record inventories. It does not convert retained-output "
            "recomputation or unavailable external campaigns into fresh execution."
        ),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": result["checks"],
                      "failures": len(failures), "result": str(args.output / 'result.json')}))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
