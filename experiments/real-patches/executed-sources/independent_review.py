#!/usr/bin/env python3
"""Independent reduction of the released-patch execution records.

This reviewer imports neither the collector, the primary classifier, nor its C
interpreter.  It derives the two reference functions from their reviewed source
bytes (median of three and minimum of four), checks them against both native
compilers, and partitions the complete finite input sets using set operations.
Definedness observations are shared inputs: agreement here is independent label
reduction and native-output review, not independent human annotation or a second
proof of the C interpreter's soundness.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
COMPILERS = ("gcc", "clang")
MODES = ("plain", "ubsan")
CATEGORIES = ("definedness", "repair-region", "preservation")
REFERENCES = {
    "median": {
        "sha256": "e805c04dbe96129bc40dcd1586aa6d9d70d4284544629202a47ce9eb51b4d50f",
        "arity": 3,
        "prefix": "Please enter 3 numbers separated by spaces > ",
        "suffix": " is the median\n",
    },
    "smallest": {
        "sha256": "e80241d9eee5ef6b7ff3fc002a1866454154da3079fcb04655fbc8b00529cde7",
        "arity": 4,
        "prefix": "Please enter 4 numbers separated by spaces > ",
        "suffix": " is the smallest\n",
    },
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON member: " + str(key))
        result[key] = value
    return result


def decode(text):
    return json.loads(text, object_pairs_hook=unique_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON number: " + value)))


def exact_equal(left, right):
    """Compare JSON values without treating booleans as integer counts."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (left.keys() == right.keys() and
                all(exact_equal(left[key], right[key]) for key in left))
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_equal(a, b) for a, b in zip(left, right))
    return left == right


def read_json(path):
    return decode(Path(path).read_text(encoding="utf-8"))


