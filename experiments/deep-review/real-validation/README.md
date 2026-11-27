# Real-patch mechanisms through an exact weak-order quotient

This new study turns six known test-passing real repair failures into complete
behavior-class explanations for a narrow comparison/copy fragment. It adds
fresh native execution, an independent rejecting syntax gate, a token-based
abstract interpreter, a written quotient proof, exhaustive class outcomes,
and a receipt verifier. Existing experiment records and RepairSeal receiver
contracts are unchanged.

## Results

The four median patches (`apr-043`, `apr-046`, `apr-069`, `apr-070`) have the
same input/output behavior. They fail **exactly when `a = b > c`**, outputting
`c` where the median is `a = b`. The original programs have two bad weak-order
classes; each patch fixes one and leaves this one. The 13 named published tests
cover only 9 of the 13 possible weak-order classes, and none covers the retained
failure. The rank witness is `[1, 1, 0]`, whose expected output is `1` and whose
candidate output is `0`.

The two smallest patches (`apr-072`, `apr-073`) also share one input/output
behavior. Their edits replace one conditional with a contradiction (`c > c`
or `d < d`), making it always false. Across all 75 weak-order classes they fix
7 original failures, retain 16 failures, preserve 51 correct classes, and
introduce **one regression**. That regression is precisely `a = d < c < b`,
represented by `[0, 2, 1, 0]`: the original and the mathematical minimum output
`0`, but both candidates output `1`. The 16 named supplied tests cover 15/75
classes and cover none of the candidates' 17 failing classes. Complete
per-class witnesses and branch traces are in `records/abstract.json`.

| Unit | Result |
| --- | ---: |
| Distinct patch files / original subjects / families | 6 / 5 / 2 |
| Distinct candidate input/output behaviors | **2** |
| Fixed original/candidate/reference source identities | 13 |
| Exhaustive median / smallest weak-order classes | 13 / 75 |
| Source/order-class observations | 417 |
| Agreement with separate branch models | 417 / 417 |
| Raw/normalized computational AST correspondences | 13 / 13 |
| Frozen distinct native inputs, median / smallest | 59 / 309 |
| Distinct source/input pairs | 1,767 |
| Fresh GCC compilations | 78 |
| Fresh native process executions | 10,602 |
| Exact native/model/full-stdout agreements | 10,602 / 10,602 |
| Named supplied-test × candidate × compiler-mode checks | 252, all pass |
| Compiler families | 1: GCC |
| Compiler modes | O0, O2, UBSan at O1 |

The final run completed at 2026-11-26 19:52 UTC, equivalent to 2026-11-27 03:52
UTC+8. `records/execution.json` has exact start/end timestamps. Version output,
compiler executable hash, frozen source/domain identities, compilation
commands, binary hashes, process commands, return codes, elapsed times, full
stdout/stderr and stream hashes are retained. No fresh Clang, CBMC or
CPAchecker run is claimed.

## What is stronger here

For admitted comparison/copy computations, magnitudes do not affect control
flow beyond the relative ordering and equality of input values. The new gate
rejects arithmetic, data constants, loops, extra calls, qualifiers, alignment
attributes and other syntax that would invalidate that premise. The token
interpreter checks initialized reads and exactly one output on every class.
`proof.md` proves that all int32 tuples in one class have the same trace and
selected input-coordinate outcome under the stated I/O assumptions.

This gives exact computational failure conditions, not an extrapolation from
large test counts. It also exposes limited diversity: six distinct published
patches represent just two output behaviors. Those six patches were selected
after known failures; this study is exploratory and supplies no population
prevalence estimate. Fractions such as 17/75 count classes, not probabilities.

The practical follow-up is equally concrete. Adding `[1,1,0] -> 1` to median's
tests and `[0,2,1,0] -> 0` to smallest's tests catches all six selected patches.
These two tests are derived after examining outcomes. They are targeted
regressions, not a complete future repair test suite. A class-complete suite
would include all 13 or 75 representatives. This result reinforces that
ordinary tests can expose the defects when given the right inputs; the
contribution lies in identifying and checking the missing obligations.
The two executable input/output specifications are retained in
`derived-regression-tests.json`, bound to the exhaustive abstract outcomes.

## Files and commands

`order_types.py` is the independent syntax gate and abstract interpreter;
`run.py` freezes a new campaign, executes it, and verifies its records.
`records/protocol.json` binds exact cases, code, sources, tests, order classes,
boundary embeddings and compiler treatments before source compilation.
`records/abstract.json` retains every source/class outcome, output-coordinate
choice, trace, mathematical oracle and original-to-candidate transition.
`records/native.jsonl` contains all new process receipts.
`records/compilations.json` binds the compiler/source/binary chain, and
`records/summary.json` is reduced from those records.

From `artifact/`, replay the offline checks:

```sh
python3 -B experiments/deep-review/real-validation/run.py verify \
  --data experiments/deep-review/real-validation/records
python3 -B -m unittest tests.test_weak_order_validation -v
```

To perform a genuinely new native campaign, use a new directory:

```sh
python3 -B experiments/deep-review/real-validation/run.py run \
  --output /absolute/new-order-study --gcc /usr/bin/gcc
```

No network or external archive is required. The exact thirteen selected raw
and normalized sources are retained. Temporary compiled binaries are removed
after execution; their hashes and compilation/execution receipts remain.
The verifier checks coverage, duplicate keys, source/code identities, exact
command/stream bindings, AST correspondence, exhaustive abstract outcomes and
the derived summary. It rechecks retained receipts; it does not authenticate
their origin through a trusted timestamp service or rerun the compiler.

The final dedicated suite passes **17 tests**: twelve profile/order checks,
one complete clean verification, and four receipt-rejection controls (missing
execution, duplicate execution, a wrong output with recomputed stream hash,
and a relabelled optimization flag). Full logs are retained alongside
`offline-verification.json`.

Independent review found two generic admission gaps in the preliminary gate
(stdio macro names and C/Python string-escape differences). Both were fixed
before the final execution and have adversarial tests. `prior-run/` retains
that earlier execution with its exact source preimages. A subsequent run was
repeated only because a hash-bound positive test misspelled one result field;
`prior-test-fix-run/` retains that record and its exact test preimage. Neither
superseded run is counted in the final 10,602 executions. No old protocol hash
was rewritten to hide a change.

## Boundaries and source rights

The all-int32 claim applies to the explicitly admitted computational fragment,
with complete successful in-range decimal input and ordinary successful output.
It is not unrestricted C verification, a proof of every I/O or library behavior,
or an extension of the finite-domain acceptance claims made by RepairSeal.
The proof is written and the quotient is exhaustively executable; it is not
a mechanically checked proof assistant development. The generic token
interpreter and the existing branch models share parsing infrastructure but
do not share the receiver's semantic implementation.

Raw source bytes originate from the same published Angelix/IntroClass corpus
already distributed by the project. The authoritative source and patch
provenance remain `../../real-patches/corpus.json` and that directory's source
notices: the deposited archive's CC BY 4.0 metadata and the original IntroClass
ProgramRepair BSD 3-Clause notice retain their separate roles. Normalized
sources are explicitly adapted derivatives and their exact hashes are bound.
This study neither relicenses those files nor adds new third-party sources.
