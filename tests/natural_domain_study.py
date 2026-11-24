"""Matched domain expansion on three fixed natural arithmetic edits.

The two Codeflaws cases use their retained ordinary test slots.  The macro case
uses an authored low-range grid because no upstream test corpus is imported.
No candidate is generated or modified by this study.  Protocol declarations are
written before receiver observations; this is not independent preregistration.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
from checker import Session
from codeflaws_cases import CASES, function
from codeflaws_source_study import ARCHIVE_BYTES, ARCHIVE_SHA, inspect, read_selected_tests, native_input
from macro_bridge import translate
from proof_dag_checker import check, evaluate_topological, canonical_bytes, exact_equal
from proof_dag_producer import produce
from refutation_witness_checker import check as check_point
from refutation_witness_producer import produce as produce_point
from scientific_driver import new_output_file
from upstream_ceil_case import REFERENCE, source

H = 2**32 - 1
TEST_METADATA = ROOT / "public-data" / "codeflaws-domain-tests.json"
OBLIGATIONS = ("defined", "repair", "preserve")
BOUND_FILES = (
    "tests/natural_domain_study.py", "tests/natural_domain_native.py",
    "tests/codeflaws_cases.py", "tests/codeflaws_source_study.py",
    "tests/upstream_ceil_case.py", "tests/scientific_driver.py",
    "src/checker.py", "src/producer.py", "src/proof_dag_checker.py",
    "src/proof_dag_producer.py", "src/refutation_witness_checker.py",
    "src/refutation_witness_producer.py", "src/macro_bridge.py",
    "public-data/codeflaws-domain-tests.json", "public-data/ceil-div-source.json",
    "public-data/codeflaws-first-300.tsv",
)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_reference(case, x):
    """Task derivations, independent of normalized-source execution."""
    if case == "4-A":
        return int(x >= 4 and x % 2 == 0)
    if case == "84-A":
        return (3 * x) // 2
    raise ValueError("unknown task")


def derive_tests(archive):
    """Fingerprint first, freeze filenames, then decode the selected payloads."""
    with tempfile.TemporaryDirectory(prefix="repairseal-domain-selection-") as temporary:
        chosen, names = inspect(archive, Path(temporary))
        rows, valid = read_selected_tests(archive, names)
    decoded = {row["test_member"]: (native_input(row["case"], raw), target)
               for row, raw, target in valid}
    for row in rows:
        if row["selection_status"] == "valid":
            x, target = decoded[row["test_member"]]
            row["scalar_input"] = x
            row["expected_matches_task_reference"] = target == task_reference(row["case"], x)
    return dict(
        schema="repairseal-codeflaws-test-domains-v1", archive_bytes=ARCHIVE_BYTES,
        archive_sha256=ARCHIVE_SHA,
        selection_rule="First eight lexical input filenames per retained case and split; invalid slots are not replaced",
        source_sha256={case: {role: identity[1] for role, identity in data["sources"].items()}
                       for case, data in CASES.items()},
        selected_names=names, rows=rows,
        payload_scope="Parsed scalar input coordinates and derived checks; no original source or test-output bytes",
    ), chosen


def validate_test_metadata(metadata):
    if metadata.get("schema") != "repairseal-codeflaws-test-domains-v1":
        raise ValueError("test metadata schema")
    if metadata.get("archive_sha256") != ARCHIVE_SHA or metadata.get("archive_bytes") != ARCHIVE_BYTES:
        raise ValueError("test archive identity")
    expected = {case: {role: identity[1] for role, identity in data["sources"].items()}
                for case, data in CASES.items()}
    if not exact_equal(metadata.get("source_sha256"), expected):
        raise ValueError("test metadata/source identities differ")
    for case in CASES:
        for split in ("repair", "heldout"):
            names = metadata["selected_names"][case][split]
            if names != sorted(set(names)) or len(names) > 8:
                raise ValueError("frozen test filename selection")
            selected = [row for row in metadata["rows"] if row["case"] == case and row["split"] == split]
            if [row["test_member"] for row in selected] != names:
                raise ValueError("selected test row coverage")
            for slot, row in enumerate(selected, 1):
                if row["slot"] != slot or row["selection_status"] not in {"valid", "invalid", "unavailable"}:
                    raise ValueError("test slot identity")
                if row["selection_status"] == "valid":
                    x = row.get("scalar_input")
                    if type(x) is not int or native_input(case, (str(x) + "\n").encode()) != x:
                        raise ValueError("test scalar input")
                    if row.get("expected_matches_task_reference") is not True:
                        raise ValueError("retained test expectation disagrees with task derivation")
                    for key in ("input_sha256", "output_sha256"):
                        value = row.get(key)
                        if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                            raise ValueError("selected payload identity")


def domain_protocol(metadata):
    """Construct domains from test membership, legal endpoints and fixed caps."""
    domains = []
    for case in CASES:
        by_split = {split: sorted({row["scalar_input"] for row in metadata["rows"]
                                  if row["case"] == case and row["split"] == split
                                  and row["selection_status"] == "valid"})
                    for split in ("repair", "heldout")}
        if any(not axis for axis in by_split.values()):
            raise ValueError("study requires nonempty retained splits; do not replace missing inputs")
        combined = sorted(set(by_split["repair"]) | set(by_split["heldout"]))
        boundary = [1, 2, 99, 100] if case == "4-A" else [2, 4, 99999998, 100000000]
        choices = [("heldout-tests", by_split["heldout"]), ("repair-tests", by_split["repair"]),
                   ("combined-tests", combined), ("test-boundary-closure", sorted(set(combined) | set(boundary)))]
        if case == "4-A":
            choices.append(("complete-legal", list(range(1, 101))))
        for name, values in choices:
            parts = [values[index:index + 64] for index in range(0, len(values), 64)]
            domains.append(dict(case=case, domain=name, axes={CASES[case]["input"]: values},
                                request_parts=[{CASES[case]["input"]: part} for part in parts],
                                distinct_points=len(values), legal_range_points=100 if case == "4-A" else 50000000,
                                complete_legal_range=case == "4-A" and name == "complete-legal"))
    low = {"m": list(range(32)), "n": list(range(1, 33))}
    expanded = {name: axis + list(range(H - 31, H + 1)) for name, axis in low.items()}
    for name, axes in (("low-range-grid", low), ("boundary-grid", expanded)):
        domains.append(dict(case="CEIL_DIV", domain=name, axes=axes, request_parts=[axes],
                            distinct_points=len(axes["m"]) * len(axes["n"]),
                            legal_range_points=(2**32) * H, complete_legal_range=False))
    for row in domains:
        if any(axis != sorted(set(axis)) for axis in row["axes"].values()):
            raise ValueError("domain order or duplicates")
        if any(len(axis) > 64 for part in row["request_parts"] for axis in part.values()):
            raise ValueError("per-request axis cap")
    return domains


def request(case, candidate, axes, part):
    if candidate not in {"original", "supplied"}:
        raise ValueError("natural source candidate only")
    if case in CASES:
        original = function(case, "buggy")
        body = function(case, "buggy" if candidate == "original" else "supplied")
        reference = function(case, "reference")
        guard = CASES[case]["guard"]
    else:
        metadata = json.loads((ROOT / "public-data/ceil-div-source.json").read_text())
        original = translate(metadata["before"]["line"], ["m", "n"])["source"]
        body = original if candidate == "original" else translate(metadata["after"]["line"], ["m", "n"])["source"]
        reference = source(REFERENCE)
        guard = "m > (4294967295u - (n - 1u))"
    return dict(id=f"natural-domain-{case}-{candidate}-part{part}", word_bits=32,
                inputs=copy.deepcopy(axes), original=original, candidate=body,
                reference=reference, repair_guard=guard)


def observation(case, role, point):
    """Literal arithmetic and normalized source-if events, without a frontend."""
    if case == "4-A":
        x, = point
        value = int(x % 2 == 0) if role == "original" else task_reference(case, x)
        return True, value, [[0, value]]
    if case == "84-A":
        x, = point
        value = x if role == "original" else task_reference(case, x)
        return True, value, []
    m, n = point
    if role == "original":
        return True, ((m + n - 1) % (2**32)) // n, []
    if role == "reference":
        return True, (m + n - 1) // n, [[0, int(m == 0)]]
    return True, (m + n - 1) // n, [[0, int(m % n != 0)]]


def selected(case, point):
    if case == "4-A": return point[0] == 2
    if case == "84-A": return True
    return point[0] + point[1] - 1 > H


def literal_rows(case, candidate, axes):
    rows = []
    for point in itertools.product(*axes.values()):
        old = observation(case, "original", point)
        got = observation(case, candidate, point)
        target = observation(case, "reference", point)
        region = selected(case, point)
        truth = [got[0], not region or (got[0] and target[0] and got[1] == target[1]),
                 region or (got[0] and old[0] and got[1] == old[1])]
        rows.append(dict(input=list(point), original=old[1], candidate=got[1], reference=target[1],
                         trace=got[2], repair_region=region, truth=truth))
    return rows


def verdict(rows):
    for index, obligation in enumerate(OBLIGATIONS):
        bad = [row for row in rows if not row["truth"][index]]
        if bad:
            first = min(bad, key=lambda row: (row["trace"], row["input"]))
            return dict(status="REFUTED", witness=dict(obligation=obligation, trace=first["trace"], input=first["input"]))
    return dict(status="ACCEPT", witness=None)


def bindings():
    return {name: digest(ROOT / name) for name in BOUND_FILES}


def run(out, archive=None, native_work=None, compilers=None):
    if out.exists() or out.is_symlink():
        raise ValueError("choose a new output directory")
    metadata = json.loads(TEST_METADATA.read_text())
    validate_test_metadata(metadata)
    chosen = None
    if archive is not None:
        actual, chosen = derive_tests(archive)
        if not exact_equal(metadata, actual):
            raise ValueError("current archive test selection differs from retained scalar metadata")
    if native_work is not None and (chosen is None or not compilers):
        raise ValueError("native execution requires the reviewed archive and explicit local compilers")
    domains = domain_protocol(metadata)
    before = bindings()
    out.mkdir(parents=True)
    protocol = dict(
        schema="repairseal-natural-domain-protocol-v1", source_bindings=before,
        source_pairs=3, candidates_per_pair=2, authored_candidates=0,
        codeflaws_selection="The same two previously selected pairs; no reselection by domain outcome",
        codeflaws_domains="Retained heldout, repair, union, then union plus first two and last two legal values",
        complete_legal_scope="Only 4-A: all 100 legal values, partitioned into 64 and 36 without omissions",
        macro_domains="First 32 legal values per axis, then first 32 plus last 32; 64-value axis and 4096-point caps determine the budget",
        macro_domain_origin="Authored arithmetic grids, not retained upstream tests or a workload sample",
        candidate_versions=["original", "supplied"], domains=domains,
        test_metadata_sha256=digest(TEST_METADATA), archive_reverified=archive is not None,
        native_requested=native_work is not None, timing_measured=False,
        inference="Domain-relative verdicts and source correspondence, not repair generation or generalization frequency",
    )
    save(out / "protocol.json", protocol)
    request_rows = []; domain_rows = []; requests = []; native_inputs = {case: set() for case in CASES}
    for domain in domains:
        case = domain["case"]
        if case in CASES:
            native_inputs[case].update(next(iter(domain["axes"].values())))
        for candidate in ("original", "supplied"):
            aggregate = []; part_names = []; cells = 0
            for index, axes in enumerate(domain["request_parts"], 1):
                q = request(case, candidate, axes, index)
                expected_rows = literal_rows(case, candidate, axes)
                expected = verdict(expected_rows)
                packet = produce(q)
                full = check(q, packet); direct = evaluate_topological(q)
                for result in (full, direct):
                    if not exact_equal({key: result[key] for key in ("status", "witness")}, expected):
                        raise ValueError("full/direct/task-derived disagreement")
                if full["checked_cells"] != direct["checked_cells"]:
                    raise ValueError("full/direct work disagreement")
                session = Session(q)
                for row in expected_rows:
                    env = dict(zip(axes, row["input"]))
                    for role, literal_role in (("original", "original"), ("candidate", candidate), ("reference", "reference")):
                        result = session.run(role, env)
                        actual = [result[0], result[1], [list(event) for event in result[2]]]
                        if not exact_equal(actual, list(observation(case, literal_role, row["input"]))):
                            raise ValueError("source interpreter/literal observation disagreement")
                name = f"{case}-{domain['domain']}-{candidate}-part{index}"
                folder = out / name; folder.mkdir()
                save(folder / "request.json", q); save(folder / "full.json", packet)
                save(folder / "observations.json", expected_rows)
                compact = None
                if expected["status"] == "REFUTED":
                    compact = produce_point(q, expected["witness"])
                    actual = check_point(q, compact)
                    if not exact_equal(actual["witness"], expected["witness"]):
                        raise ValueError("compact witness disagreement")
                    save(folder / "compact.json", compact)
                row = dict(record=name, case=case, domain=domain["domain"], candidate=candidate,
                           part=index, points=len(expected_rows), **expected,
                           full_direct_cells=full["checked_cells"], full_certificate_bytes=len(canonical_bytes(packet)),
                           compact_certificate_bytes=len(canonical_bytes(compact)) if compact else None)
                request_rows.append(row); part_names.append(name); requests.append(dict(record=name, request=q))
                aggregate.extend(expected_rows); cells += full["checked_cells"]
            if len(aggregate) != domain["distinct_points"] or len({tuple(row["input"]) for row in aggregate}) != len(aggregate):
                raise ValueError("domain partition coverage")
            domain_rows.append(dict(case=case, domain=domain["domain"], candidate=candidate,
                                    points=len(aggregate), request_records=part_names, **verdict(aggregate),
                                    repair_points=sum(row["repair_region"] for row in aggregate),
                                    violations={label: sum(not row["truth"][j] for row in aggregate) for j, label in enumerate(OBLIGATIONS)},
                                    full_direct_cells=cells, complete_legal_range=domain["complete_legal_range"]))
    save(out / "request-results.json", request_rows); save(out / "domain-results.json", domain_rows)
    save(out / "requests.json", requests)
    tests = []
    for case in CASES:
        for split in ("repair", "heldout"):
            slots = [row for row in metadata["rows"] if row["case"] == case and row["split"] == split]
            valid = [row for row in slots if row["selection_status"] == "valid"]
            for candidate in ("original", "supplied"):
                tests.append(dict(case=case, split=split, candidate=candidate, selected_slots=len(slots),
                                  valid_slots=len(valid), unique_inputs=len({row["scalar_input"] for row in valid}),
                                  matching_task_reference=sum(observation(case, candidate, [row["scalar_input"]])[1] == task_reference(case, row["scalar_input"]) for row in valid),
                                  scope="Task-derived scalar observations; raw retained tests are not executed by the offline study"))
    save(out / "test-slot-results.json", tests)
    native = None
    if native_work is not None:
        from natural_domain_native import run as run_native
        native = run_native(out, native_work, chosen, {case: sorted(axis) for case, axis in native_inputs.items()},
                            domains[-1]["axes"], compilers)
    after = bindings()
    save(out / "source-binding-check.json", dict(before=before, after=after, unchanged=exact_equal(before, after)))
    if not exact_equal(before, after):
        raise ValueError("scientific source changed during the domain study")
    summary = dict(schema="repairseal-natural-domain-summary-v1", outcome="PASS", source_pairs=3,
                   natural_candidate_versions=6, authored_candidates=0, domains=len(domains),
                   domain_verdicts=len(domain_rows), requests=len(request_rows),
                   accepted_requests=sum(row["status"] == "ACCEPT" for row in request_rows),
                   refuted_requests=sum(row["status"] == "REFUTED" for row in request_rows),
                   candidate_point_observations=sum(row["points"] for row in request_rows),
                   full_direct_semantic_cells=sum(row["full_direct_cells"] for row in request_rows),
                   compact_refutations=sum(row["status"] == "REFUTED" for row in request_rows),
                   full_direct_literal_disagreements=0, native=native,
                   source_bindings=before, archive_reverified=archive is not None,
                   scope="Same three selected edits; ordinary tests already reject both Codeflaws originals when repair and heldout splits are combined")
    save(out / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--derive-tests", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--native-work", type=Path)
    parser.add_argument("--compiler", action="append", type=Path, default=[])
    args = parser.parse_args()
    if args.derive_tests is not None:
        if args.archive is None or args.native_work is not None or args.compiler:
            parser.error("test derivation requires --archive and performs no native execution")
        output = new_output_file(args.derive_tests)
        metadata, _chosen = derive_tests(args.archive)
        validate_test_metadata(metadata); save(output, metadata)
    else:
        if args.compiler and args.native_work is None:
            parser.error("--compiler requires --native-work")
        run(args.output, args.archive, args.native_work, args.compiler)


if __name__ == "__main__":
    main()
