#!/usr/bin/env python3
"""Recompute the review update from its retained source and process records.

No network, external archive, compiler, CBMC, or CPAchecker is used. Native
process receipts remain receipts; only the local semantic/certificate and
statistical reductions are rerun here. Expected numbers are checked by the
separate verify_expected_results.py contract.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
STUDIES = {
    "real_patches": "experiments/real-patches/verify.py",
    "independent_patch_review": "experiments/real-patches/independent_review.py",
    "independent_definedness_review": "experiments/real-patches/independent_definedness.py",
    "natural_expansion": "experiments/natural-expansion/verify.py",
    "introclass_certificates": "experiments/introclass-certificates/verify.py",
    "independent_normalization_review": "experiments/introclass-certificates/independent_review.py",
    "domain_scale": "experiments/natural-domains-review/analyze_scale.py",
    "fresh_census": "experiments/natural-domains-review/recollect_census.py",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location("repairseal_update_" + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def recompute_study(name, root=ROOT):
    root = Path(root)
    if name not in STUDIES:
        raise ValueError("unknown update study")
    module = load_module(name, root / STUDIES[name])
    if name == "real_patches":
        result = module.verify(root / "experiments/real-patches")
        expected_status = "PASS_REAL_PATCH_RECORDS"
    elif name == "independent_patch_review":
        result = module.review(root / "experiments/real-patches")
        retained = module.read_json(root / "experiments/real-patches/independent-review.json")
        if not module.exact_equal(result, retained):
            raise ValueError("independent patch review differs from retained record")
        return {"status": "PASS" if result["status"] == "PASS_INDEPENDENT_LABEL_REVIEW" and not result["disagreements"] else "FAIL",
                "errors": result["disagreements"], "recomputed": result}
    elif name == "independent_normalization_review":
        result = module.review(root / "experiments/introclass-certificates/records")
        retained = module.load(root / "experiments/introclass-certificates/independent-review.json")
        if not module.exact(result, retained):
            raise ValueError("independent normalization review differs from retained record")
        ok = result["status"] == "PASS_INDEPENDENT_NORMALIZATION_REVIEW"
        return {"status": "PASS" if ok else "FAIL", "errors": [] if ok else [result["status"]],
                "recomputed": result}
    elif name == "independent_definedness_review":
        result = module.review(root / "experiments/real-patches")
        retained = module.load(root / "experiments/real-patches/independent-definedness.json")
        if json.dumps(result, sort_keys=True, allow_nan=False) != json.dumps(retained, sort_keys=True, allow_nan=False):
            raise ValueError("independent definedness review differs from retained record")
        ok = result["status"] == "PASS_INDEPENDENT_DEFINEDNESS_WITNESSES"
        return {"status": "PASS" if ok else "FAIL", "errors": [] if ok else [result["status"]],
                "recomputed": result}
    elif name == "domain_scale":
        checked = module.verify(root / "experiments/natural-domains-review")
        if checked.get("outcome") != "PASS" or checked.get("errors", []) != []:
            raise ValueError("domain scale verification did not pass: " + repr(checked))
        return {"status": "PASS", "errors": [],
                "recomputed": json.loads(module.compute(root=root)["summary.json"])}
    else:
        result = module.verify(root=root)
        expected_status = "PASS"
    return {"status": "PASS" if result.get("status") == expected_status and not result.get("errors") else "FAIL",
            "errors": result.get("errors", []), "recomputed": result.get("recomputed")}


def verify(root=ROOT, studies=None):
    names = list(STUDIES) if studies is None else list(studies)
    results = {}
    errors = [] if names else ["At least one study must be selected; an empty run is not a verification."]
    for name in names:
        try:
            results[name] = recompute_study(name, root)
        except (AssertionError, ValueError, TypeError, KeyError, IndexError, OSError) as exc:
            results[name] = {"status": "FAIL", "errors": [type(exc).__name__ + ": " + str(exc)], "recomputed": None}
    return {"schema": "repairseal-review-update-offline-verification-v1",
            "status": "PASS" if not errors and all(r["status"] == "PASS" for r in results.values()) else "FAIL",
            "errors": errors,
            "studies": results,
            "scope": "Offline source/certificate/receipt reductions, never claimed as fresh external process execution."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--study", action="append", choices=sorted(STUDIES))
    args = parser.parse_args()
    result = verify(studies=args.study)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"], "errors": result["errors"], "studies": {
        name: {"status": r["status"], "errors": r["errors"]} for name, r in result["studies"].items()}}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
