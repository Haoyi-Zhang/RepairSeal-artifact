# Measurement overhead in demand receiving

The five-arm experiment separates the cost of observing demand evaluation
from the cost of its receiving algorithm. The original support-keyed and
point-local implementations update counters during memo queries, stores,
conditional choices and diagnostic traversal. They also track maximum stack
depth; the support implementation records projection work. The live-node
baseline obtains its semantic-cell total by aggregation. Removing measurement
bookkeeping from both demand implementations makes the effect of this
asymmetry directly observable.

## Paired implementations

| Arm | Receiving implementation | Returned observation |
| --- | --- | --- |
| `support` | Original support-keyed demand | Canonical decision and original work metadata |
| `point` | Original point-local demand | Canonical decision and original work metadata |
| `support_uninstrumented` | Exact derived support receiver with measurement bookkeeping removed | Canonical decision |
| `point_uninstrumented` | Exact derived point receiver with measurement bookkeeping removed | Canonical decision |
| `live` | Original live-node baseline | Canonical decision and original work metadata |

`tests/counter_free_receivers.py` derives the two measurement-free receivers
from the actual source syntax trees. Its whitelist identifies each removable
statement by source file, enclosing function or method, exact syntax tree and
occurrence count. The original sources remain unchanged. A new measurement
site, modified counter argument, unexpected return expression or helper
signature causes derivation to fail until the transformation is reviewed.

The transformation removes the counter object and its argument plumbing,
per-event counter calls, stack-depth updates, projection measurements,
measurement-only result fields and one point-memo accounting consistency
check. It retains source admission and reconstruction, all exact Boolean and
word checks, local value rules, support construction, representative
selection, key construction, cache operations, traversal, source definedness,
candidate traces and canonical diagnostic minimization. It also retains the
support receiver's per-call functional helper imports, routing them to the
derived definitions. No no-op counting callback remains in the traversal.
The derived receivers return only `status` and `witness`; omitted work fields
are never represented as zero.

The executable derived source, exact change manifest and copies of the small
executed Python source files accompany every campaign. The manifest binds
the selected and derived syntax trees to their original source bytes. These
records make the intervention inspectable without redistributing the
external C source archive.

## Population and preflight

The study reconstructs all 739 existing natural candidate-subject
combinations on both repair and union domains: 1,478 requests across 35
problems. Each domain population contains 95 own references, 95 own originals
and all 549 compatible cross-source combinations. No request is selected by
measured cost or by the direction of an effect. Source admission and lowering
are performed anew inside every receiving call.

Before measurement, each arm receives every request once. These 7,390
untimed calls check complete typed canonical results against the retained
signed study. The three original arms also reproduce their complete prior
point-demand result records, including work counters. The two derived arms
must contain exactly the canonical fields.

Temporary store hooks inside those same preflight calls record node identity,
memo key or actual input index, exact value type and local value. Each
instrumented demand arm must have exactly the same store sequence as its
derived counterpart. The sequence length must equal its original
semantic-cell counter. After an element-by-element typed comparison, only
the sequence identity and number of stores are retained; duplicate large
trace files are unnecessary. This establishes execution correspondence for
the intervention. It does not introduce a separate native-C semantics oracle.
All hooks are restored and their method identities checked before timing.

## Timing and comparisons

The protocol is written and bound before the first preflight call. Each
request then receives every arm ten times, using the ten orders of a
five-treatment Williams design. Across its ten repetitions each arm occurs
twice in every position and each directed adjacent pair occurs twice. Request
order is independently shuffled within each repetition using the recorded
seed. All arms use the same dispatch and timing interval, with
`perf_counter_ns` immediately around the complete receiving call. Function
objects are resolved before measurement, so the derived arms do not incur an
extra initialization wrapper. Normal garbage collection remains enabled.

There are 73,900 timed calls. Each call is checked against its own complete
preflight result after the timer stops. The raw record retains every integer
nanosecond measurement, actual arm order, request position and repetition.
Input, source, prior-record and protocol bindings are rechecked before a
passing summary is written. A failed or interrupted campaign does not
constitute a completed result.

For every request, analysis takes the median of the ten durations per arm
and then forms these eight within-campaign ratios:

