"""Source-bound compact refutations for the signed exact-point profile.

The receiver rebuilds the whole admitted request, checks exact point membership,
and evaluates the typed circuit at one point. A successful check proves an
actual violation, not complete-domain acceptance or canonical leastness. Source
admission and symbolic lowering are shared with the signed vector receiver;
native/compiler and concrete-interpreter checks remain separate obligations.
"""
from __future__ import annotations

import hashlib
import re

import int32_circuit as signed
import proof_dag_checker as core

SCHEMA = "repairseal-int32-point-refutation-v1"
FIELDS = {"kind", "task_sha256", "obligation", "input", "trace",
          "certificate_sha256"}


def _digest(value):
    return hashlib.sha256(signed._canonical(value)).hexdigest()


def _validate_witness(witness, names, points):
    if type(witness) is not dict or set(witness) != {"obligation", "input", "trace"}:
        raise core.Invalid("int32 refutation witness schema")
    obligation = witness["obligation"]
    if type(obligation) is not str or obligation not in core.OBLIGATIONS:
        raise core.Invalid("int32 refutation obligation")
    point = witness["input"]
    if (type(point) is not list or len(point) != len(names)
            or any(type(value) is not int or not signed.INT_MIN <= value <= signed.INT_MAX
                   for value in point)):
        raise core.Invalid("int32 refutation input schema")
    # Exact vectors, never Cartesian membership in independent projections.
    if point not in points:
        raise core.Invalid("int32 refutation input outside exact domain")
    trace = witness["trace"]
    if type(trace) is not list or any(
        type(event) is not list or len(event) != 2
        or type(event[0]) is not int or event[0] < 0
        or type(event[1]) is not int or event[1] not in (0, 1)
        for event in trace
    ):
        raise core.Invalid("int32 refutation trace schema")


def check(task, certificate):
    """Confirm one named violation; malformed evidence raises core.Invalid."""
    circuit, programs, roots, names, _kind, _labels = signed.build_task(task)
    if type(certificate) is not dict or set(certificate) != FIELDS:
        raise core.Invalid("int32 refutation certificate schema")
    if certificate["kind"] != SCHEMA:
        raise core.Invalid("int32 refutation certificate kind")
    supplied = certificate["certificate_sha256"]
    if type(supplied) is not str or re.fullmatch(r"[0-9a-f]{64}", supplied) is None:
        raise core.Invalid("int32 refutation digest format")
    body = {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    if supplied != _digest(body):
        raise core.Invalid("int32 refutation digest")
    if certificate["task_sha256"] != signed.task_identity(task):
        raise core.Invalid("int32 refutation task binding")
    witness = {key: certificate[key] for key in ("obligation", "input", "trace")}
    _validate_witness(witness, names, task["points"])
    # Only this singleton enters semantic evaluation. Full request construction
    # and finite-domain membership are still part of receiving the certificate.
    values = [row[0] for row in signed._vectors(circuit, names, [witness["input"]])]
    root = roots[core.OBLIGATIONS.index(witness["obligation"])]
    if values[root] is not False:
        raise core.Invalid("int32 refutation claimed obligation is true")
    trace = [[site, int(bool(values[guard]))]
             for site, reachable, guard in programs["candidate"].events if values[reachable]]
    if not core.exact_equal(witness["trace"], trace):
        raise core.Invalid("int32 refutation trace mismatch")
    return {"status": "REFUTED", "witness": witness,
            "checked_nodes": len(circuit.nodes), "checked_cells": len(circuit.nodes),
            "checked_points": 1, "mode": "int32-one-point-refutation"}


def produce(task, witness=None):
    """Package a supplied violation, or search for one using the direct arm.

    Production may search the full finite domain. Its cost is separate from
    checking the resulting one-point certificate. Accepted requests have no
    refutation and are rejected by this producer.
    """
    if witness is None:
        decision = signed.evaluate_direct(task)
        if decision["status"] != "REFUTED":
            raise core.Invalid("int32 accepted task has no refutation")
        witness = decision["witness"]
    # Validate before copying, so malformed containers do not become valid JSON
    # arrays as a side effect of normalization.
    _circuit, _programs, _roots, names, _kind, _labels = signed.build_task(task)
    _validate_witness(witness, names, task["points"])
    certificate = {"kind": SCHEMA, "task_sha256": signed.task_identity(task),
                   "obligation": witness["obligation"], "input": list(witness["input"]),
                   "trace": [list(event) for event in witness["trace"]]}
    certificate["certificate_sha256"] = _digest(certificate)
    check(task, certificate)
    return certificate
