# Real test-passing patches received by RepairSeal

This is a new, actually executed six-patch campaign. It connects published
Angelix patches from the separate `../real-patches/` study to the signed full
receiver, evidence-erased direct receiver, and compact refutation checker.
The six patches were selected after the fixed-sample study found their failures.
They are an exploratory mechanism study, not a prevalence sample.

## Source, selection, and license

Every original, candidate, and teacher source is identified by SHA-256 in
`records/protocol.json`. Raw bytes are retained in `../real-patches/sources/`;
the released diffs, archive identities, license notices, and complete selection
inventory are in that study. The source dataset is the published Angelix
inventory in [Zenodo 1012686](https://doi.org/10.5281/zenodo.1012686), licensed
CC BY 4.0; the original IntroClass source retains the ProgramRepair BSD 3-Clause
notice. The generated files in `records/normalized/` are explicitly adapted
derivatives, not unchanged upstream translation units.

There are six distinct candidate patches, five original subjects, and two
program families. In particular, `apr-072` and `apr-073` repair the same
original subject. These are not six independent bugs. `apr-082` was not included:
its source does not meet this narrow initialization/adaptation profile without
additional semantic work. No initialization was added to make it pass admission.

## Observed results

All six original candidate programs pass every published blackbox and whitebox
test on both plain compilers. Every complete declared domain contains a wrong
output. Counts below are recomputed from `records/requests.json`,
`records/semantic-observations.jsonl`, and both native JSONL files.

| Patch | Original subject | Domain points | Wrong-output points | Canonical witness input | Candidate | Teacher | Original |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| apr-043 | median/h29/000 | 133 | 10 | `[-1, -1, -2]` | -2 | -1 | -2 |
| apr-046 | median/h3/000 | 133 | 10 | `[-1, -1, -2]` | -2 | -1 | -2 |
| apr-069 | median/h5/000 | 133 | 10 | `[-1, -1, -2]` | -2 | -1 | -2 |
| apr-070 | median/h7/000 | 133 | 10 | `[-1, -1, -2]` | -2 | -1 | -2 |
| apr-072 | smallest/h1/001 | 263 | 41 | `[-1, 1, 0, -1]` | 0 | -1 | -1 |
| apr-073 | smallest/h1/001 | 263 | 41 | `[-1, 1, 0, -1]` | 0 | -1 | -1 |

The domain is the same exact point set as the source study: a small complete
integer grid united with all supplied test inputs. Canonical order includes
the modeled branch trace before the input tuple; it is not input order alone.
The signed receiver uses its existing **reference-everywhere** policy, so all
six signed failure roots are named `repair`. On the smallest witness the
original is already correct: under the source study's operational repair
region, that witness is a preservation failure. These are different declared
policies, not conflicting measurements. The signed profile has not been
extended to claim a nonvacuous preservation root.

The final campaign performed 52 successful compilations and 8,996 native
program executions: 13 unique raw source identities, their 13 adapted forms,
two compilers, and all applicable inputs. There are 2,249 source/input
observations, 8,996 native correspondence agreements, zero disagreements,
168 supplied-test/compiler checks, six full/direct complete-result agreements,
and six compact confirmations. The teacher output agrees with separately
computed median/minimum on all 396 family/input points.

## What adaptation means

`normalize.py` is a narrow, rejecting adapter. It checks the exact published
identity macro and the original main signature; preserves the macro's
unparenthesized replacement semantics; replaces ordered `atoi(argv[k])` input
reads with reads of the same integer variables; removes only admitted identity
integer casts; and translates the teacher's fixed prompt and numeric suffix.
Computations, conditions, declaration types, and assignment order are retained.
The ordinary candidate test criterion uses its complete original stdout.

Both the original bytes and the adapted bytes were compiled and run under
GCC 14.2.0 and Clang 19.1.7 on every declared point. Full teacher stdout is
matched against the fixed complete prompt/suffix codec. Arbitrary output is
not stripped to manufacture correspondence. Compiler identities, commands,
binary hashes, return codes, raw stdout/stderr, and stream hashes are retained.

Independent review found macro-precedence and main-signature boundaries in an
earlier adapter. Both were corrected, and the entire native campaign was run
again with the final implementation. Only that final campaign is counted here.

`independent_review.py` does not import the normalization, bridge, circuit,
or collection implementations. It separately compares whole-body AST
computational structure and writes branch models for the 13 fixed source
identities. It checks 13 structural correspondences, 2,249 value-and-trace
observations, all 8,996 complete native output observations, the six canonical
counterexamples, and all 168 supplied-test/compiler checks. Parsing infrastructure
(`pycparser`) is shared. `independent-review.json` is the retained review result;
this is computational review, with zero human annotators.

## Verify and reproduce

From `artifact/`, with the pinned Python dependencies:

```sh
python3 -B experiments/introclass-certificates/verify.py
python3 -B experiments/introclass-certificates/independent_review.py \
  --data experiments/introclass-certificates/records
python3 -B -m unittest tests.test_introclass_normalization \
  tests.test_introclass_independent_review tests.test_int32_refutation -v
```

These commands replay local source/certificate/review calculations and check
retained process receipts; they do not launch new native processes.

To execute the entire native campaign again, choose new output and work paths
outside the project and provide two compiler executables:

```sh
python3 -B experiments/introclass-certificates/run.py \
  --output ../fresh-introclass-records --native-work ../fresh-introclass-work \
  --gcc /path/to/gcc --clang /path/to/clang
```

The original selected source bytes are already included under their stated
licenses. The full external archive is not required for this six-case replay.

## Boundaries

Finite-domain correctness and source correspondence do not prove equivalence
for arbitrary C, arbitrary integer inputs, all I/O encodings, or production
software. Full and direct receivers share a frontend and are not independent
semantic oracles. The separate branch models and native executions reduce that
shared risk for these exact sources and inputs. A compact certificate confirms
one actual violating member of the declared point set; it neither proves
acceptance nor establishes that the supplied witness is globally canonical.
Its checker evaluates only that member, while full/direct evaluation establishes
the complete canonical result. Adding the witnessed input to a test suite would
also expose the defect; no claim is made that ordinary tests can never do so.
