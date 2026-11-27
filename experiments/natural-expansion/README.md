# Additional whole-source Codeflaws cases

This study expands the two manually normalized Codeflaws examples by using the
existing signed-C profile directly on complete, unchanged source files. The
profile admits scalar input/output, assignments, conditionals and early returns;
it retains signed overflow and division definedness. It does not convert signed
operations to unsigned operations or edit an unsupported program into the
accepted language.

## Selection and domains

The main cohort contains 20 distinct problems selected deterministically from
the previously recorded 95 subjects defined on all given tests. After excluding
4-A and 84-A, problems are ordered by scalar input arity, numeric contest number,
and problem letter. The smallest numeric original/reference submission pair is
selected per problem, and the first 20 problems are retained.

Two additional cases, `171-B-bug-1463121-1463124` and
`675-A-bug-18264119-18264212`, follow up the undefined behavior previously recorded
outside that all-defined cohort. They are expressly targeted exploratory cases,
not independent random samples. Domain design also uses the delivered records,
including the previously known 15000 overflow input. This is not blind
preregistration. The complete domain list is frozen before the new source run;
there are no replacements or additions in response to its outcome.

`problem-sources.json` records the official Codeforces input constraints for
every included problem. `domains.py` enforces both numeric bounds and correlations
such as `m <= n`, even side lengths, and feasible grade sums. Every provided repair
and held-out test is included, without the older eight-slot truncation. Additional
points include complete small legal domains and explicitly selected boundary
points. Except for the explicitly enumerated small domains, these finite sets
do not cover every legal task input.

`frozen-plan.json` records the selection, all given tests, source/test fingerprints,
and declared point vectors. `records/protocol.json` is the actual execution-bound
copy. Original and accepted Codeflaws submissions are kept distinct: an unchanged
original is a negative candidate, and an accepted submission is the supplied
correction. Neither is attributed to an automatic repair tool.

## Four checks and native execution

For both versions of every pair, the experiment performs:

1. Independent concrete AST interpretation and symbolic circuit evaluation of
   every declared source/input combination, comparing definedness, value, and
   trace.
2. Complete vector production/checking, complete direct evaluation, and direct
   construction of the same full record. All three complete decisions must agree
   with the concrete canonical diagnostic.
3. A task-bound compact one-point refutation for each rejected request. This
   proves a real violating point; canonical leastness is supplied by the complete
   arms, not by the compact checker.
4. Plain GCC and Clang execution of unchanged original source on every declared
   point. Every given test is also run with its exact archived input bytes; byte
   identical source/input pairs can share an execution, with all logical test
   occurrences retained. Defined outputs must agree with both semantic models.

Undefined model executions are retained as undefined. Their ordinary compiler
outputs are observations of those binaries, never a defined C value. Both
compilers additionally run UBSan on these points. A compile-time/runtime int32
probe and an overflowing positive control establish the target and sanitizer
configuration. Raw stdout, stderr, process status, compiler flags and binary
hashes are retained. Native branch traces are not measured.

The signed request policy is `reference-everywhere`, so preservation is vacuous
in these certificate cases. The separate real-patch failure-mode study is the
source of preservation-region measurements. Each case reports whether the
reference remains defined on the whole declared domain; a bad reference is not
silently treated as a correct output oracle.

## What counts as testing missing a failure

`all_given_tests_pass_both_compilers` requires successful stdout agreement with
the archive oracle on every given repair and held-out test under both ordinary
compilers. `tests_pass_but_wrong` additionally requires a certificate refutation
on the declared domain: candidate undefinedness, or a value disagreement with a
reference that is defined on the domain. A repair-only pass followed by a
held-out failure does not meet this definition. Failure to collect a process
observation never counts as a semantic counterexample.

The two targeted UB cases were selected because the old concrete interpreter
reported undefined executions, not because their ordinary tests were known to
pass. The fresh ordinary runs determine that latter fact. Any negative result
for the testing-gap hypothesis remains in the delivered records.

## Reproduction

All raw Codeflaws source/test payloads remain in an external working directory;
they are not redistributed here. Acquire the exact archive by the main artifact
README and use two distinct GCC/Clang executables:

```sh
python -B experiments/natural-expansion/run.py \
  --archive ../codeflaws.tar.gz \
  --output ../fresh-natural-expansion \
  --native-work ../fresh-natural-expansion-native \
  --gcc /usr/bin/gcc --clang /usr/bin/clang

python -B experiments/natural-expansion/verify.py
python -B -m unittest discover -s tests -p test_natural_expansion.py -v
```

The offline verifier needs neither archive nor compiler. It recomputes every
retained packet's local arithmetic, its complete canonical verdict, one-point
certificate bindings, native stdout decoding and stream hashes, domain/test
coverage, and all summary counts. The hash inventory covers every retained data
file. This validates retained evidence; fresh verification of the source-to-DAG
correspondence requires the pinned external archive.

The reported model agreement is computational cross-validation. It is not a
two-person annotation study. The concrete and symbolic implementations share
source admission but execute arithmetic independently; the native compilers add
separate output checks. No independence of related submissions or statistical
generalization to arbitrary C patches is claimed.