def read_lines(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [decode(line) for line in stream if line.strip()]


def keyed(rows, fields, name):
    result = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        require(key not in result, "duplicate " + name + " key: " + repr(key))
        result[key] = row
    return result


def mathematical_answer(family, values):
    require(family in REFERENCES, "unreviewed reference family")
    require(len(values) == REFERENCES[family]["arity"] and
            all(type(value) is int and -(2**31) <= value < 2**31 for value in values),
            "reference input contract")
    return sorted(values)[1] if family == "median" else min(values)


def reduction(universe, original_healthy, candidate_defined, candidate_healthy):
    """Partition the input set, then count disjoint violation sets."""
    require(original_healthy <= universe and candidate_defined <= universe and
            candidate_healthy <= candidate_defined, "invalid observation sets")
    repair = universe - original_healthy
    preservation = original_healthy
    defined_wrong = candidate_defined - candidate_healthy
    violations = {
        "definedness": universe - candidate_defined,
        "repair-region": defined_wrong & repair,
        "preservation": defined_wrong & preservation,
    }
    require(not (repair & preservation) and repair | preservation == universe,
            "repair/preservation partition")
    require(len(set.union(*violations.values())) ==
            sum(len(values) for values in violations.values()), "violation partition")
    labels = [category for category in CATEGORIES if violations[category]]
    return {
        "primary": labels[0] if labels else "correct",
        "labels": labels or ["correct"],
        "repair_points": len(repair),
        "preservation_points": len(preservation),
        "violation_counts": {category: len(violations[category]) for category in CATEGORIES},
        "violation_points": {category: sorted(violations[category]) for category in CATEGORIES},
    }


def review(root=HERE):
    root = Path(root)
    paths = ["corpus.json", "points.json", "given-tests.json", "labels.json",
             "records/admission.json", "records/compiles.json",
             "records/semantics.jsonl", "records/native.jsonl"]
    corpus = read_json(root / paths[0])
    points = read_json(root / paths[1])
    tests = read_json(root / paths[2])
    primary = keyed(read_json(root / paths[3]), ("case_id",), "primary label")
    admissions = keyed(read_json(root / paths[4]), ("source_sha256",), "admission")
    builds = keyed(read_json(root / paths[5]), ("source_sha256", "compiler", "mode"), "build")
    semantic = keyed(read_lines(root / paths[6]), ("source_sha256", "point_id"), "semantic")
    native = keyed(read_lines(root / paths[7]),
                   ("source_sha256", "point_id", "compiler", "mode"), "native")
    point_index = keyed(points, ("point_id",), "input point")
    require(len(primary) == len(corpus), "primary label/corpus count")
    require({case["case_id"] for case in corpus} == {key[0] for key in primary},
            "primary label/corpus identity set")
    family_points = {family: [point for point in points if point["family"] == family]
                     for family in REFERENCES}
    source_family = {}
    for case in corpus:
        require(case["reference_sha256"] == REFERENCES[case["family"]]["sha256"],
                "reference source identity differs from independent source review")
        for role in ("original", "candidate", "reference"):
            ident = case[role + "_sha256"]
            require(ident not in source_family or source_family[ident] == case["family"],
                    "one source is assigned incompatible input families")
            source_family[ident] = case["family"]
    require({key[0] for key in admissions} == set(source_family), "source/admission closure")
    expected_builds = {(ident, compiler, mode) for ident in source_family
                       for compiler in COMPILERS for mode in MODES}
    require(set(builds) == expected_builds, "compile receipt closure")
    for row in native.values():
        require(type(row["timeout"]) is bool, "native timeout type")
        require(row["returncode"] is None or type(row["returncode"]) is int,
                "native return code type")
        for stream in ("stdout", "stderr"):
            require(type(row[stream]) is str and
                    hashlib.sha256(row[stream].encode()).hexdigest() == row[stream + "_sha256"],
                    "native output stream digest")
    expected_semantic = set()
    expected_native = set()
    compatible = {}
    defined_cross_checks = 0
    static_profile = Counter()
    macro_calls = 0
    simple_macro = re.compile(
        r'ANGELIX_OUTPUT\s*\(\s*int\s*,\s*(?:\(int\)\s*)?'
        r'[A-Za-z_][A-Za-z_0-9]*\s*,\s*"stdout"\s*\)')
    for ident, family in sorted(source_family.items()):
        source = root / "sources" / (ident + ".c")
        require(digest(source) == ident, "source bytes do not match source identity")
        raw = source.read_text(encoding="utf-8")
        static_profile["sources"] += 1
        static_profile["sources_with_multidigit_leading_zero_token"] += bool(
            re.search(r"(?<![A-Za-z0-9_])0[0-9]+", raw))
        static_profile["sources_with_shift_token"] += bool(re.search(r">>|<<", raw))
        for line in raw.splitlines():
            if "ANGELIX_OUTPUT" in line and not line.lstrip().startswith("#"):
                macro_calls += line.count("ANGELIX_OUTPUT")
                static_profile["lines_with_nonsimple_output_macro"] += bool(
                    "ANGELIX_OUTPUT" in simple_macro.sub("", line))
        admitted = admissions[(ident,)]["status"] == "admitted"
        require(admissions[(ident,)]["status"] in {"admitted", "unsupported"},
                "unrecognized source admission state")
        subset = family_points[family]
        if admitted:
            expected_semantic.update((ident, point["point_id"]) for point in subset)
        native_points = subset if admitted else [point for point in subset if point["given_tests"]]
        for compiler in COMPILERS:
            for mode in MODES:
                build = builds[(ident, compiler, mode)]
                require(type(build["returncode"]) is int, "compile return code type")
                if build["returncode"] == 0:
                    expected_native.update((ident, point["point_id"], compiler, mode)
                                           for point in native_points)
        agrees = admitted
        if admitted:
            for point in subset:
                observation = semantic.get((ident, point["point_id"]))
                require(observation is not None, "missing semantic observation")
                require(type(observation["defined"]) is bool, "definedness flag type")
                if observation["defined"]:
                    require(type(observation["returncode"]) is int and
                            type(observation["stdout"]) is str and
                            type(observation["numeric_values"]) is list and
                            all(type(value) is int for value in observation["numeric_values"]),
                            "defined observation value types")
                else:
                    require(observation["returncode"] is None and
                            observation["stdout"] is None and observation["numeric_values"] is None and
                            type(observation["undefined_reason"]) is str,
                            "undefined observation must not supply defined values")
                for compiler in COMPILERS:
                    for mode in MODES:
                        receipt = native.get((ident, point["point_id"], compiler, mode))
                        if builds[(ident, compiler, mode)]["returncode"] or receipt is None:
                            agrees = False
                        elif observation["defined"]:
                            defined_cross_checks += 1
                            agrees &= (not receipt["timeout"] and
                                       receipt["returncode"] == observation["returncode"] and
                                       receipt["stdout"] == observation["stdout"] and
                                       "runtime error:" not in receipt["stderr"])
        compatible[ident] = bool(agrees)
    require(set(semantic) == expected_semantic, "semantic receipt closure")
    require(set(native) == expected_native, "native receipt closure")
    reference_checks = 0
    for family, reference in REFERENCES.items():
        for point in family_points[family]:
            answer = mathematical_answer(family, point["values"])
            observation = semantic[(reference["sha256"], point["point_id"])]
            expected_stdout = reference["prefix"] + str(answer) + reference["suffix"]
            require(observation["defined"] and observation["numeric_values"] == [answer] and
                    observation["stdout"] == expected_stdout and observation["returncode"] == 0,
                    "teacher-reference observation disagrees with independent mathematical function")
            for compiler in COMPILERS:
                for mode in MODES:
                    receipt = native[(reference["sha256"], point["point_id"], compiler, mode)]
                    require(not receipt["timeout"] and receipt["returncode"] == 0 and
                            receipt["stdout"] == expected_stdout and not receipt["stderr"],
                            "teacher-reference native result disagrees with mathematical function")
                    reference_checks += 1
    test_points = {}
    for test in tests:
        matches = [point for point in family_points[test["family"]]
                   if point["values"] == test["input_values"]]
        require(len(matches) == 1, "given test has no unique exact input vector")
        answer = mathematical_answer(test["family"], test["input_values"])
        require(test["expected_stdout"] == str(answer) + "\n",
                "published test oracle disagrees with independent mathematical function")
        key = (test["family"], test["suite"], test["name"])
        require(key not in test_points, "duplicate published test identity")
        test_points[key] = matches[0]["point_id"]
    rows = []
    disagreements = []
    undefined_reasons = Counter()
    checked_fields = ("primary", "labels", "repair_points", "preservation_points",
                      "violation_counts", "all_given_tests_pass", "tests_pass_but_wrong")
    for case in corpus:
        family = case["family"]
        ident = case["candidate_sha256"]
        subset = family_points[family]
        universe = {point["point_id"] for point in subset}
        pass_tests = True
        for test in (test for test in tests if test["family"] == family):
            pid = test_points[(family, test["suite"], test["name"])]
            for compiler in COMPILERS:
                receipt = native.get((ident, pid, compiler, "plain"))
                pass_tests &= bool(receipt is not None and not receipt["timeout"] and
                                   receipt["returncode"] == 0 and
                                   receipt["stdout"] == test["expected_stdout"])
        if not all(compatible[case[role + "_sha256"]]
                   for role in ("original", "candidate", "reference")):
            outcome = {"primary": "other", "labels": ["other"],
                       "repair_points": 0, "preservation_points": 0,
                       "violation_counts": {category: 0 for category in CATEGORIES},
                       "violation_points": {category: [] for category in CATEGORIES}}
        else:
            healthy = {"original": set(), "candidate": set()}
            candidate_defined = set()
            for point in subset:
                pid = point["point_id"]
                expected = str(mathematical_answer(family, point["values"])) + "\n"
                for role in healthy:
                    source_id = case[role + "_sha256"]
                    observation = semantic[(source_id, pid)]
                    if observation["defined"]:
                        if role == "candidate":
                            candidate_defined.add(pid)
                        # Values for classification are independently read from both
                        # native plain executions; semantic stdout is not the oracle.
                        native_agreement = all(
                            native[(source_id, pid, compiler, "plain")]["stdout"] == expected and
                            native[(source_id, pid, compiler, "plain")]["returncode"] == 0
                            for compiler in COMPILERS)
                        if native_agreement:
                            healthy[role].add(pid)
                    elif role == "candidate":
                        undefined_reasons[observation["undefined_reason"]] += 1
            outcome = reduction(universe, healthy["original"], candidate_defined, healthy["candidate"])
        outcome.update(case_id=case["case_id"], family=family,
                       all_given_tests_pass=bool(pass_tests),
                       tests_pass_but_wrong=bool(pass_tests and outcome["primary"] not in {"correct", "other"}))
        retained = primary[(case["case_id"],)]
        mismatch = [field for field in checked_fields if not exact_equal(outcome[field], retained[field])]
        if mismatch:
            disagreements.append({"case_id": case["case_id"], "fields": mismatch,
                                  "primary": {field: retained[field] for field in mismatch},
                                  "independent": {field: outcome[field] for field in mismatch}})
        outcome["agrees_with_primary"] = not mismatch
        rows.append(outcome)
    result = {
        "schema": "repairseal-independent-real-patch-review-v1",
        "status": "PASS_INDEPENDENT_LABEL_REVIEW" if not disagreements else "FAIL_INDEPENDENT_LABEL_REVIEW",
        "method": "reviewed mathematical reference functions, complete native receipt closure, and independent set partition; no import of primary classification or interpreter",
        "shared_evidence_limit": "definedness flags are the retained closed-int32 interpretation observations; this reviewer does not claim a second independent semantic frontend or human annotations",
        "human_annotators": 0,
        "human_agreement": None,
        "reviewed_patches": len(rows),
        "agreed_patches": len(rows) - len(disagreements),
        "agreement_fraction": {"numerator": len(rows) - len(disagreements), "denominator": len(rows)},
        "disagreements": disagreements,
        "primary_counts": dict(sorted(Counter(row["primary"] for row in rows).items())),
        "nonexclusive_counts": dict(sorted(Counter(label for row in rows for label in row["labels"]).items())),
        "all_given_tests_pass": sum(row["all_given_tests_pass"] for row in rows),
        "tests_pass_but_wrong": sum(row["tests_pass_but_wrong"] for row in rows),
        "mathematical_reference_native_checks": reference_checks,
        "defined_native_correspondence_checks": defined_cross_checks,
        "native_receipts_checked": len(native),
        "semantic_receipts_shared": len(semantic),
        "static_source_survey": {**dict(static_profile), "simple_output_macro_calls": macro_calls},
        "candidate_undefined_observation_reasons": dict(sorted(undefined_reasons.items())),
        "reviewer_sha256": digest(Path(__file__)),
        "inputs": {path: digest(root / path) for path in paths},
        "rows": rows,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = review(args.root)
        target = args.root / "independent-review.json"
        if args.write:
            target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        elif target.exists():
            require(exact_equal(read_json(target), result), "retained independent review differs from recomputation")
        print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
        return bool(result["disagreements"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "FAIL_INDEPENDENT_LABEL_REVIEW", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
