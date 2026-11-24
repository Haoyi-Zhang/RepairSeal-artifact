# External witness interoperability

This experiment sends CBMC's GraphML output to CPAchecker's witness validator.
The external tools receive the same checked C product and reachability property.
They decide the finite conjunction of candidate definedness, guarded repair
equality and guarded preservation equality. Neither is asked to reproduce the
receiver's least obligation, trace and input diagnostic.

## Product construction and correspondence

The input population is the existing unsigned comparison: 380 core requests,
400 grammar requests and 24 requests from the retained natural-domain study.
Selection is fixed before witness production. No case is selected because a
particular validator accepts its witness. Each case retains the complete input
request, the original three source functions and repair guard, the generated C
product, the property, all produced witnesses, each command and its outputs.

An independent `pycparser` syntax tree emits each function. Four unsigned
operations need explicit definedness checks in a reachability property. Division
and remainder call the error function when the divisor is zero; shifts call it
when the count is at least 32. The checked helper returns zero after the error
call, so the product does not introduce undefined behavior after reporting the
violation. Other expressions, assignments and branches retain their C form.
In particular, logical `&&` and `||` remain C operators, so a helper on an
unselected short-circuit branch is not evaluated. Operands of admitted
expressions have no source-level side effects. Their evaluation order therefore
cannot change whether the reachability property fails.

The product chooses unsigned inputs through the standard nondeterministic
function and returns immediately outside the declared finite domain. This is
ordinary C control flow, without a tool-specific assumption function. It calls
the candidate on every retained input, the reference under the repair guard,
and the original on its complement. The receiver admits the repair guard only
when its existing totality condition holds. A difference between the applicable
outputs calls `__VERIFIER_error`. Under the declared unsigned model, avoiding
that call is equivalent to satisfying all three Boolean repair obligations.
The repair guard uses the same checked-expression emitter as the source
functions. This preserves short-circuit behavior even when an unselected guard
operand contains division by zero or an invalid shift.

The instrumented product is a separate, disclosed transformation; the study
does not describe it as unchanged original source. For every product, GCC
compiles a native wrapper whose error function records a sticky failure flag.
Every declared finite input is executed, including inputs after the first
counterexample. The flag is compared with the conjunction of the receiver's
three obligation roots. The retained vectors give the complete point-level
comparison. The compiler command and source remain in the artifact; the
temporary shared object is removed after use.

The separate `tests/test_witness_product_semantics.py` suite exercises 25
native control programs: selected and skipped partial operations, overwritten
undefined assignments, unsigned wrap and shifts, exact domain holes, all eight
input slots, legal identifier collisions and a valid constant XOR expression.
It checks both an immediate-error executable and the sticky-flag wrapper. The
retained run contains 152 actual executable invocations and 147 wrapper point
calls; all 11 test methods pass without skips. Its source and compiler bindings,
compiler output and individual observations are retained in
`experiments/witness-product-controls/`.

## Receiving arms

| Arm | Input to CPAchecker | Purpose |
| --- | --- | --- |
| Direct | Program and property, predicate analysis | Independent Boolean check without a supplied witness |
| Raw | CBMC GraphML exactly as produced | Actual unmodified producer/consumer compatibility |
| Context | Raw graph plus required source/property metadata | Separate missing context from semantic annotations |
| Standard | Context plus explicit return-value notation adaptation | Test the portable interpretation of CBMC temporary equalities |
| Located | Standard plus source-located callee binding | Separate caller/callee ambiguity from path structure |
| Input | Producer input values in a standard violation witness | Test an explicit projection to an existential input record |
| Trivial | Same context and witness type, unrestricted one-state automaton | Check what the receiver can establish without semantic hints |

The context arm adds required graph metadata and declares missing graph keys.
Existing conflicting task metadata is an experiment error. It does not change
nodes, edges, locations, assumptions or invariants. The standard arm translates
only an exact unsigned equality of the form `return_value_FUNCTION = NUMBERu;`
into `\result == NUMBERu;` with an `assumption.resultfunction` annotation. It
keeps the source location, value and graph topology. No other expression is
deleted or replaced. In particular, an internal expression in a correctness
witness remains present even if the consumer cannot parse it.

The raw arm concerns the direct `cbmc --graphml-witness` export used by this
experiment. Its context requirements are those of this invocation; a complete
competition wrapper is a separate producer workflow.

