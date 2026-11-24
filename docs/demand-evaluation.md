# Support-keyed demand evaluation

This document specifies the certificate-free evaluator in `src/demand_evaluator.py`, its exact comparison contract, and what its operation counts mean. It concerns the original unsigned Cartesian-domain request schema. The separately admitted signed-C point-set frontend has an additional admission boundary and uses actual point representatives rather than Cartesian completions.

## API and comparison contract

```python
from demand_evaluator import evaluate_demand, evaluate_projected_live

result = evaluate_demand(request)
control = evaluate_projected_live(request)
```

Both entry points use the existing receiver's request-field admission, full source reconstruction, 32-bit unsigned word semantics, obligation order and candidate event order. They return the same typed `status` and `witness` as `proof_dag_checker.check` and `domain_transport.evaluate_pruned`. The witness identifies the first failed obligation in `defined`, `repair`, `preserve` order. Within that obligation it minimizes the candidate trace first, then the complete input vector in the request's input order. This complete contract is stricter than checking only acceptance or only finding some counterexample.

`evaluate_projected_live` computes every node in the obligation-and-candidate-event dependency closure on that node's own global support projection. `evaluate_demand` additionally computes values only when requested, visits obligations in priority order, applies conditional local rules, and obtains candidate trace values only after finding the first failed obligation. Both reconstruct all authoritative sources before evaluating any obligation; unnecessary execution work does not weaken source admission.

Memo tables are private to one call. Sources and admitted axis values are snapshotted before invoking an optional counting callback. Callback exceptions propagate without returning a verdict or publishing reusable state. The implementations use an explicit evaluation stack, including for dependency chains created by many sequential source assignments.

## Global support and correct cache keys

Let `FV(v)` be the input variables occurring in reconstructed node `v`, after the existing domain-independent circuit simplifications. Constants have empty support, an input has its own variable as support, and an operator has the union of its children's supports. A vector that happens to be constant on one domain does not justify removing a variable.

Two total valuations agreeing on `FV(v)` give the same typed value at `v`. This follows by induction over the reconstructed DAG: the claim is immediate for constants and inputs, and each operator depends only on its children's values. Totalized division and shifts are covered by the same argument; source-language definedness is represented separately by Boolean nodes.

The memo key is therefore the node identity together with the ordered tuple of values on `FV(v)`. Empty support has one projected tuple, so a demanded constant contributes one cell. A hit reuses a value established earlier in this same call. The source circuit and word model remain fixed throughout that call.

For `and`, `or`, and `ite`, the evaluator requests only arguments needed by the total local operation. Source-language undefinedness is still checked through the reconstructed definedness nodes. For example, an unused executed division can make the `defined` obligation false, whereas a division behind an untaken source short circuit need not do so. Exact Boolean and integer types are checked before memo insertion.

## Universal decisions and canonical witnesses

For each obligation root, enumerate its support projection. Every full-domain input projects to one of these tuples and every projected tuple has a full-domain extension because the domain is a nonempty Cartesian product. Universal truth on the projection is therefore equivalent to universal truth on the full domain. The first root having a false value fixes the failed obligation. An accepted request needs no candidate trace for its result.

For a failed root, form the union of its support and the supports of every candidate event's reachability and guard node. Enumerate that joint projection. On failing projected inputs, reconstruct the trace in the receiver's event order, evaluating an event guard only when the event is reachable. Variables outside the joint support cannot affect either the failed predicate or the trace. Assigning their minimum admitted values gives the least full input extending that projection. Minimizing `(trace, completed input)` over all projected failures yields the exact existing witness.

The order matters. The first failing input in ordinary numeric order can have a larger trace than a later input. Likewise, dropping a variable from the truth supports does not make it irrelevant to the canonical diagnostic: it may still control a candidate event.

**Point-set boundary.** Independently filling omitted coordinates is justified here by the Cartesian domain. For a correlated finite set, such a completion can create an input that was never declared. A point-set evaluator must group the actual declared points by their projected keys and retain the least actual full point in each class. For signed points, that minimum uses signed input order, even if internal word values use two's-complement encoding.

## Work bounds and counter scope

Let `N` be the number of reconstructed nodes, `L` the size of the live obligation-and-event closure and `M` the full Cartesian product size. Let `P(v)` be the size of node `v`'s support projection, with `P(v)=1` for empty support. Define

`C_projected = sum(P(v) for v in live)`.

The full vector receiver checks exactly `N*M` local cells. The old pruned evaluator computes `L*M`. The projected-live evaluator computes exactly `C_projected`; demand evaluation computes a subset of these node/key pairs. Thus

`C_demand <= C_projected <= L*M <= N*M`.

These are semantic-cell bounds. They are not elapsed-time bounds or a claim that dictionary operations are free. The result separately reports:

- Memo queries, hits and writes, and the number of coordinates used to form memo keys.
- Support nodes, support edges and visits to child-support coordinates.
- Copied axes and axis values, projected points and coordinates filled in full-point representatives.
- Root predicate tests, conditional choices, candidate events examined, diagnostic points and candidates, and comparisons between diagnostic keys.

The implementation checks `cache_queries = semantic_cells + cache_hits`, `cache_writes = semantic_cells`, and the sum of phase-cell counts. A key-comparison count records comparison calls, not how many tuple positions Python examines within each comparison. Parsing, reconstruction, allocation, hashing implementation details and elapsed time remain additional costs. No zero counter entry means zero receiving cost.

