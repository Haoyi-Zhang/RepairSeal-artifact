# Domain changes and receiver-owned acceptance

`src/domain_transport.py` provides two interfaces. `evaluate_pruned(request)`
computes the existing finite decision using only nodes needed by the three
obligations and the candidate's canonical trace. `AcceptanceTransport` keeps
one successfully checked acceptance in a receiver process and uses global
obligation supports to decide when it can accept a changed domain without
evaluating new semantic cells. Both return the current request identity.

The implementation is separate from the durable approval journal. A transport
result is a process-local result dictionary. It is neither a full certificate
nor a row in the journal, and the journal has no API for importing it as an
approval.

## A fresh result for a changed request

Run the following from `artifact/`, with `src/` on the Python import path:

```python
import copy
from pathlib import Path

import proof_dag_checker as core
from domain_transport import AcceptanceTransport, evaluate_pruned

request = core.load_json_strict(
    Path("results/upstream-ceil/supplied-request.json").read_text()
)
receiver = AcceptanceTransport()
basis = receiver.establish(request)  # Dependency-pruned, certificate-free check.

review = copy.deepcopy(request)
review["id"] = "ceil-reviewed-subdomain"
first_axis = next(iter(review["inputs"]))
review["inputs"][first_axis] = review["inputs"][first_axis][:1]

result = receiver.revalidate(review)
print({key: result[key] for key in
       ("status", "transported", "checked_cells", "request_identity",
        "basis_request_identity")})

independent_call = evaluate_pruned(review)
print(independent_call["status"], independent_call["checked_cells"])
```

The supplied ceiling-division request is accepted. The subdomain is covered by
the original basis, so `revalidate` returns `ACCEPT`, `transported=True`, and
`checked_cells=0`. Its `request_identity` belongs to `review`, while
`basis_request_identity` identifies the earlier checked request. The ordinary
direct call also accepts and reports its own semantic-cell count. Zero new
semantic cells in the transport call does not mean zero receiving work:
request admission, source-context comparison, axis coverage, and identity
construction still execute.

To establish a basis from a full packet, supply the packet explicitly:

```python
packet = core.load_json_strict(
    Path("results/upstream-ceil/supplied-full.json").read_text()
)
full_receiver = AcceptanceTransport()
checked = full_receiver.establish(request, packet, mode="full")
```

Full mode calls the existing independent full checker before establishing
the basis. Direct mode rejects a supplied packet. `revalidate` accepts no
packet argument; its reusable facts come only from that receiver object's
successful history.

## The coverage rule

For each obligation root, `obligation_supports` collects the free input names
of its reconstructed DAG dependencies. The existing DAG simplifications are
independent of the finite domain. These supports can contain unnecessary
variables, but every obligation is constant when its support variables are
fixed. An observed constant vector on an old domain is not used to remove a
variable.

Suppose the checked Cartesian domain is `D`, the new domain is `E`, and `S_j`
is the global support of obligation `j`. An accepted basis can establish
acceptance on `E` when all of the following hold:

1. The original, candidate, reference, and selector have identical source
   strings; the input names and their order, and the 32-bit word model, match.
2. The new request satisfies the ordinary axis and product admission bounds.
3. For every input in any `S_j`, its new axis is a subset of its old axis.

To see why this is sufficient, choose any new point and any obligation. Its
supported coordinates also occur in the old axes. Because the old domain is
a nonempty Cartesian product, there is an old point with those same supported
coordinates. That obligation is true there by the checked acceptance, and it
has the same value at the new point by support constancy. This reasoning
applies to every obligation and every new point.

An axis absent from all obligation supports may therefore gain new values.
If all three roots have empty supports, their globally constant truth values
permit any newly admitted domain with the same source context. The candidate
trace is not an acceptance obligation: a coordinate used only to choose a
trace may change without invalidating acceptance. Direct refutation still
requires the trace dependencies to choose the canonical witness.

For example, checking `x & 1u` against zero only at `x=0` observes equality but
leaves `x` in the repair obligation's global support. Adding `x=1` triggers
ordinary checking and produces a refutation. Similarly, an unused assignment
containing `1u / y` retains `y` through candidate definedness; adding zero to
that axis cannot be justified from a positive-divisor basis.

## Fallback and state behavior

`establish(request, certificate=None, mode="direct", count=None)` always
checks the supplied request. Only an `ACCEPT` result installs a basis. In
full mode, it validates the whole supplied certificate; in direct mode, it
uses dependency-pruned evaluation.