The located arm additionally parses the generated C and identifies a unique
function call used as a declaration initializer or assignment at the reported
source line. It binds the return constraint to that callee and records each
change. Ambiguous or nested calls are left unchanged.

The input arm is a separate representation for refutations. It extracts each
concrete input value from CBMC annotations at independently parsed
nondeterministic initialization sites. Every value must belong to the
declared domain, and the exact input must refute the native product. The
standard GraphML then constrains these inputs and leaves the subsequent
execution to CPAchecker. Intra-procedural path annotations are explicitly
erased by this projection. An accepted request has no existential refutation,
so this arm is marked `NOT_APPLICABLE`, not zero time or failed validation.
If the producer provides no unique input projection, the adapter reports
`ADAPTER_UNAVAILABLE`; it does not substitute the receiver's canonical witness.

The trivial control has one entry node and an unrestricted self-loop. A
violation control also marks that state as a violation node; a correctness
control supplies no invariant. It carries no semantic constraint. This is a
receiver control, not a claim that CBMC emitted the trivial graph.

## Outcome classification and controls

For a violation witness, CPAchecker reports a successful confirmation with
`FALSE`; for a correctness witness, confirmation is `TRUE`. A run counts as a
reported `CONFIRMED` outcome only when it exits normally and has exactly one
matching terminal result. This classification does not assert that every
annotation was checked. In particular, a correctness configuration may
re-establish the program property without using supplied invariants. A `TRUE`
result from a violation validator instead means that the violation witness
was not confirmed; it is not an unrestricted safety proof. Parser/configuration errors, opposite Boolean results,
unresolved results and timeouts have separate categories. A malformed witness
is not a semantic refutation of the program.

CPAchecker warnings are retained. An output containing ignored or unknown
semantic annotation warnings is reported separately from a confirmation
without such warnings. The absence of a warning does not establish that every
annotation was essential to the result. The trivial arm is the corresponding
control for the contribution of supplied semantic information.

The first request in each population and producer-result stratum receives
three additional controls: malformed XML, a source-binding mismatch, and
contradictory annotations added to the well-formed trivial witness. The program
and property stay unchanged. The contradictory-annotation control is located at the first nondeterministic
input initialization in `main`. A false invariant is attached to its successor
state for correctness validation. For violation validation, the entry and
violation states are distinct, and the only connecting edge has a false
assumption. This avoids treating an initially marked violation state as a
negative control: such a state could already accept an empty witness path.
These controls are selected by the declared input order, not by success rates.

Each receiving arm runs once per case, with a deterministic rotation of arm
order. Process wall times include startup and are retained as execution logs.
The direct and automatic witness configurations differ, and parallel cases
share the host. These measurements do not support a matched speedup estimate.

## Reproduction

Obtain the external verifier and validator from their official distributions;
the runner does not download or install tools. The commands require a native C
compiler, `pycparser`, the receiver modules, and the inputs already in the
artifact. Invoke from the project root with an output directory that does not
exist:

```sh
python3 -B artifact/tests/witness_interoperability.py \
  --cbmc /absolute/path/to/cbmc \
  --cpachecker /absolute/path/to/bin/cpachecker \
  --gcc /absolute/path/to/gcc \
  --output /absolute/new/witness-study
```

If the chosen CBMC distribution requires an additional shared-library search
path, pass `--library-dir /absolute/path/to/cbmc/libraries`.

The optional `--limit` explicitly creates a pilot prefix, recorded in the
protocol. Omitting it selects all 804 requests. The protocol is written before
execution and binds all study modules, inputs, external executables, validator
configurations and validator libraries; completion checks that these remained
unchanged. The Python and `pycparser` distributions and external tool version
probes are retained in the experiment records. Per-case results and full logs remain available if an external tool
rejects a witness or times out. A source/product disagreement aborts the study;
the runner never changes an expected answer to match an external outcome.

After a full campaign completes, reconcile the retained records and extract
the secondary search statistics:

