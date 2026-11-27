"""Direct evaluation and acceptance transport for receiver-owned requests.

The direct evaluator retains exactly the dependency closure needed for the
three obligations and the candidate trace.  It returns the same ordered
diagnostic as the full-DAG evaluator; it is not claimed to be an optimal
interpreter.

AcceptanceTransport is a sequential, process-local receiver object.  Its basis
is created only by a successful check in this process, never deserialized from
producer data.  Source bytes, input order and the word model must stay fixed.
The receiver derives global supports from its DAG, not from observations on
the old domain.  It may then issue a fresh acceptance for a new Cartesian
domain whose relevant axes are covered by the old domain.  Refutations and
producer packets are never transported.  The process must keep these trusted
modules and their source files fixed after import.
"""
from __future__ import annotations

import copy
import hashlib
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import proof_dag_checker as core


def _implementation_identity() -> str:
    files = (Path(core.__file__), Path(__file__))
    body = {
        "schema": "repairseal-domain-transport-implementation-v1",
        "sources": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in files},
        "python_implementation": platform.python_implementation(),
        "python_version": list(sys.version_info),
    }
    return hashlib.sha256(core.canonical_bytes(body)).hexdigest()


_IMPLEMENTATION_IDENTITY = _implementation_identity()


def receiver_identity() -> str:
    """Identity of this fixed receiver implementation, independent of paths."""
    return _IMPLEMENTATION_IDENTITY


def request_identity(request: dict) -> str:
    """Bind request bytes/values and the order of its input coordinates."""
    _domains, names = core.validate_request_fields(request)
    return hashlib.sha256(core.canonical_bytes(
        {"request": request, "input_order": names})).hexdigest()


def _children(key):
    return () if key[0] in {"b", "u", "input"} else key[1:]


def live_nodes(circuit, roots, events) -> tuple[int, ...]:
    """Dependency closure for decisions and candidate trace tie breaking."""
    pending = list(roots)
    for _site, reachable, guard in events:
        pending.extend((reachable, guard))
    live = set()
    while pending:
        index = pending.pop()
        if index not in live:
            live.add(index)
            pending.extend(_children(circuit.nodes[index]))
    return tuple(sorted(live))


def obligation_supports(circuit, roots) -> tuple[tuple[str, ...], ...]:
    """Sound global supports after domain-independent DAG simplification.

    Free-variable sets can overapproximate semantic support.  No constant
    vector or equality observed only on a requested domain is used here.
    """
    supports = []
    for key in circuit.nodes:
        if key[0] == "input":
            support = frozenset((key[1],))
        elif key[0] in {"b", "u"}:
            support = frozenset()
        else:
            support = frozenset().union(*(supports[ch] for ch in key[1:]))
        supports.append(support)
    return tuple(tuple(sorted(supports[root])) for root in roots)


def evaluate_pruned(request: dict,
                    count: Callable[[str, int], None] | None = None) -> dict:
    """Evaluate only nodes needed for the existing canonical result."""
    tick = count or (lambda _kind, _n=1: None)
    _domains, names, points = core.validate_request(request)
    circuit, programs, _guard, roots = core.build_expected(request)
    active = live_nodes(circuit, roots, programs["candidate"].events)
    positions = {name: i for i, name in enumerate(names)}
    vectors = [None] * len(circuit.nodes)
    for index in active:
        key = circuit.nodes[index]
        op = key[0]
        vector = []
        for cell, point in enumerate(points):
            tick("pruned_cells", 1)
            if op in {"b", "u"}:
                value = key[1]
            elif op == "input":
                value = point[positions[key[1]]]
            else:
                value = core.local_value(op, tuple(vectors[ch][cell]
                                                  for ch in key[1:]))
            vector.append(value)
        vectors[index] = vector
    result = core.classify_vectors(points, roots,
                                   programs["candidate"].events, vectors)
    result.update({"constructed_nodes": len(circuit.nodes),
                   "checked_nodes": len(active),
                   "checked_cells": len(active) * len(points),
                   "mode": "direct-pruned"})
    return result


