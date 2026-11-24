"""Compare three direct evaluators under the same canonical result contract.

The fixed population is the retained 380-request core and 400-request grammar
corpora, followed by all 285 requests already emitted by the domain-transport
study.  A separate authored axis-size control distinguishes decision support,
trace-only support, and a wholly unused coordinate.  None of these measurements
is a production hit rate or an elapsed-time speedup claim.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
from proof_dag_producer import produce
from domain_transport import evaluate_pruned, request_identity
from demand_evaluator import evaluate_demand, evaluate_projected_live
import fixture_oracle
from scientific_driver import new_output_directory, require_assertions


SOURCE_FILES = (
    ROOT / "src/proof_dag_checker.py", ROOT / "src/producer.py",
    ROOT / "src/proof_dag_producer.py", ROOT / "src/domain_transport.py",
    ROOT / "src/demand_evaluator.py", ROOT / "tests/fixture_oracle.py",
    ROOT / "tests/scientific_driver.py", Path(__file__).resolve(),
)
DEFAULT_TRANSPORT = ROOT / "data/contract-study"
AXIS_SIZES = (1, 2, 4, 8, 16, 32, 64)
DIRECT_NAMES = ("pruned", "projected_live", "demand")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def label(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def source_bindings():
    return {label(path): sha(path.read_bytes()) for path in SOURCE_FILES}


def require_same(left, right, context):
    if not core.exact_equal(left, right):
        raise AssertionError((context, left, right))


def decision(result):
    return {key: result[key] for key in ("status", "witness")}


class FrozenFiles:
    """Bind bytes before evaluation and reject changes before accepting results."""
    def __init__(self):
        self.bindings = {}
        self.paths = {}

    def read(self, path):
        path = path.resolve()
        name = label(path)
        data = path.read_bytes()
        digest = sha(data)
        if name in self.bindings:
            require_same(digest, self.bindings[name], (name, "input changed"))
        else:
            self.bindings[name] = digest
            self.paths[name] = path
        return data

    def json(self, path):
        return core.load_json_strict(self.read(path).decode("utf-8"))

    def verify(self):
        for name, path in self.paths.items():
            require_same(sha(path.read_bytes()), self.bindings[name], (name, "input changed during study"))


def unique_rows(rows, context):
    if type(rows) is not list or any(type(row) is not dict or type(row.get("id")) is not str for row in rows):
        raise AssertionError((context, "record schema"))
    indexed = {row["id"]: row for row in rows}
    require_same(len(indexed), len(rows), (context, "duplicate identifiers"))
    return indexed


def freeze_population(files, transport_source):
    retained = ROOT / "proof-data"
    population = []
    for group, directory, expected_path, certificate_directory, required_size in (
        ("core-fixture", "fixture-inputs", "fixture-cases.json", "fixture-certificates", 80),
        ("core-stress", "stress-inputs", "stress-cases.json", "stress-certificates", 300),
        ("grammar", "holdout-differential/inputs", "holdout-differential/cases.json", None, 400),
    ):
        expected = unique_rows(files.json(retained / expected_path), expected_path)
        paths = sorted((retained / directory).glob("*.json"))
        require_same(len(paths), required_size, (group, "population"))
        seen = set()
        for path in paths:
            request = files.json(path)
            identity = request_identity(request)
            identifier = request["id"]
            if identifier in seen or identifier not in expected:
                raise AssertionError((group, identifier, "unexpected identifier"))
            seen.add(identifier)
            certificate_path = retained / certificate_directory / path.name if certificate_directory else None
            if certificate_path is not None:
                files.read(certificate_path)
            population.append({"corpus": group, "request": request,
                               "request_identity": identity, "expected": decision(expected[identifier]),
                               "request_file": label(path), "certificate_path": certificate_path})
        require_same(sorted(seen), sorted(expected), (group, "expected identities"))
    old_transport = unique_rows(files.json(transport_source / "transport.json"), "transport.json")
    require_same(len(old_transport), 285, "transport population")
    require_same(dict(Counter(row["kind"] for row in old_transport.values())),
                 {"axis-subset": 95, "irrelevant-axis-replacement": 95,
                  "uncovered-relevant-value": 95}, "transport kinds")
    targets = []
    for identifier, previous in sorted(old_transport.items()):
        path = transport_source / "requests" / (identifier + ".json")
        request = files.json(path)
        require_same(request["id"], identifier, "target file identity")
        transported = previous["receipt"]["transported"]
        require_same(transported, previous["kind"] != "uncovered-relevant-value", "fixed coverage control")
        targets.append({"request": request, "request_identity": request_identity(request),
                        "request_file": label(path), "expected": decision(previous["receipt"]),
                        "basis": previous["basis"], "kind": previous["kind"],
                        "previously_covered": transported})
    require_same(len({item["basis"] for item in targets}), 95, "transport basis population")
    return population, targets


def checked_evaluations(request, certificate, expected):
    full_counts, pruned_counts = Counter(), Counter()
    def full_tick(kind, n):
        full_counts[kind] += n
    def pruned_tick(kind, n):
        pruned_counts[kind] += n
    full = core.check(request, certificate, count=full_tick)
    pruned = evaluate_pruned(request, count=pruned_tick)
    projected = evaluate_projected_live(request)
    demanded = evaluate_demand(request)
    outcomes = {"pruned": pruned, "projected_live": projected, "demand": demanded}
    require_same(decision(full), expected, (request["id"], "retained or literal control"))
    for name, result in outcomes.items():
        require_same(decision(result), decision(full), (request["id"], name, "canonical result"))
    points = math.prod(map(len, request["inputs"].values()))
    require_same(dict(full_counts), {"proof_cells": full["checked_cells"]}, "full callback cells")
    require_same(dict(pruned_counts), {"pruned_cells": pruned["checked_cells"]}, "pruned callback cells")
    require_same(full["checked_cells"], full["checked_nodes"] * points, "NM accounting")
    require_same(pruned["checked_cells"], pruned["checked_nodes"] * points, "LM accounting")
    require_same(projected["checked_cells"], projected["projected_live_cell_bound"], "projection bound attained")
    if not demanded["checked_cells"] <= projected["checked_cells"] <= pruned["checked_cells"] <= full["checked_cells"]:
        raise AssertionError((request["id"], "cell bounds"))
    for result in (projected, demanded):
        counts = result["work_counts"]
        require_same(result["checked_cells"], counts["semantic_cells"], "semantic counter")
        require_same(counts["cache_writes"], counts["semantic_cells"], "memo write counter")
        require_same(counts["cache_queries"], counts["cache_hits"] + counts["cache_writes"], "query accounting")
        require_same(sum(result["phase_cells"].values()), result["checked_cells"], "phase accounting")
        if result["status"] == "ACCEPT":
            require_same(result["work_counts"]["trace_events_examined"], 0, "acceptance diagnostic work")
            require_same(result["work_counts"]["diagnostic_points"], 0, "acceptance diagnostic points")
    return {"id": request["id"], "request_identity": request_identity(request), **decision(full),
            "input_order": list(request["inputs"]), "axis_sizes": {n: len(v) for n, v in request["inputs"].items()},
            "input_points": points, "full_nodes": full["checked_nodes"], "live_nodes": pruned["checked_nodes"],
            "full_cells": full["checked_cells"],
            "cells": {name: result["checked_cells"] for name, result in outcomes.items()},
            "demand_obligation_supports": demanded["obligation_supports"],
            "truth_irrelevant_axes": demanded["truth_irrelevant_axes"],
            "diagnostic_support": demanded["diagnostic_support"],
            "projected_live_cell_bound": demanded["projected_live_cell_bound"],
            "work_counts": {"full": dict(full_counts), "pruned": dict(pruned_counts),
                            "projected_live": projected["work_counts"], "demand": demanded["work_counts"]},
            "phase_cells": {"projected_live": projected["phase_cells"], "demand": demanded["phase_cells"]},
            "maximum_evaluation_stack_depth": demanded["maximum_evaluation_stack_depth"]}


def aggregate(rows):
    return {"requests": len(rows), "statuses": dict(Counter(row["status"] for row in rows)),
            "input_points": sum(row["input_points"] for row in rows),
            "full_cells": sum(row["full_cells"] for row in rows),
            "cells": {name: sum(row["cells"][name] for row in rows) for name in DIRECT_NAMES},
            "strictly_less_than_pruned": {name: sum(row["cells"][name] < row["cells"]["pruned"] for row in rows)
                                         for name in ("projected_live", "demand")},
            "demand_strictly_less_than_projected_live": sum(row["cells"]["demand"] < row["cells"]["projected_live"] for row in rows),
            "accepted_with_truth_irrelevant_axis": sum(row["status"] == "ACCEPT" and bool(row["truth_irrelevant_axes"]) for row in rows),
            "work_counts": {name: dict(sum((Counter(row["work_counts"][name]) for row in rows), Counter()))
                            for name in ("full", *DIRECT_NAMES)}}


def axis_controls(output):
    rows = []
    for variant in ("correct", "overfit"):
        for axis in ("t", "z"):
            for size in AXIS_SIZES:
                request = fixture_oracle.request(1, variant)
                request["id"] = f"axis-control-{variant}-{axis}-{size:02d}"
                request["inputs"][axis] = list(range(size))
                observations = [fixture_oracle.observation(1, variant, point)
                                for point in itertools.product(*request["inputs"].values())]
                witness = fixture_oracle.least_violation(observations)
                expected = {"status": "ACCEPT" if witness is None else "REFUTED", "witness": witness}
                row = checked_evaluations(request, produce(request), expected)
                row.update({"variant": variant, "axis": axis, "axis_size": size,
                            "axis_role": "wholly-unused" if axis == "t" else "trace-only",
                            "literal_oracle_points": len(observations)})
                rows.append(row)
                save(output / "axis-requests" / (request["id"] + ".json"), request)
    for variant in ("correct", "overfit"):
        unused = [row for row in rows if row["variant"] == variant and row["axis"] == "t"]
        for name in ("projected_live", "demand"):
            require_same(len({row["cells"][name] for row in unused}), 1, (variant, name, "unused axis cell invariance"))
    accepted_trace = [row for row in rows if row["variant"] == "correct" and row["axis"] == "z"]
    require_same(len({row["cells"]["demand"] for row in accepted_trace}), 1, "accepted trace axis demand cell invariance")
    rejected_trace = [row for row in rows if row["variant"] == "overfit" and row["axis"] == "z"]
    if rejected_trace[-1]["cells"]["demand"] <= rejected_trace[0]["cells"]["demand"]:
        raise AssertionError("trace-sensitive refutation control did not exercise diagnostic work")
    return rows


def run(output, transport_source=DEFAULT_TRANSPORT):
    require_assertions()
    output = new_output_directory(output)
    sources = source_bindings()
    save(output / "status.json", {"outcome": "RUNNING", "phase": "freeze-inputs"})
    try:
        files = FrozenFiles()
        population, targets = freeze_population(files, Path(transport_source).resolve())
        protocol = {
            "schema": "demand-comparison-protocol-v1", "source_bindings": sources,
            "python_implementation": platform.python_implementation(), "python_version": platform.python_version(),
            "populations": {"core": 380, "grammar": 400, "retained_transport_targets": 285, "axis_controls": 28},
            "canonical_contract": "exact typed status plus first failed obligation, then lexicographically least candidate trace and input",
            "full_control": "fresh receiver check of retained core packets or newly produced grammar/target/control packets",
            "direct_baselines": {"pruned": "all live nodes times the complete Cartesian domain",
                                 "projected_live": "all live nodes on their respective global syntactic support projections",
                                 "demand": "support-keyed demand memoization; obligation priority; conditional local rules; diagnostics only after the earliest failed obligation"},
            "counter_scope": "semantic node/key values and explicitly named logical visits/queries; parsing, reconstruction, allocation and elapsed time remain additional costs",
            "transport_scope": "cold re-evaluation of the exact retained targets, without a history advantage in any arm; the old coverage designation is a constructed control, not a measured natural hit rate",
            "axis_control": {"fixture": "literal fixture 01", "variants": ["correct", "overfit"],
                             "axes": {"t": "wholly unused by obligations and candidate trace", "z": "candidate trace only"},
                             "sizes": list(AXIS_SIZES), "values": "range(size)",
                             "other_axes": "retained three-value axes", "selection": "authored scaling control fixed before outcomes"},
            "oracle_scope": "retained independently generated core/grammar outcomes; the 28 axis controls additionally use the literal fixture arithmetic oracle on every new point",
            "performance_claim": "operation counts only; no elapsed-time speedup or optimality claim",
            "input_files": len(files.bindings), "input_manifest_sha256": sha(core.canonical_bytes(files.bindings)),
        }
        save(output / "protocol.json", protocol)
        save(output / "corpus-bindings.json", files.bindings)
        rows = []
        for index, item in enumerate(population, 1):
            request = item["request"]
            certificate = files.json(item["certificate_path"]) if item["certificate_path"] else produce(request)
            row = checked_evaluations(request, certificate, item["expected"])
            require_same(row["request_identity"], item["request_identity"], "frozen corpus identity")
            row.update({"corpus": item["corpus"], "request_file": item["request_file"]})
            rows.append(row)
            if index % 50 == 0 or index == len(population):
                print(f"canonical corpus: {index}/{len(population)}", file=sys.stderr, flush=True)
                save(output / "status.json", {"outcome": "RUNNING", "phase": "canonical-corpus", "completed": index})
        save(output / "decisions.json", rows)
        accepted_core = {row["id"] for row in rows if row["corpus"].startswith("core") and row["status"] == "ACCEPT"}
        require_same(len(accepted_core), 95, "accepted core count")
        require_same(sorted({item["basis"] for item in targets}), sorted(accepted_core), "target basis identity")
        transport_rows = []
        for index, item in enumerate(targets, 1):
            request = item["request"]
            row = checked_evaluations(request, produce(request), item["expected"])
            require_same(row["request_identity"], item["request_identity"], "frozen target identity")
            row.update({key: item[key] for key in ("request_file", "basis", "kind", "previously_covered")})
            transport_rows.append(row)
            if index % 50 == 0 or index == len(targets):
                print(f"retained targets: {index}/{len(targets)}", file=sys.stderr, flush=True)
                save(output / "status.json", {"outcome": "RUNNING", "phase": "retained-targets", "completed": index})
        save(output / "transport.json", transport_rows)
        save(output / "status.json", {"outcome": "RUNNING", "phase": "axis-controls"})
        axis_rows = axis_controls(output)
        save(output / "axis-scaling.json", axis_rows)
        files.verify()
        require_same(source_bindings(), sources, "executed sources changed during study")
        summaries = {group: aggregate([row for row in rows if row["corpus"].startswith(group)]) for group in ("core", "grammar")}
        transported = [row for row in transport_rows if row["previously_covered"]]
        uncovered = [row for row in transport_rows if not row["previously_covered"]]
        summary = {"schema": "demand-comparison-v1", "outcome": "PASS", "corpora": summaries,
                   "canonical_corpus_results": len(rows), "canonical_target_results": len(transport_rows),
                   "transport_targets": {"covered": aggregate(transported), "uncovered": aggregate(uncovered),
                                         "by_kind": {kind: aggregate([row for row in transport_rows if row["kind"] == kind]) for kind in sorted({row["kind"] for row in transport_rows})},
                                         "interpretation": "The 190 covered targets were constructed from accepted bases to satisfy coverage. Their cold costs are baseline comparisons, not natural reuse frequencies."},
                   "axis_scaling": {"requests": len(axis_rows), "literal_oracle_points": sum(row["literal_oracle_points"] for row in axis_rows),
                                    "groups": {variant + ":" + axis: [{"size": row["axis_size"], "points": row["input_points"], "full_cells": row["full_cells"], "cells": row["cells"], "demand_cache_queries": row["work_counts"]["demand"]["cache_queries"], "diagnostic_points": row["work_counts"]["demand"]["diagnostic_points"], "axis_values_copied": row["work_counts"]["demand"]["axis_values_copied"]} for row in axis_rows if row["variant"] == variant and row["axis"] == axis] for variant in ("correct", "overfit") for axis in ("t", "z")},
                                    "interpretation": "Unused coordinates increase full-product work but not projected semantic cells. Acceptance requires no candidate trace evaluation. Refutation retains trace-dependent diagnostic work; input copying and key/query work are separately counted."},
                   "records": {name: sha((output / name).read_bytes()) for name in ("protocol.json", "corpus-bindings.json", "decisions.json", "transport.json", "axis-scaling.json")}}
        save(output / "summary.json", summary)
        save(output / "status.json", {"outcome": "PASS", "summary_sha256": sha((output / "summary.json").read_bytes())})
        return summary
    except BaseException as error:
        save(output / "status.json", {"outcome": "FAILED", "error_type": type(error).__name__, "error": str(error)})
        raise


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--transport-source", type=Path, default=DEFAULT_TRANSPORT)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.transport_source), indent=2))


if __name__ == "__main__":
    main()