```sh
python3 -B artifact/tests/verify_witness_interoperability.py \
  --study /absolute/new/witness-study \
  --output /absolute/new/witness-study/verification.json
python3 -B artifact/tests/analyze_witness_search.py \
  --study /absolute/new/witness-study \
  --output /absolute/new/witness-study/search-statistics.json
python3 -B artifact/tests/witness_projection_controls.py \
  --study /absolute/new/witness-study \
  --output /absolute/new/witness-input-controls \
  --cpachecker /absolute/path/to/bin/cpachecker \
  --gcc /absolute/path/to/gcc
```

The record verifier checks the complete seven-arm inventory, exact receiving
commands, raw terminal results and warnings, retained source strings, native
point vectors, metadata-only context transformation, and the projection's
values against the raw producer graph at parsed input sites. It also checks
the three kinds of negative-control files and their selection. Every output
must be new, and optimized Python modes are rejected because they disable
assertions used in the audit.

The secondary analysis retains all 594 planned refutations. Input and trivial
witnesses must use the same receiving command and the same single started
analysis. The latter is reconstructed from the loading and starting events in
stderr; the restart summary's last-configuration field is not used as a proxy
for the active analysis. A per-metric comparison requires both witnesses to be
confirmed and exactly one statistics block from the expected component for
each run. CPA iterations, CEGAR refinements, value-analysis abstraction
computations and reached states remain separate units. The abstraction counter
belongs to `ValueAnalysisPrecisionAdjustment`; it is distinct from
`PredicateCPA`'s number of abstractions. Missing or ambiguous counters and zero
numerators or denominators are reported explicitly. The ratios characterize
these dependent workloads and do not estimate independent defect frequencies.

The final command checks three further input-consumption controls. It chooses
the first refuted request in each population, changes only the first projected
input to the smallest nonnegative value outside that input's domain, and keeps
the program, property and other input constraints. Native execution checks
that the domain-membership branch returns without reaching the error.
CPAchecker then receives the altered witness. Its expected unconfirmed result
tests whether the input constraint participates in validation, without relying
on ignored-annotation warnings alone. These three additional runs are retained
separately from the campaign's 18 controls.

## Reconciled observations

The completed study contains 804 subjects: 210 accepted and 594 refuted by
both the receiver and CBMC. Native execution agrees with the receiver on all
699,086 declared input points. The independent record audit reconciles 5,418
main CPAchecker invocations and 18 registered controls. The three additional
input-consumption controls are stored in the sibling
`experiments/witness-input-controls/` directory.

| Arm | Accepted subjects (210) | Refuted subjects (594) | Runs with an ignored-annotation warning |
| --- | --- | --- | ---: |
| Direct property analysis | 206 TRUE; 4 UNKNOWN | 593 FALSE; 1 UNKNOWN | 0 |
| Raw producer graph | 210 ERROR | 594 ERROR | 0 |
| Context metadata | 208 CONFIRMED; 2 UNKNOWN | 8 CONFIRMED; 586 UNCONFIRMED | 594 |
| Standard result notation | 207 CONFIRMED; 3 UNKNOWN | 594 UNCONFIRMED | 153 |
| Located result notation | 207 CONFIRMED; 3 UNKNOWN | 195 CONFIRMED; 399 UNCONFIRMED | 153 |
| Producer-input projection | 210 NOT_APPLICABLE | 594 CONFIRMED | 0 |
| Trivial witness | 208 CONFIRMED; 2 UNKNOWN | 593 CONFIRMED; 1 UNKNOWN | 0 |

The raw arm is the direct CBMC `--graphml-witness` export under the retained
command, rather than an SV-COMP wrapper invocation. Its errors occur at format
recognition. The context adapter makes those files recognizable, but the
receiving logs show why reported confirmation and consumption of all supplied
annotations are separate observations. General structural warnings also occur
in the input and trivial arms; absence of an ignored-annotation warning does
not mean absence of all warnings. Every definitive direct-property result
agrees with the receiver, while its five UNKNOWN outcomes remain unresolved.

All six malformed controls produce ERROR. The three foreign-source bindings
produce ERROR for violation witnesses, whereas the three correctness controls
report confirmation. Likewise, the three contradictory violation constraints
are unconfirmed, while the three false correctness invariants still accompany
reported confirmation. These observations describe the configured consumer's
property-confirmation behavior; they do not establish that every correctness
witness annotation or source-binding field was validated.