If `R` counts root predicate tests, `B` counts failing diagnostic representatives and `E` is the number of candidate events, then the demand evaluator makes at most `R + 2*E*B + 3*C_demand` memo queries. Each semantic node has arity at most three, each event queries reachability and at most one guard, and each root predicate test makes one initial query. The separately counted key-coordinate work reflects the support sizes of these queries.

Syntactic supports can overapproximate actual semantic dependence. The method does not claim optimality: equivalent roots, symbolic reasoning or a more specialized diagnostic search may eliminate further work. A full-support workload can approach full-product costs, and fewer semantic cells do not imply shorter wall-clock time when cache and enumeration overhead dominate.

## Reproduction and fixed results

From the artifact root:

```sh
PYTHONDONTWRITEBYTECODE=1 python tests/test_demand_evaluator.py -v
PYTHONDONTWRITEBYTECODE=1 python tests/demand_comparison.py --output /tmp/repairseal-demand-new
```

The output directory must be new or empty. Scientific reproduction refuses `-O` and `-OO` before creating output. Receiver APIs remain usable under optimized Python. `--transport-source` can select an explicit directory containing the retained `transport.json` and its `requests` subdirectory; by default the driver reads `data/contract-study`.

The study freezes the exact 380 core requests, 400 grammar requests and 285 already retained transport targets, including their input order and source bytes. It checks the complete typed canonical result against the retained controls and reruns full, pruned, projected-live and demand evaluation. Source and input digests are checked again before a passing summary is written. An interrupted or failed run records `FAILED`, not a partial passing summary.

The retained protocol identifies an earlier revision of
`tests/demand_comparison.py` for which this distribution does not include an
executed-source snapshot. The retained observations can still be independently
read and a fresh current-source run can be compared against them, but exact
byte-level replay of the historical driver source is unavailable from the
supplied files. Fresh runs therefore keep their own source binding and never
replace the retained protocol.

The completed records are retained under `data/unsigned-demand`:

| Population | Requests | Full cells | Pruned cells | Projected-live cells | Demand cells |
| --- | ---: | ---: | ---: | ---: | ---: |
| Core | 380 | 1,179,684 | 934,011 | 126,999 | 50,338 |
| Grammar | 400 | 47,327,168 | 38,342,272 | 9,707,232 | 5,257,792 |
| Previously covered targets | 190 | 5,413,499 | 4,350,164 | 41,057 | 18,705 |
| Uncovered relevant-value targets | 95 | 253,611 | 203,796 | 22,986 | 16,861 |

All 780 corpus decisions and 285 target decisions agree on the complete canonical result. The shared front end means this agreement tests evaluation strategies and diagnostic reconstruction; it is not independent validation of that shared front end. The retained independent fixture/grammar controls remain relevant for that separate question.

The driver also varies one axis through sizes 1, 2, 4, 8, 16, 32 and 64 in literal fixture 01, for both the correct and overfitting candidates, and checks all 13,716 resulting points against the independently written arithmetic fixture oracle. An unused axis and a trace-only axis each leave the accepted candidate at 65 demand cells and 121 cache queries, while copied axis values increase from 10 to 73. For the refuted candidate, enlarging the trace-only axis increases demand cells from 46 to 172, cache queries from 78 to 1,023 and diagnostic projected points from 9 to 576. Diagnostic overhead is therefore visible even when its cell count is much smaller than a full-product computation.

## Interpretation of old and new evidence

The mode names identify distinct receiving algorithms. `topological-direct`
evaluates the full reconstructed DAG, `direct-pruned` evaluates every live
node at every full-domain point, `direct-projected-live` shares support
projections, and `direct-demand` computes projected values when needed.
Each retained result records the algorithm and its actual work counters.

The 190 previously covered targets were constructed from accepted bases to satisfy the coverage rule: 95 axis subsets and 95 irrelevant-axis replacements. All 95 accepted core requests have an irrelevant truth axis, whereas only 28 of the 100 accepted grammar requests do. Coverage success in the constructed targets is not a natural reuse frequency. Their cold costs must be compared with the stronger direct evaluator, which avoids much of the repeated work caused by irrelevant dimensions without using any prior history.

The vector packet has no exclusive advantage established by these counts. Its receiver recomputes every submitted cell, and a direct receiver can serialize a request binding, verdict, canonical witness and operation record after its own evaluation. A benefit attributed to evidence representation must be stated separately from a benefit of choosing a weaker direct algorithm.

## History and source-change extensions

The implementation here has no cross-request cache. A future receiver-owned cache may retain established node/key values, but uncovered keys require new evaluation. A producer-supplied value is not trusted merely because its key matches a current node.

Old universal facts cannot be combined by taking coordinatewise unions across requests. For root `x == y`, singleton domains `{(0,0)}` and `{(1,1)}` each satisfy the root; the product of the merged axis values includes the failing cross pairs `(0,1)` and `(1,0)`. A sound extension must retain coverage of complete projected tuples or unions of established rectangles.

Source changes can preserve some terms, but raw node numbers are not persistent semantic identities. Reuse would require exact typed operator/constant/input identities and recursively identified children under a fixed word model. Current candidate event ordering and reachability must still determine a new trace because inserting a statement can renumber branch sites. Competing direct and packet-based methods must receive the same prior observations, and the costs of establishing, retaining and querying those observations belong in the comparison.
