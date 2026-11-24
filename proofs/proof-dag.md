# Full-vector evidence and direct validation

## Objects

Let the receiver fix original program `P`, candidate `Q`, reference `T`, a semantically total repair guard `R`, ordered variables `(x1,...,xn)`, and finite sorted domains `D1,...,Dn`. The declared domain is the Cartesian product `D`. The executable prototype admits a conservative subset: the independently reconstructed guard-definedness term must simplify directly to Boolean `true`; certificate fields never determine this admission decision.

For each role and input, source execution yields definedness, a value when defined, and a source-if trace. The obligations are candidate definedness, reference agreement under `R`, and original preservation under `not R`.

The proof certificate contains a canonical typed acyclic circuit and a semantic vector for every node over the receiver-generated point order.

## Lemma 1: vector induction

Assume exact topology reconstruction and successful local checking. Induct over node ID.

- A constant vector is checked against its constant.
- An input vector is checked against the corresponding coordinate of every canonical point.
- Every compound node refers only to earlier nodes. By induction, child vectors equal their denotations. The local rule checks the parent as the declared total operator applied to those child cells.

Therefore every checked vector equals the denotation of the independently reconstructed node at every declared point.

## Lemma 2: source-to-root correspondence

Assume the independent parser and compiler implement the documented fragment semantics. Structural induction over expressions and statements gives:

- output roots equal source returned values on defined executions;
- definedness roots are true exactly when the admitted source execution is defined;
- event reach/guard roots reconstruct the source-if trace, including prefixes terminated by undefinedness.

Exact root binding prevents the producer from substituting another observation.

## Theorem: generator-independent soundness

If the checker returns `ACCEPT`, then all three obligations hold at every point in `D`, independently of how the candidate or certificate was generated.

**Argument.** Acceptance requires a completely locally valid certificate. Lemma 1 establishes every obligation-root vector cell. Lemma 2 connects those roots to the authoritative sources. The canonical point list enumerates all of `D`. Acceptance checks every obligation cell as true.

## Refutation and least witness

If a checked obligation vector contains false cells, each names a real violation. The checker chooses the first failing obligation and minimizes candidate trace then input over every false point, so the returned witness is the least under the declared total order.

## Finite format completeness

For every prototype-admitted request, a valid certificate exists: use the canonical reconstructed circuit and evaluate every node at every canonical point. Valid evidence may lead to either `ACCEPT` or `REFUTED`; evidence validity is distinct from patch correctness. This is not completeness for all mathematically total selectors: selectors whose definedness is total only through a short-circuit argument that the current simplifier cannot reduce are conservatively rejected.

## Semantic premises and evidence

The source profiles, finite domain and source observation define the theorem's
scope. Its implementation premises are source admission, reconstruction, local
semantics, strict decoding and classification. Content binding additionally
requires collision-resistant identities and the stated host environment.
Differential, native and external-verifier comparisons test those premises on
the retained populations. Semantic-cell counts and elapsed receiving times are
measured separately because the implementations incur different bookkeeping
costs.

## Named-root retention in the framed representation

The complete-JSON receiver stores the full certificate. The separate framed
representation discards a vector after its last circuit-node use,
except for distinct named roots needed by final status and trace evaluation.
If the ordinary future-child frontier has maximum width w and R such roots
are retained, semantic working storage is O(M(w+R+1)) for M domain points,
including the vector currently being checked.
At a topological cut, every retained vector belongs to the future-child set
or the processed named-root set. Those sets have at most w and R members.
Equivalently, add a final root consumer and use the resulting augmented width.
An ordinary chain has child frontier one but can retain all N cells when each
is a named output; ordinary child width alone omits this cost. This statement
applies to the framed traversal; decoding a complete JSON packet retains its
own allocation costs.

## Equal outputs and direct controls

A topological evaluator can retain each computed value and emit the same
complete record as the full-vector format. Erasing submitted-value comparisons
preserves the semantic decision because the checker obtains every expected
value from the receiver-owned circuit. This gives the complete-record control.

When the required output is the decision and least diagnostic, live-node
evaluation needs only the ancestor closure of the obligation and candidate
event roots. Projected-live evaluation computes each live node on the distinct
projections of the actual inputs onto its global support. Support-keyed demand
additionally requests children according to the same conditional local rules
and delays trace construction until the first failed obligation is known.
Its projected representatives remain actual inputs, including for a listed
point set whose coordinates are correlated.

Point-local demand retains the same root order, conditional rules and complete
diagnostic minimization while addressing each memo cell by actual input and
node. Let C_support and C_point count cold local values, L be the live ancestor
closure size and M the actual input count. Then

    C_support <= C_point <= L M.

For the upper bound, every requested node belongs to the closure and each
input/node cell is computed at most once. For the lower bound, point-local
demand checks every earlier obligation at every point, and checks the first
failed root and its traces throughout the actual domain during diagnosis.
Every representative used by support-keyed demand is among those points.
Expanding memo hits follows the same conditional rules and gives a computed
point cell for each computed support key. Distinct support keys cannot map to
one input/node cell. Dense point-local memo rows reserve O(NM) value slots in
the worst case, independently of how many slots receive computed values.

These bounds concern the defined algorithms and cold complete decisions.
The paired experiments measure the cost of implementing support reuse and
conditional access. See `refutation-boundary.md` for the separate contract in
which both compact and direct receivers are given the same violating point.