The additional input-consumption controls select original indices 1, 381 and
780. They change only the first projected input, respectively from 0 to 2,
from 1 to 2, and from 2 to 0; each replacement is outside the corresponding
declared domain. All three native executions return without reaching the error,
and all three receiving calls report TRUE for the constrained violation task,
hence an unconfirmed witness. The source, property and remaining graph content
are unchanged. Their source, input and external-tool bindings pass the final
continuity check.

The secondary counter analysis retains all 594 planned refutations. There are
593 confirmed input/trivial pairs: 285 core, 299 grammar and 9 natural. The
remaining grammar subject, index 733, has a confirmed input projection and an
UNKNOWN trivial-witness result after the internal CPU limit. Every included
pair has the same single started analysis and a unique statistics block from
the expected component. No included metric has a missing or ambiguous value,
zero numerator or zero denominator.

| Population | Confirmed pairs / planned refutations | Median input/trivial iterations | Median input/trivial value-analysis abstraction computations |
| --- | ---: | ---: | ---: |
| Core | 285 / 285 | 0.8551 | 0.7241 |
| Grammar | 299 / 300 | 0.8095 | 0.6709 |
| Natural | 9 / 9 | 1.0000 | 1.0000 |
| All | 593 / 594 | 0.8358 | 0.7069 |

For both counters in the table, 585 pairs have lower values with the input
projection, eight are equal, and none are higher. Eight of the nine natural
pairs are equal. The pooled iteration totals are 49,414 and 65,254; the pooled
value-analysis abstraction-computation totals are 53,818 and 79,179. The
reported medians are medians of per-subject ratios. These are descriptive
receiver counters under the recorded configurations, not elapsed-time
speedups or estimates of independent defect frequencies.

## Execution records and source correspondence

The original invocation completed 527 subjects before GCC treated an admitted
bitwise XOR expression as a possible exponentiation typo and stopped the native
compile gate. Its protocol, completed observations, failed compiler invocation
and exact executed sources are retained. The registered continuation changes
the native diagnostic option from `-Werror` to `-pedantic-errors`, keeping the
diagnostic text. It re-executes native correspondence for the inherited subjects
and uses that same policy for the remaining original subjects. The programs,
property, CBMC and CPAchecker commands, receiving order and resource limits
remain fixed.

A later directory-creation failure interrupted that continuation. After its
worker pool stopped, all 572 existing case directories held complete records;
no partial case directory remained. A separate resource-resume protocol binds
that checkpoint and selects the remaining 232 original indices with the same
scientific policy. The resource exception is retained separately from compiler
invocations. Its directory-creation attempts were not individually counted.

The complete record verifier checks both protocol links and source snapshots,
each inherited-file manifest, the index partitions and the native command used
for each subject. `native-reconciliation/records.json` identifies the uniform
native-policy record for every subject. Compilation-attempt counts come from
distinct retained invocation receipts, while the experiment denominator remains
804 subjects. The interrupted invocations are not relabeled as complete runs.

The product verifier compares the exact executed source snapshot with the
published runner in separate Python processes. It emits every retained request
from both implementations and requires both outputs to equal the retained
`program.c` bytes:

```sh
python3 -B artifact/tests/verify_witness_products.py \
  --study /absolute/new/witness-study \
  --output /absolute/new/witness-study/product-equivalence.json
```

This check permits source-maintenance fixes to be assessed against the actual
experimental subjects without substituting new source identities into the
original execution protocol. A completed paper build checks the independent
record audit, product correspondence, search statistics and input controls.
The retained comparison passes for all 804 products: both emitters reproduce
the same 2,104,521 C-source bytes and reconcile all 1,332 native compilation
receipts. The guard-expression maintenance change leaves this population
unchanged because its registered guards use no partial operations; the native
controls above exercise the additional guard cases explicitly.

## Primary documentation

- [CPAchecker official distribution](https://cpachecker.sosy-lab.org/download.php)
- [CPAchecker release archive](https://zenodo.org/records/24339049)
- [CPAchecker witness-validation architecture](https://www.sosy-lab.org/research/pub/2025-TACAS.CPAchecker_4.0_as_Witness_Validator.pdf)
- [GraphML witness interface and semantics](https://www.sosy-lab.org/research/pub/2022-TOSEM.Verification_Witnesses.pdf)
- [CBMC command-line reference](https://diffblue.github.io/cbmc/man/cbmc.html)
