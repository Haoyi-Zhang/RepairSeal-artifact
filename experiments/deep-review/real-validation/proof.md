# Exact weak-order analysis for comparison/copy programs

## Claim and scope

This is an additional analysis of thirteen fixed computational fragments. It
does **not** change RepairSeal's existing finite request domains, acceptance
rules, canonical diagnostic order, or certificate formats. The analysis has a
written mathematical proof and an executable, exhaustive quotient checker; it
is not a proof mechanized in a theorem prover.

For a program admitted by `order_types.Program`, let its input be a tuple
`x = (x0, ..., x(n-1))` of signed 32-bit integers, with `1 <= n <= 4`. Assume
complete successful decimal input and ordinary successful numeric output. Its
computation contains automatic unqualified `int` locals, copies of previously
initialized locals, comparisons of locals, Boolean combinations of those
comparisons, and finite `if`/`else` control flow. It contains no loops,
arithmetic, data constants, casts, pointer computation, indirect calls,
qualifiers, alignment attributes, external computational functions, or data
structure operations. The only literal numerical result is the final
`return 0`, which is not the program's reported numerical observation.

Local identifiers are conservatively restricted to lower-case ASCII letters
and decimal digits, starting with a letter, excluding `stdin`, `stdout`,
`stderr`, `main`, `scanf`, and `printf`. This excludes object-like standard
stdio macros, leading-underscore implementation-reserved names, and source
names whose native preprocessing would change the analyzed tokens. The fixed
strict C11 compilation context is part of the source model; arbitrary added
headers, command-line macro definitions, and nonstandard macro environments
are outside it. I/O format **spellings** are fixed literally: one or more `%d`
conversions for input and exactly `"%d\n"` for output. A Python-decoded string
lookalike, including `\x25d`, is rejected because C and Python hex-escape rules
are different.

The profile checks the whole syntax tree, including branches not taken by a
particular input. Each abstract execution must read only initialized locals
and produce exactly one output. A syntactically admitted program with an
undefined or missing-output abstract path fails the study; admission alone
does not assert correctness.

Define the **rank pattern** `rho(x)` by replacing the smallest distinct input
value by `0`, the next distinct value by `1`, and so on. Equal inputs receive
equal ranks. A canonical pattern is therefore a tuple whose set of entries is
exactly `{0, ..., k-1}` for some `1 <= k <= n`.

**Proposition.** For each canonical rank pattern `r`, all input tuples `x`
with `rho(x) = r` follow the same branch trace, have the same initialized-read
and output-count outcomes, and, when valid, output `x[j]` for one input
coordinate `j` selected by the abstract execution on `r`. The selected
coordinate and branch trace can depend on `r`, but not on the actual magnitudes
of its distinct values.

### Proof

The abstract environment associates every initialized local with an input
coordinate token. The corresponding concrete local contains that input's
value. Each `scanf` position establishes this relation, and a declaration
without an initializer leaves the variable uninitialized in both environments.
A copy assignment preserves the relation. No other data-producing expression
is admitted.

If two initialized locals hold tokens `i` and `j`, then `x[i] < x[j]` exactly
when `r[i] < r[j]`; the same equivalence holds for `<=`, `>`, `>=`, `==`, and
`!=`. Induction over Boolean expressions preserves their values and their C
short-circuit evaluation paths. An uninitialized read therefore occurs at the
same evaluated operand in both executions, if it occurs at all.

Induction over the finite statement tree now shows that both executions take
the same conditional branches, copy the same tokens, and encounter the same
output events. A valid output holding token `j` denotes `x[j]` concretely and
`r[j]` abstractly. The final `return 0` is identical in both executions. There
is no arithmetic to overflow and no unbounded iteration. This proves the
proposition.

Every finite input tuple has exactly one canonical pattern. Conversely, every
enumerated pattern is realizable by its ranks themselves, which are all
representable int32 values. Enumerating all canonical patterns thus exhausts
the computational behavior classes under these assumptions. The generator
checks the entire set of tuples in `{0, ..., n-1}^n` and retains exactly the
contiguous, zero-based rank sets; it does not sample patterns.

The number of classes is `sum(k! * S(n,k), k=1..n)`, where `S(n,k)` counts
partitions of the coordinate positions into `k` nonempty equality groups.
For three inputs the count is `1 + 6 + 6 = 13`; for four it is
`1 + 14 + 36 + 24 = 75`. Ties are essential; checking only permutations of
distinct values would inspect just 6 or 24 classes.

### Agreement with median/minimum and another program

Median and minimum commute with strictly increasing renamings of distinct
values. Their output rank on a class is therefore sufficient to determine
agreement for every tuple in that class. Likewise, two admitted programs agree
in output throughout the entire int32 input space precisely when their output
ranks agree on every canonical pattern. Different selected coordinates that
are tied in a pattern still denote equal outputs.

This equivalence concerns input/output values. Two programs can have the same
output behavior and different control-flow traces, syntax, or patch provenance.
The two behavior groups reported by this study must not be interpreted as two
source-identical patches or two identical execution traces.

## Connection to the retained real sources

The study checks thirteen hash-bound original/candidate/reference sources,
the same sources used by the existing six-case IntroClass certificate study.
An independent AST traversal in
`experiments/introclass-certificates/independent_review.py` verifies that the
retained raw and normalized source bodies preserve computational nodes and
statement order, accounting explicitly for the recorded input and output
shells. Its separately written branch models agree with every one of the
417 source/order-class executions.

The new syntax gate and token interpreter import no RepairSeal frontend,
symbolic circuit, or receiver. They still share `pycparser` infrastructure with
the earlier structural review. Raw input via the published `atoi(argv[k])`
wrappers, fixed teacher prompts, and numeric suffixes remain assumptions of
the documented I/O adaptation. Their concrete behavior is cross-checked by
freshly compiling the exact raw bytes and retained normalized bytes and running
both at the frozen boundary points. This evidence supports those exact
adaptations; it does not prove arbitrary library, platform, process, or
malformed-input behavior.

## Empirical boundary checks versus the mathematical argument

Four order-preserving embeddings are declared before the native run: small
rank representatives, values adjacent to `INT_MIN`, values adjacent to
`INT_MAX`, and values spread across the full int32 range. All published tests
are also included. Duplicate concrete inputs are executed once per source,
form and compiler mode. The run uses one GCC executable in three modes:
`-O0`, `-O2`, and `-O1 -fsanitize=undefined -fno-sanitize-recover=all`.

The 10,602 native executions are implementation checks at specified points;
they are not 10,602 independent repairs and are not the basis for claiming
exhaustive int32 coverage. Exhaustive coverage for the admitted computational
fragment follows from the proposition and complete class enumeration. UBSan
silence alone does not establish absence of undefined behavior.

The weak-order fractions are counts of behavior classes, not probabilities
under a uniform integer distribution or estimates of defect prevalence. The
six patches were selected after known failures were observed. Their output
equivalence reduces the effective behavioral diversity to two groups; this is
an explicit limitation, not a new benchmark-population claim.

No quotient representative is claimed to be RepairSeal's globally canonical
least witness over the full int32 space. The existing receiver's finite-domain
canonical diagnostics remain separate.