| Ratio | Question |
| --- | --- |
| `support_over_live` | How does the original support receiver compare with the live baseline? |
| `point_over_live` | How does the original point receiver compare with the live baseline? |
| `support_uninstrumented_over_live` | Does the support receiver's ranking persist after removing its measurements? |
| `point_uninstrumented_over_live` | Does the point receiver's ranking persist after removing its measurements? |
| `point_uninstrumented_over_support_uninstrumented` | What is the point/support comparison with measurement bookkeeping removed from both? |
| `support_over_uninstrumented` | How much does the support receiver's measurement bookkeeping cost in this implementation? |
| `point_over_uninstrumented` | How much does the point receiver's measurement bookkeeping cost in this implementation? |
| `point_over_support` | What is the paired original point/support comparison in this campaign? |

Ratios below one favor the numerator. Request distributions use empirical
order-statistic quantiles. Problem-level ratios divide the sums of request
medians within each problem; they do not pool unrelated raw calls. Analysis
also reports the median across 35 problem ratios and lower/equal/higher
counts, and repeats the full aggregation for the 549 cross-source requests
across 23 problems. Repair and union domains are reported separately.
Earlier timing campaigns supply reference decisions and deterministic work,
not nanosecond values for these ratios.

Removing measurement bookkeeping isolates that complete intervention. It
does not separately assign elapsed time to counter calls, stack-depth
updates, metadata construction or projection measurements. Likewise, the
point/support contrast changes support analysis, representative selection
and memo layout together. Both interpretations follow directly from the
actual paired implementations.

## Completed findings

The retained campaign completed all 1,478 requests, 7,390 preflight calls and
73,900 timed calls; canonical decisions and the paired typed store sequences
agreed throughout. Independent recomputation verified the raw schedules,
medians, eight ratios and all request/problem aggregations. Within this
campaign, the request-median ratios of the original to measurement-free
implementations were 1.124/1.297 for support demand and 1.104/1.353 for point
demand on repair/union domains. Removing measurement bookkeeping therefore
accounts for part of the original timing difference. The measurement-free
support/live ratios were 1.187/1.730, and the point/live ratios were
1.039/1.201. The repair-stage point receiver was close to the live baseline;
the small median difference is not evidence of a general speed disadvantage.
At the problem level, measurement-free point receiving exceeded live-node
time in 27/35 repair problems and 33/35 union problems. Point receiving still
ran faster than support receiving after measurement removal: its request
ratios were 0.863/0.694, with lower aggregate time in 33/35 and 35/35 problems.
The 549 cross-source combinations gave point/live ratios of 1.041/1.204 and
point/support ratios of 0.858/0.687 after measurement removal. These are paired
observations of the complete implemented receivers on the registered
population; they isolate the stated bookkeeping intervention without
assigning its elapsed effect to any single counter or phase.

## Reproduction

From the released artifact root, the focused transformation and semantic
checks run without the external source archive:

```sh
PYTHONDONTWRITEBYTECODE=1 python tests/test_counter_free_receivers.py -v
```

To reconstruct and measure the complete population, provide the original
archive and use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python tests/counter_overhead_study.py \
  --corpus data/source-programs/normalized-corpus.json \
  --archive /path/to/codeflaws.tar.gz \
  --prior data/signed-contract \
  --point-prior experiments/point-demand/measurements \
  --output /tmp/repairseal-counter-overhead
```

`--cpu` optionally fixes process affinity to one permitted logical CPU.
Measurements should run without competing verification or compilation jobs.
For a complete fresh reproduction, `--point-prior` selects the freshly
completed point-demand campaign. The source and canonical-record bindings
must match; substituting a different request population is rejected.

The independently written checker requires only the recorded campaign and
its retained references:

```sh
PYTHONDONTWRITEBYTECODE=1 python tests/verify_counter_overhead_study.py \
  /tmp/repairseal-counter-overhead \
  --reference data/signed-contract/requests.json \
  --point-reference experiments/point-demand/measurements/work.json \
  --output /tmp/repairseal-counter-overhead-independent.json
```

It imports neither the experiment writer nor a receiving evaluator. It
reconstructs request medians and every aggregate from raw durations, checks
the actual balanced schedule and complete population, and validates the
canonical, work, source and record bindings.

## Campaign records

The complete campaign belongs in `experiments/counter-overhead/`. Its
`protocol.json` defines the intervention and measurement scope;
`derived/manifest.json` lists every AST change; `derived/receivers.py` and
`executed-sources/` retain the executed code. `work.json` holds preflight
observations, `timings.jsonl` holds individual measurements,
`request-timing-summary.json` holds request medians and `analysis.json` holds
the paired comparisons. Completion is established by both the writer's
`summary.json` and the independent recomputation result. Numerical findings
must be drawn from that completed campaign.