## Observed results

The fresh run completed successfully with GCC 14.2.0 and Clang 19.1.7 under CPython 3.12.14. `records/summary.json` contains the exact counts; `verification.json` reports 100 passing offline checks.

| Measurement | Recorded count |
| --- | ---: |
| Deterministically selected pairs | 20 |
| Targeted historical-UB follow-up pairs | 2 |
| Total pairs / distinct problems / distinct source versions | 22 / 21 / 44 |
| Complete requests / accepted / refuted | 44 / 22 / 22 |
| Repair / definedness refutations | 20 / 2 |
| Full/direct/concrete agreements | 44 / 44 |
| Compact refutation confirmations | 22 |
| Concrete/circuit source-input agreements | 16,878 / 16,878 |
| Given-test logical occurrences per compiler, across both source versions | 2,602 |
| Ordinary native process executions | 33,960 |
| Defined native output agreements | 33,446 / 33,446 |
| UBSan confirmations, across both compilers | 514 / 514 |
| All native process executions | 34,474 |
| Pairs with an undefined reference anywhere in the declared domain | 0 |
| Candidates passing all given tests under both compilers | 22 |
| Candidates passing all given tests but refuted on the declared domain | 0 |

The 22 all-test-passing candidates are the supplied accepted versions. Both targeted UB originals also fail ordinary tests: 171-B passes 40 of 49 and 675-A passes 188 of 193 under each compiler. These cases provide real definedness failures but do not establish a testing gap. The separate IntroClass APR certificate study supplies testing-gap cases.

### Per-pair outcomes

Test counts below include every provided repair and held-out file occurrence for one source version. The GCC and Clang original pass counts agree in every row. Every supplied version passes all given tests and is accepted on its listed domain. Canonical witnesses refer to the unchanged original candidate under the signed source profile.

| Subject | Domain points | Given tests | Original passes (each compiler) | Original obligation | Canonical witness | Supplied |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `104-A-bug-7900405-7900409` | 25 | 48 | 46 | O1 | `[21]` | ACCEPT |
| `122-A-bug-18015599-18015631` | 1000 | 44 | 41 | O1 | `[477]` | ACCEPT |
| `171-B-bug-1458594-1458980` | 102 | 41 | 1 | O1 | `[2]` | ACCEPT |
| `313-A-bug-16465019-16465065` | 1134 | 54 | 43 | O1 | `[-623563697]` | ACCEPT |
| `617-A-bug-17713160-17713171` | 152 | 36 | 15 | O1 | `[1]` | ACCEPT |
| `672-A-bug-18054472-18054639` | 1000 | 67 | 63 | O1 | `[215]` | ACCEPT |
| `194-A-bug-7939649-7939655` | 69 | 44 | 25 | O1 | `[1,4]` | ACCEPT |
| `451-A-bug-17925132-17925142` | 77 | 32 | 24 | O1 | `[2,3]` | ACCEPT |
| `476-A-bug-16348364-16348536` | 333 | 42 | 22 | O1 | `[3,2]` | ACCEPT |
| `570-B-bug-13182087-13182283` | 100 | 77 | 74 | O1 | `[1,1]` | ACCEPT |
| `638-A-bug-16913566-16913587` | 100 | 75 | 41 | O1 | `[4,4]` | ACCEPT |
| `90-A-bug-3761963-3761989` | 530 | 62 | 55 | O1 | `[1,1,0]` | ACCEPT |
| `112-B-bug-668250-668255` | 212 | 36 | 34 | O1 | `[4,1,3]` | ACCEPT |
| `124-A-bug-17380518-17380581` | 178 | 55 | 39 | O1 | `[2,0,0]` | ACCEPT |
| `168-A-bug-13795832-13795874` | 360 | 47 | 34 | O1 | `[2,2,50]` | ACCEPT |
| `197-A-bug-4169281-4169297` | 591 | 105 | 96 | O1 | `[2,2,1]` | ACCEPT |
| `216-A-bug-5868432-5868621` | 537 | 43 | 12 | O1 | `[3,2,2]` | ACCEPT |
| `515-A-bug-16913836-16913854` | 516 | 55 | 50 | O1 | `[-1000000000,-999999999,1]` | ACCEPT |
| `546-A-bug-18027083-18027120` | 298 | 17 | 11 | O1 | `[1,2,1]` | ACCEPT |
| `659-A-bug-18007364-18007390` | 256 | 79 | 63 | O1 | `[2,2,1]` | ACCEPT |
| `171-B-bug-1463121-1463124` | 102 | 49 | 40 | O0 | `[14999]` | ACCEPT |
| `675-A-bug-18264119-18264212` | 767 | 193 | 188 | O0 | `[-1000000000,-2,-1000000000]` | ACCEPT |

The main cohort is the first 20 rows. The final two rows are targeted follow-ups. O2 is vacuous for these reference-everywhere requests; no preservation frequency is inferred from this table.
