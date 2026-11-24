"""A finite certificate authenticates its declared domain, not its adequacy.

This source-derived controlled study varies only the receiver-owned finite
domain of the ceiling-division policy. It is not a patch-success benchmark.
Three domain axes and five candidates are registered before any observation.
The unchanged expression and the replacement correspond to the selected
upstream edit; three adverse variants are explicitly authored controls.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from admission_journal import AdmissionJournal, request_identity
from checker import Session
from proof_dag_checker import Invalid, canonical_bytes, check, evaluate_topological
from proof_dag_producer import produce
from refutation_witness_checker import check as check_compact
from refutation_witness_producer import produce as produce_compact
from upstream_ceil_case import H, M_AXIS, N_AXIS, OLD, SAFE, REFERENCE, source

VARIANTS = ("original", "supplied", "regression", "definedness", "domain-overfit")
DOMAINS = {
    "small25": {"m": [0, 1, 2, 31, 32], "n": [1, 2, 3, 7, 32]},
    "retained42": {"m": M_AXIS, "n": N_AXIS},
    "expanded4096": {
        "m": list(range(33)) + list(range(H - 30, H + 1)),
        "n": list(range(1, 33)) + list(range(H - 31, H + 1)),
    },
}
BOUND_FILES = (
    "tests/domain_adequacy_study.py", "tests/upstream_ceil_case.py",
    "src/admission_journal.py", "src/checker.py", "src/producer.py",
    "src/proof_dag_checker.py", "src/proof_dag_producer.py",
    "src/refutation_witness_checker.py", "src/refutation_witness_producer.py",
    "public-data/ceil-div-source.json",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    # Domain key order is authoritative, so requests are not sort-key encoded.
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def request(variant, domain):
    bodies = {
        "original": OLD,
        "supplied": SAFE + "return r;",
        "regression": SAFE + "if (m == 0u) { r = 1u; } else { r = r; } return r;",
        "definedness": "unsigned discarded = 1u / (n - 1u); " + SAFE + "return r;",
        "domain-overfit": SAFE + (
            "if (m == 4294967293u) { "
            "if (n == 4294967295u) { r = 0u; } else { r = r; } "
            "} else { r = r; } return r;"
        ),
    }
    return dict(
        # Keep this identifier the same across domains: the replay controls
        # then exercise domain binding rather than a different request label.
        id="ceil-domain-adequacy-" + variant, word_bits=32,
        inputs=copy.deepcopy(DOMAINS[domain]), original=source(OLD),
        candidate=source(bodies[variant]), reference=source(REFERENCE),
        repair_guard="m > (4294967295u - (n - 1u))",
    )


def observation(variant, m, n):
    """Closed mathematical functions; no parser, producer or circuit import."""
    old = ((m + n - 1) % (2**32)) // n
    ceiling = (m + n - 1) // n
    if variant == "original":
        return True, old, []
    if variant == "definedness" and n == 1:
        return False, None, []
    trace = [[0, int(m % n != 0)]]
    if variant == "regression":
        trace.append([1, int(m == 0)])
        return True, 1 if m == 0 else ceiling, trace
    if variant == "domain-overfit":
        trace.append([1, int(m == H - 2)])
        if m == H - 2:
            trace.append([2, int(n == H)])
        return True, 0 if m == H - 2 and n == H else ceiling, trace
    return True, ceiling, trace


def oracle(variant, domain):
    bad = [[], [], []]
    repair_points = 0
    for m, n in itertools.product(*DOMAINS[domain].values()):
        defined, value, trace = observation(variant, m, n)
        selected = m + n - 1 > H
        repair_points += int(selected)
        old, target = ((m + n - 1) % (2**32)) // n, (m + n - 1) // n
        truth = (
            defined,
            not selected or (defined and value == target),
            selected or (defined and value == old),
        )
        for index, holds in enumerate(truth):
            if not holds:
                bad[index].append((trace, [m, n]))
    for obligation, points in zip(("defined", "repair", "preserve"), bad):
        if points:
            trace, point = min(points)
            return dict(status="REFUTED", witness=dict(obligation=obligation, trace=trace, input=point)), repair_points
    return dict(status="ACCEPT", witness=None), repair_points


def domain_metadata():
    rows = []
    previous = None
    for name, axes in DOMAINS.items():
        for axis in axes.values():
            if axis != sorted(set(axis)) or not all(type(v) is int and 0 <= v <= H for v in axis):
                raise ValueError("registered domain axis")
        points = set(itertools.product(*axes.values()))
        if previous is not None and not previous < points:
            raise ValueError("registered domains must be strictly nested")
        previous = points
        repair = sum(m + n - 1 > H for m, n in points)
        rows.append(dict(name=name, axes=axes, points=len(points), repair_points=repair,
                         preservation_points=len(points) - repair))
    if [row["points"] for row in rows] != [25, 42, 4096]:
        raise ValueError("registered domain counts")
    return rows


def journal_domain_change(small_request, small_packet, expanded_request, expanded_packet):
    """Only the authoritative domain changes; a formerly valid approval expires."""
    with tempfile.TemporaryDirectory(prefix="repairseal-domain-journal-") as directory:
        owner = AdmissionJournal(Path(directory) / "scope.sqlite")
        try:
            registered = owner.register(small_request)
            old = owner.decide(small_request["id"], "old-proof", "proof", small_packet)
            if not old["approved"]:
                raise ValueError("registered overfit must satisfy the smaller domain")
            new = owner.register(expanded_request, registered["request_identity"])
            if old["request_identity"] == new["request_identity"]:
                raise ValueError("domain change must change request identity")
            if owner.approved(expanded_request["id"], old["request_identity"]):
                raise ValueError("stale domain approval survived")
            try:
                owner.decide(expanded_request["id"], "stale-packet", "proof", small_packet)
            except Invalid as exc:
                stale_reason = str(exc)
            else:
                raise ValueError("packet for smaller domain accepted after expansion")
            if owner.db.execute("SELECT COUNT(*) FROM receipts").fetchone()[0] != 1:
                raise ValueError("failed domain replay created a receipt")
            full = owner.decide(expanded_request["id"], "new-proof", "proof", expanded_packet)
            direct = owner.decide(expanded_request["id"], "new-direct", "direct")
            fields = ("semantic_status", "approved", "witness", "checked_cells")
            if any(full[key] != direct[key] for key in fields) or full["approved"]:
                raise ValueError("expanded journal decision mismatch")
            if owner.approved(expanded_request["id"], request_identity(expanded_request)):
                raise ValueError("expanded refutation approved")
            return dict(
                old_revision=registered["revision"], new_revision=new["revision"],
                old_status=old["semantic_status"], new_status=full["semantic_status"],
                domain_changed_identity=True, stale_approval_rejected=True,
                stale_packet_rejected=True, stale_packet_reason=stale_reason,
                failed_replay_committed_no_receipt=True, full_direct_agreement=True,
                expanded_witness=full["witness"],
            )
        finally:
            owner.close()


def run(out):
    if out.exists():
        raise ValueError("choose a new output directory")
    metadata = domain_metadata()
    bindings = {name: digest(ROOT / name) for name in BOUND_FILES}
    out.mkdir(parents=True)
    # This is an executable prospective declaration for each rerun, not a
    # claim that the research study itself was independently preregistered.
    save(out / "protocol.json", dict(
        schema="repairseal-domain-adequacy-v1", domains=metadata, variants=list(VARIANTS),
        domain_selection="Nested arithmetic-sanity, retained source-case and boundary-neighborhood grids",
        control_selection="Three authored adverse controls; domain-overfit explicitly targets one omitted point",
        request_count=15, maximum_points=4096, timing_measured=False,
        source_bindings=bindings,
    ))
    rows = []
    packets = {}
    requests = {}
    for domain in DOMAINS:
        for variant in VARIANTS:
            q = request(variant, domain)
            expected, repair_points = oracle(variant, domain)
            packet = produce(q)
            full, direct = check(q, packet), evaluate_topological(q)
            for result in (full, direct):
                if {key: result[key] for key in ("status", "witness")} != expected:
                    raise ValueError("literal/full/direct disagreement: " + variant + "/" + domain)
            if full["checked_cells"] != direct["checked_cells"]:
                raise ValueError("same-obligation work mismatch")
            # Check the independent literal formula against the source
            # interpreter at every point, including source-if diagnostics.
            session = Session(q)
            observations = []
            for m, n in itertools.product(*DOMAINS[domain].values()):
                defined, value, trace = session.run("candidate", {"m": m, "n": n})
                actual = defined, value, [list(event) for event in trace]
                if actual != observation(variant, m, n):
                    raise ValueError("literal/source observation disagreement")
                observations.append(dict(input=[m, n], defined=defined, value=value, trace=actual[2]))
            compact = None
            if expected["status"] == "REFUTED":
                compact = produce_compact(q, expected["witness"])
                point = check_compact(q, compact)
                if point["witness"] != expected["witness"]:
                    raise ValueError("compact supplied-point disagreement")
            name = domain + "-" + variant
            folder = out / name
            folder.mkdir()
            save(folder / "request.json", q)
            save(folder / "full.json", packet)
            save(folder / "observations.json", observations)
            if compact is not None:
                save(folder / "compact.json", compact)
            rows.append(dict(
                domain=domain, variant=variant, points=len(observations),
                repair_points=repair_points, preservation_points=len(observations) - repair_points,
                **expected, semantic_cells_per_full_or_direct_arm=full["checked_cells"],
                full_certificate_bytes=len(canonical_bytes(packet)),
                compact_verified=compact is not None,
            ))
            packets[(variant, domain)] = packet
            requests[(variant, domain)] = q
    replay_rows = []
    for variant in VARIANTS:
        expanded = requests[(variant, "expanded4096")]
        for smaller in ("small25", "retained42"):
            try:
                check(expanded, packets[(variant, smaller)])
            except Invalid as exc:
                replay_rows.append(dict(variant=variant, source_domain=smaller,
                                       destination_domain="expanded4096", rejected=True, reason=str(exc)))
            else:
                raise ValueError("old-domain packet accepted")
    scope_change = journal_domain_change(
        requests[("domain-overfit", "retained42")], packets[("domain-overfit", "retained42")],
        requests[("domain-overfit", "expanded4096")], packets[("domain-overfit", "expanded4096")],
    )
    for name, expected in bindings.items():
        if digest(ROOT / name) != expected:
            raise ValueError("scientific source changed during execution: " + name)
    summary = dict(
        schema="repairseal-domain-adequacy-v1", outcome="PASS", requests=len(rows),
        domains=metadata, full_direct_literal_agreements=len(rows),
        candidate_point_observations=sum(row["points"] for row in rows),
        semantic_cells_per_full_or_direct_arm=sum(row["semantic_cells_per_full_or_direct_arm"] for row in rows),
        compact_refutations=sum(row["compact_verified"] for row in rows),
        old_domain_packets_rejected=len(replay_rows), journal_domain_change=scope_change,
        source_bindings=bindings, scientific_sources_unchanged_during_run=True,
        native_execution=False, new_upstream_repairs=0,
        interpretation="Exact decisions on declared finite domains; domain selection remains receiver responsibility. Controlled examples establish no real-world frequency or whole-input repair guarantee.",
    )
    save(out / "outcomes.json", rows)
    save(out / "domain-replays.json", replay_rows)
    save(out / "summary.json", summary)
    save(out / "environment.json", dict(python=sys.version, platform=platform.platform()))
    print(json.dumps({key: value for key, value in summary.items() if key not in ("source_bindings", "domains")}, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    run(parser.parse_args().output)
