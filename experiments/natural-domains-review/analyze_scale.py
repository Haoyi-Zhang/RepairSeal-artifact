"""Recompute the scope of the 4,096-point cap from retained Codeflaws records.

This is a descriptive re-analysis of the delivered census, not a fresh corpus
execution. Unknown arities are retained as unknown. A Cartesian closure of test
coordinates is only a size estimate: it may break input correlations and is not
claimed to be a task-legal or verified domain.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAP = 4096
SOURCE_FILES = (
    "data/source-programs/source-admission.json",
    "data/source-programs/normalized-corpus.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_bytes(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def bin_size(size: int) -> str:
    if size <= 64:
        return "1-64"
    if size <= 4096:
        return "65-4096"
    if size <= 1_000_000:
        return "4097-1000000"
    return "above-1000000"


def compute(root: Path = ROOT) -> dict[str, bytes]:
    admission = json.loads((root / SOURCE_FILES[0]).read_text())
    corpus = json.loads((root / SOURCE_FILES[1]).read_text())
    census_rows = []
    for row in admission["rows"]:
        admitted = row["admitted"]
        arity = row.get("input_arity") if admitted else None
        census_rows.append({
            "subject": row["subject"], "role": row["role"],
            "source_member": row["member"], "source_sha256": row["sha256"],
            "profile_admitted": admitted,
            "scalar_input_arity": "" if arity is None else arity,
            "arity_status": "verified-by-retained-profile-admission" if admitted
                            else "unavailable-outside-admitted-profile",
            "profile_rejection": "" if admitted else row["rejection"]["code"],
            "eight_values_per_coordinate_points": "" if arity is None else 8 ** arity,
            "eight_values_per_coordinate_exceeds_cap": "" if arity is None else 8 ** arity > CAP,
        })

    domains = []
    for subject in corpus["subjects"]:
        points = {tuple(test["input"]) for test in subject["tests"]}
        arity = subject["input_arity"]
        if not points or any(len(point) != arity for point in points):
            raise ValueError("invalid retained point set")
        sizes = [len({point[i] for point in points}) for i in range(arity)]
        product = math.prod(sizes)
        domains.append({
            "subject": subject["id"], "problem": subject["problem"],
            "all_defined_on_given_tests": subject["eligible"],
            "scalar_input_arity": arity,
            "given_test_occurrences": len(subject["tests"]),
            "distinct_given_test_vectors": len(points),
            "coordinate_projection_cardinalities": json.dumps(sizes, separators=(",", ":")),
            "cartesian_projection_product": product,
            "projection_product_exceeds_4096": product > CAP,
            "projection_product_bin": bin_size(product),
            "size_only_4096_point_chunk_lower_bound": math.ceil(product / CAP),
            "cartesian_task_legality": "not-established-correlations-may-be-lost",
        })

    admitted_rows = [row for row in census_rows if row["profile_admitted"]]
    eligible_domains = [row for row in domains if row["all_defined_on_given_tests"]]
    summary = {
        "schema": "repairseal-observed-domain-scale-v1",
        "outcome": "PASS",
        "data_origin": "recomputed-from-retained-delivered-census-not-fresh-execution",
        "admission_point_cap": CAP,
        "source_bindings": {name: digest(root / name) for name in SOURCE_FILES},
        "script_sha256": digest(Path(__file__)),
        "source_occurrences": len(census_rows),
        "distinct_source_sha256": len({row["source_sha256"] for row in census_rows}),
        "known_arity_occurrences": len(admitted_rows),
        "unknown_arity_occurrences": len(census_rows) - len(admitted_rows),
        "known_arity_distribution": dict(sorted(Counter(str(row["scalar_input_arity"]) for row in admitted_rows).items())),
        "eight_values_per_coordinate_exceeding_cap_occurrences": sum(row["eight_values_per_coordinate_exceeds_cap"] for row in admitted_rows),
        "complete_io_subjects": len(domains),
        "all_defined_subjects": len(eligible_domains),
        "cartesian_projection_product_above_cap": sum(row["projection_product_exceeds_4096"] for row in domains),
        "all_defined_cartesian_projection_product_above_cap": sum(row["projection_product_exceeds_4096"] for row in eligible_domains),
        "cartesian_projection_product_bins": dict(sorted(Counter(row["projection_product_bin"] for row in domains).items())),
        "all_defined_cartesian_projection_product_bins": dict(sorted(Counter(row["projection_product_bin"] for row in eligible_domains).items())),
        "minimum_retained_point_set_size": min(row["distinct_given_test_vectors"] for row in domains),
        "maximum_retained_point_set_size": max(row["distinct_given_test_vectors"] for row in domains),
        "maximum_cartesian_projection_product": max(row["cartesian_projection_product"] for row in domains),
        "scope": [
            "Every one of the 7,806 indexed source occurrences is represented; unsupported source arities are explicitly unknown.",
            "Coordinate projection cardinalities use every given repair and held-out input of each of the 100 complete-I/O subjects.",
            "The product measures Cartesian expansion of observed coordinate values only; it is not a claim that all products are legal, defined, independent, or verified.",
            "Eight values per coordinate is a declared scaling scenario, not an inferred distribution of real input domains.",
            "Repeated source hashes and same-problem subjects are dependent; no population prevalence or confidence interval is inferred.",
        ],
    }
    outputs = {
        "source-arity-census.csv": csv_bytes(census_rows),
        "test-projection-scale.csv": csv_bytes(domains),
    }
    summary["records"] = {name: hashlib.sha256(raw).hexdigest() for name, raw in outputs.items()}
    outputs["summary.json"] = (json.dumps(summary, indent=2, ensure_ascii=True) + "\n").encode()
    return outputs


def verify(output: Path) -> dict:
    wanted = compute()
    failures = [name for name, raw in wanted.items()
                if not (output / name).is_file() or (output / name).read_bytes() != raw]
    if failures:
        raise ValueError("scale record mismatch: " + ", ".join(failures))
    return {"outcome": "PASS", "verified_files": len(wanted)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        result = verify(args.output)
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, raw in compute().items():
            (args.output / name).write_bytes(raw)
        result = json.loads((args.output / "summary.json").read_text())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
