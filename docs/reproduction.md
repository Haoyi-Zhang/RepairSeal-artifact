# Reproducing RepairSeal

## Evaluator-first acceptance path

The supported evaluator entry point is `../evaluate.sh`.  It separates local
fresh execution, retained-output recomputation, and external-only campaigns:

```sh
../evaluate.sh preflight
../evaluate.sh smoke
../evaluate.sh paper
../evaluate.sh core
../evaluate.sh external --python312 /path/to/python3.12 \
  --cbmc66 /path/to/cbmc-6.6.0 --cbmc611 /path/to/cbmc-6.11.0 \
  --cpachecker /path/to/cpachecker --archive /path/to/codeflaws.tar.gz
```

The exact tool installation (Debian 13 packages, CPython 3.12.14, CBMC 6.11.0,
CPAchecker 4.3, Codeflaws archive) and measured runtimes are in the artifact
README (sections "Installing the external tools" and "External campaigns").
Each invocation requires a new output path, records commands and logs, and
writes `evaluation.json`.  `expected-results.json` is the exact claim boundary.
`verify_expected_results.py` parses named fields and record hash inventories;
it does not accept a number merely because it appears somewhere in the tree.

`preflight`, `smoke`, `paper`, and `core` can succeed without the external
campaigns. `paper` (and the paper step of `core`) needs the companion `paper/`
sources next to this directory; in a standalone checkout that step is reported
as skipped and `paper` returns `FAILED_PRECONDITION`.  `external` and `all` return `FAILED_PRECONDITION` with zero
scientific studies started until all pinned external prerequisites are present.
This state is different from a failed program, a timeout, and a negative
scientific result.

## Lower-level scientific driver
Run commands from the `artifact/` directory. The entry point writes all new observations to a directory outside the artifact and preserves the supplied project and its retained data. The destination must not already exist. Python optimization (`-O` or `-OO`) is rejected because the scientific drivers use assertions to enforce oracle agreement.

## Recompute the reported measurements

This command checks the retained raw durations, balanced schedules, complete request populations, canonical reference results, request medians and problem aggregates. It includes the experiment that removes measurement bookkeeping from both demand receivers. It also independently recomputes support coverage and Boolean outcomes from the 739 retained signed circuits and their actual point sets:

```sh
python3 -B reproduce.py --checks analysis --output /absolute/new/analysis
```

It does not rerun the C programs, external verifiers or receiving measurements. A successful report therefore says `PASS_SELECTED_CHECKS`, with every unselected stage marked `NOT_REQUESTED`. The three timing campaigns remain separate: the original five receivers with ten repetitions per request, the point-local ablation with four receivers and twelve repetitions, and the measurement-overhead experiment with five receivers and ten repetitions. Ratios are recomputed from each campaign's own paired observations.

## Execute the complete set of studies

Provide local tool paths and the external Codeflaws archive. The runner does not download software or execute upstream build scripts.

```sh
python3 -B reproduce.py \
  --output /absolute/new/reproduction \
  --archive /absolute/path/codeflaws.tar.gz \
  --cbmc /absolute/path/cbmc \
  --witness-cbmc /absolute/path/witness-cbmc \
  --cpachecker /absolute/path/cpachecker \
  --gcc /absolute/path/gcc \
  --clang /absolute/path/clang \
  --jobs 4
```

Use `--library-dir /absolute/path/to/libraries` when the selected CBMC needs additional dynamic libraries. The option can be repeated. The recorded scientific Python dependency is pinned in `requirements-codeflaws.txt`. External C execution requires a POSIX host; CBMC uses `prlimit`, and CPAchecker requires its supported Java runtime. Startup probes check the selected executables before any study starts. If a dependency or required input record is missing, the entry stops with `FAILED_PRECONDITION` and records that zero scientific studies started.

The retained Boolean comparison used CBMC 6.6; the witness campaign used CBMC 6.11.0 with CPAchecker 4.3. `--witness-cbmc` selects a separate producer for that campaign and is independently checked at startup when its path differs. Omitting it uses `--cbmc` for both campaigns. The wrapper permits other executable configurations for fresh experiments and records their actual startup output; it does not label them as the retained tool configuration.