def _context(request: dict) -> tuple:
    return (request["word_bits"], tuple(request["inputs"]),
            *(request[role] for role in core.ROLES), request["repair_guard"])


@dataclass(frozen=True)
class _Basis:
    context: tuple
    axes: tuple[tuple[str, tuple[int, ...]], ...]
    supports: tuple[tuple[str, ...], ...]
    request_identity: str
    receiver_identity: str


class AcceptanceTransport:
    """Keep one checked acceptance basis in a trusted sequential receiver.

    Changing sources or adding an uncovered relevant value triggers an ordinary
    dependency-pruned check.  An invalid or interrupted call commits no basis.
    A refutation leaves the previous accepted basis available for later calls.
    Transported acceptances retain the original basis instead of weakening it
    to the most recently requested subdomain.
    """

    def __init__(self):
        self._basis: _Basis | None = None

    @property
    def receiver_identity(self) -> str:
        return _IMPLEMENTATION_IDENTITY

    @property
    def basis_request_identity(self) -> str | None:
        return None if self._basis is None else self._basis.request_identity

    def _finish_checked(self, request: dict, result: dict) -> dict:
        identity = request_identity(request)
        basis = None
        if result["status"] == "ACCEPT":
            circuit, _programs, _guard, roots = core.build_expected(request)
            basis = _Basis(
                context=_context(request),
                axes=tuple((name, tuple(values))
                           for name, values in request["inputs"].items()),
                supports=obligation_supports(circuit, roots),
                request_identity=identity,
                receiver_identity=self.receiver_identity,
            )
        receipt = dict(result)
        receipt.update({"request_identity": identity,
                        "receiver_identity": self.receiver_identity,
                        "transported": False,
                        "basis_request_identity": identity if basis else None})
        if basis is not None:
            self._basis = basis
        return receipt

    def establish(self, request: dict, certificate=None, *, mode="direct",
                  count: Callable[[str, int], None] | None = None) -> dict:
        """Check a new basis; full mode always checks the supplied packet."""
        if mode not in {"direct", "full"}:
            raise core.Invalid("acceptance basis mode")
        snapshot = copy.deepcopy(request)
        if mode == "full":
            result = core.check(snapshot, certificate, count=count)
        else:
            if certificate is not None:
                raise core.Invalid("direct basis does not consume a packet")
            result = evaluate_pruned(snapshot, count=count)
        return self._finish_checked(snapshot, result)

    def revalidate(self, request: dict, *,
                   count: Callable[[str, int], None] | None = None) -> dict:
        """Issue a fresh result for a request, using only owned checked history."""
        snapshot = copy.deepcopy(request)
        domains, names = core.validate_request_fields(snapshot)
        tick = count or (lambda _kind, _n=1: None)
        basis = self._basis
        reason = "no-accepted-basis"
        if basis is not None:
            if (basis.receiver_identity != self.receiver_identity or
                    basis.context != _context(snapshot)):
                reason = "context-changed"
            else:
                covered = True
                old_axes = dict(basis.axes)
                relevant = frozenset().union(*map(frozenset, basis.supports))
                for name in names:
                    if name in relevant:
                        old_values = frozenset(old_axes[name])
                        for value in domains[name]:
                            tick("transport_axis_values", 1)
                            if value not in old_values:
                                covered = False
                if covered:
                    return {
                        "status": "ACCEPT", "witness": None,
                        "checked_nodes": 0, "checked_cells": 0,
                        "mode": "support-transport", "transported": True,
                        "request_identity": request_identity(snapshot),
                        "receiver_identity": self.receiver_identity,
                        "basis_request_identity": basis.request_identity,
                        "obligation_supports": [list(s) for s in basis.supports],
                        "relevant_inputs": [n for n in names if n in relevant],
                    }
                reason = "uncovered-relevant-value"
        result = evaluate_pruned(snapshot, count=count)
        result["fallback_reason"] = reason
        return self._finish_checked(snapshot, result)