`revalidate(request, count=None)` uses the coverage rule if possible. If there
is no accepted basis, the source context differs, or a relevant axis contains
an uncovered value, it performs an ordinary dependency-pruned check. The
returned `fallback_reason` records which condition required that check.
Success can establish a new basis; a refutation leaves the earlier accepted
basis available. Invalid requests and interrupted work install no basis.

A transported acceptance keeps the original basis instead of replacing it
with a narrower queried domain. This matters when a small covered request is
followed by another request that needs values present in the original basis.
The object exposes `basis_request_identity` for observing this ownership
boundary; it exposes no basis-import or deserialization method.

Requests are copied before checking, and stored axes, source context, and
supports are immutable tuples. Calls on one receiver object are sequential.
The object has no persistent storage, cross-process sharing, or concurrent
update protocol. Create a new object in a new process and establish its basis
through a new successful check.

## Request and implementation identities

`request_identity(request)` hashes the complete request together with its
explicit input order. Domain values, source strings, request identifier, word
width, and coordinate order are bound. A changed request can therefore have
a fresh accepted result while the packet or receipt for the preceding
request remains inapplicable. `core.check(new_request, old_packet)` continues
to require the packet's exact current bindings.

`domain_transport.receiver_identity()` binds the exact trusted
`domain_transport.py` and `proof_dag_checker.py` source bytes and the Python
implementation/version. Paths are excluded. The binding is captured at
import, and these trusted modules and source files must stay fixed for the
process lifetime. A source edit conservatively changes the identity even if
the edit has no semantic effect.

The journal's identically named function has a different scope: it binds
`admission_journal.py` and the core checker. Those two implementation
identities are not interchangeable. The journal records full or full-DAG
direct checks in its own serialized SQLite transactions; it does not import
the process-local transport basis or its result dictionaries.

## Work and the matched direct comparisons

Let `N` be the number of reconstructed DAG nodes, `M` the number of declared
points, and `L` the number of nodes in the dependency closure of the three
obligation roots and all candidate trace-event predicates.

| Receiver operation | Semantic-cell work | What it establishes |
| --- | ---: | --- |
| Full-vector checking | `N × M` | Exact full-packet validation and finite semantic decision |
| Full-DAG certificate-free evaluation | `N × M` | The same finite semantic decision, without a packet |
| Dependency-pruned certificate-free evaluation | `L × M` | The same decision and canonical witness |
| Covered acceptance transport | `0` new semantic cells | Fresh acceptance for the newly admitted request |

The pruned evaluator removes nodes outside the decision/trace dependency
closure. Every retained node still evaluates every domain point. It does not
enumerate each node over a projected support domain, and it is not claimed
to be an optimal direct algorithm. `L` can equal `N`.

Both direct paths receive the same authoritative sources, domains, reference,
and selector as full checking. Full-vector checking additionally decodes and
compares the supplied values, including nodes outside the live decision
closure because those nodes belong to its exact certificate format. The
`N × M` comparison therefore describes the matched full-DAG implementation;
the dependency-pruned comparison is also needed when assessing whether
transferred full vectors save receiving work.

Semantic-cell counters exclude parsing, DAG construction, support traversal,
identity hashing, comparisons, and data structure allocation. Transport checks
every new value of each relevant axis; it also builds membership sets from
the corresponding old axes. The optional `count(category, n)` callback counts
`pruned_cells`, `proof_cells`, or `transport_axis_values` on the corresponding
paths. Raising from that callback prevents the attempted operation from
installing a new basis. Counts describe algorithmic work; measured wall time
must include the complete receiving call and its implementation/version.

## Reproduction and edge cases

The unit tests in `tests/test_domain_transport.py` exercise global versus
observed constancy, definedness of unused assignments, empty supports,
trace-only coordinates, short-circuit failure, canonical trace selection,
original-basis retention, request identity, and interrupted checking.

```sh
python3 -B -m unittest discover -s tests -p 'test_domain_transport.py' -v
```

The complete matched comparison is run by `tests/contract_comparison.py`.
Its retained observations are in `data/contract-study/`; the 285 domain-change
requests retain their new axes, coverage decisions, independent direct
results and work counts. The full project reproduction also exercises these
controls. See `reproduction.md` for the entry point and fresh-output rules.