### Historical execution identities

The retained Python interpreter is CPython 3.12.14. The admission-journal and
domain-transport receiver identities bind the full Python implementation and
version together with their trusted source bytes. Running those studies under a
different interpreter is a valid fresh execution with a new identity, but it
cannot validate or relabel historical receipts. Exact receipt replay therefore
requires the retained interpreter version. The admission conformance tests keep
that historical compatibility check separate from current-runtime behavior: they
skip only the exact retained-receipt replay when the receiver identity differs,
then generate a fresh journal and run the full positive, stale-source, wrong-
identity, count-tampering and SQLite-metadata controls against it. A skip is not
evidence that the retained receipt was replayed.

The supplied `data/unsigned-demand/protocol.json` binds an earlier
`tests/demand_comparison.py` source revision, but no executed-source snapshot of
that revision is bundled. A fresh `--checks demand` run records and checks the
current driver and can compare its deterministic decisions and work records to
the retained outputs. It is not an exact source-identity replay of the historical
driver, and the retained protocol must not be rewritten to imply otherwise.

The default selection executes every stage below, in order. The standard-witness campaign is part of the default selection.

| Stage | Work actually performed |
| --- | --- |
| `analysis` | Independently recompute all three retained timing campaigns, canonical reference agreement, and signed support-coverage records. |
| `units` | Discover every current unit-test module, including the external CBMC controls; skipped methods make this stage incomplete. |
| `functional` | Execute the complete functional campaign, structured/grammar controls, compact evidence, domain transport, journal and native arithmetic controls. |
| `demand` | Recompute the 780 unsigned comparisons, existing domain-transport targets and axis controls. |
| `cbmc` | Recheck all 804 unsigned Boolean decisions with the supplied CBMC. |
| `native` | Screen the original source archive and compile/execute its admitted complete programs with both supplied compilers. |
| `signed` | Reconstruct all 1,478 signed finite requests and compare full, demand, direct-record and concrete reference observations. |
| `coverage` | Reconstruct all 739 natural candidate/subject combinations, freeze support coverage before joining union outcomes, then independently recompute the retained DAG rules and projections. |
| `timing` | Execute the five-arm, ten-repetition receiving-time campaign. |
| `point-timing` | Execute the four-arm, twelve-repetition point-local ablation. |
| `counter-overhead` | Co-measure original and uninstrumented support and point receivers with the live-node baseline, using ten balanced repetitions per request, then independently reconcile all recorded calls. |
| `headers` | Execute the owned header-admission controls with both compilers. |
| `witness` | Run the complete producer/validator campaign and its 18 negative controls, reconcile its records, compare both source emitters with every retained C product, analyze matched search counters, then execute three additional input-constraint controls. |

When `native` and `signed` are selected together, the signed study consumes the newly produced normalized corpus. The coverage and timing studies also use that fresh corpus when `native` is selected, and use the newly produced signed-contract reference when `signed` is selected. The `counter-overhead` stage additionally uses the fresh `point-timing` work record when that stage is selected; otherwise it uses the retained point-demand reference. The selected stage uses the identified retained input when its producing stage is not requested. Retained observations never replace a selected execution. The archive-free coverage and counter-overhead verifiers run on both fresh records and the retained-analysis path; their own process failures fail the enclosing stage.

The receiving measurements run serially. `--cpu N` pins each timing child to an allowed processor when supported by the host. `--jobs` controls only external-verifier workers; values from one to four are accepted. Keep other CPU-intensive work out of the timing interval if making a comparison with the retained measurements. Actual durations remain specific to the tools, implementation and host recorded by each run.

`--step-timeout SECONDS` supplies a finite positive wall limit for each invoked study command; the default is 21,600 seconds (six hours), and callers can lower it. The complete command uses four external-verifier workers, matching the retained witness campaign. The functional entry also passes the selected limit to its nested scientific children, including the full disk replay; its internal default of 240 seconds is therefore not an independent cutoff when invoked here. A slow or contended host can use a larger explicit limit. Reaching a limit remains a failed execution, with its original output retained.

## Select a concrete subset

Use `--checks` when rerunning a particular part of the project:

```sh
python3 -B reproduce.py \
  --checks native signed coverage \
  --output /absolute/new/source-checks \
  --archive /absolute/path/codeflaws.tar.gz \
  --gcc /absolute/path/gcc \
  --clang /absolute/path/clang
```

```sh
python3 -B reproduce.py \
  --checks point-timing \
  --output /absolute/new/point-measurements \
  --archive /absolute/path/codeflaws.tar.gz
```

The first command reruns original programs, signed contracts and the natural-domain support-coverage study. The second uses the retained normalized corpus and signed-contract reference, then performs new measurements of all four arms. A selected subset can return `PASS_SELECTED_CHECKS`; it cannot return `PASS_COMPLETE`.

To run only the measurement-overhead experiment with the retained signed and point-work references:

```sh
python3 -B reproduce.py \
  --checks counter-overhead \
  --output /absolute/new/counter-measurements \
  --archive /absolute/path/codeflaws.tar.gz
```

This stage performs 7,390 untimed preflight receiving calls and 73,900 timed receiving calls over all 1,478 requests. The preflight compares exact typed local-value/store sequences for each original demand receiver and its derived uninstrumented counterpart. Temporary hooks are restored before timing. The uninstrumented receivers return only the canonical decision; their removed counters are not reported as zero work. The live-node baseline is measured in the same campaign, and no previous nanoseconds enter these comparisons. See [the measurement-overhead protocol](counter-overhead.md) for the exact derivation and preserved semantic checks.

## Read the result

`reproduction.json` records the selection, commands, per-stage states and checks. Logs and new study outputs are adjacent. States distinguish work that passed, failed, was not reached, or was not requested. A failed or interrupted child stops the sequence and leaves later selected stages as `NOT_RUN`. Source files must remain unchanged during execution. The wrapper also refuses an optimistic child receipt when its process exits with a nonzero code. If a coverage or counter-overhead verifier fails after its study writer succeeds, the primary exit code remains intact and `failed_validation_process` records the failing verifier's command, logs and exit code.

`PASS_COMPLETE` requires every default stage to run and pass its stated completion checks. For the witness campaign, completion means every planned request and control has a recorded external outcome. Individual witnesses may be unconfirmed or tools may report an unresolved result; these remain observations in the witness tables, and are not converted into confirmations. The CBMC Boolean-comparison stage separately requires all 804 comparisons to resolve and agree.

The witness stage also requires four subsequent checks. `witness-interoperability/verification.json` reconciles the fresh 804-case campaign with its retained process output and 18 controls. `witness-interoperability/product-equivalence.json` checks the executed source snapshot against its original protocol, invokes executed and current emitters in separate Python processes, and compares both outputs byte for byte with all 804 actual C products. `witness-interoperability/search-statistics.json` analyzes all 594 planned refutations, preserving missing or ambiguous statistics and comparing counters only where both arms confirmed. `witness-input-controls/` contains three additional native executions and CPAchecker calls that replace an input constraint with an out-of-domain value. Each command has a separate log, validation result and process exit code under the witness stage's `followups` field. A failed reconciliation or unexpected input-control outcome fails the stage and prevents later checks from starting. A zero exit from the primary campaign alone cannot complete the witness stage.

The retained witness records include an explicitly registered continuation after GCC rejected a legitimate bitwise-XOR expression through its programmer-intent warning, followed by a separately recorded resume after a directory-creation resource failure. The original failed invocations and completed observations remain available. Native correspondence was repeated under the declared C11 constraint policy for inherited subjects, while pending subjects used that same corrected policy. The final 804 subjects comprise 527 initial completions, 45 completions in the compiler-policy continuation and 232 in the resource-resume segment. All 1,332 native compilation receipts remain available, including the failed compilation and the 527 policy rechecks. Fresh executions use the corrected policy directly; they do not recreate the historical interruptions or claim that those never occurred.

A fresh receiving study should reproduce canonical decisions and deterministic semantic-work counts. It is expected to produce new elapsed times. The analysis reads those newly measured times; it does not copy previously reported nanoseconds into a new experiment. Paper compilation and visual review are performed from the `paper/` directory and are outside this scientific execution entry point.
