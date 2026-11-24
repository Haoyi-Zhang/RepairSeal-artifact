# Independent CBMC comparison on the admitted C sources

`tests/cbmc_comparison.py` checks the finite repair decision with a separate C frontend and SAT-based verification implementation. It passes the receiver-owned C functions to CBMC, without translating RepairSeal's DAG or importing a producer certificate. The comparison concerns the Boolean decision. CBMC counterexamples are not claimed to be the canonical obligation/trace/input minimum required by the RepairSeal direct interface.

## Semantic correspondence

For each admitted request the driver writes the original, candidate and reference strings byte for byte to `original.c`, `candidate.c` and `reference.c`. The wrapper includes those files under separate `f`-renaming macros. It does not normalize their comments, line endings, expressions, control flow or unsigned literals. The same raw guard expression appears in the wrapper. Request admission is performed before any source is written or passed to the external tool; it rejects preprocessor directives, calls, memory operations, loops, signed arithmetic and all other constructs outside the admitted scalar fragment.

The wrapper chooses one nondeterministic unsigned value for every input coordinate. An assumption restricts each coordinate to the exact list of values in its axis, using a disjunction of equality tests. It then executes the candidate on every feasible input. If the repair guard holds it executes the reference and asserts equal results; otherwise it executes the original and asserts equal results. This conditional execution is necessary: undefined behavior of an unselected original or reference is not a failed repair obligation.

The command fixes the C data model to 32 bits and uses C11. Compile-time assertions additionally require a four-byte unsigned type whose maximum value is `4294967295u`. It disables CBMC's default check bundle, then explicitly enables integer division-by-zero and undefined-shift checks. These checks cover the admitted language's potentially undefined numerical operations, including remainder by zero, while respecting C short-circuit and branch execution. Unsigned addition, subtraction, multiplication and valid shifts retain their modular behavior. **Unsigned-overflow checks are not enabled.** The source fragment has no loops; no depth bound, loop-unwinding bound or partial-loop option is supplied.

Under the admitted-language correspondence, successful verification establishes the same conjunction:

- The candidate is defined throughout the specified finite product.
- In the repair region, the reference is defined and the candidate equals it.
- Outside that region, the original is defined and the candidate equals it.

These are the existing definedness, repair and preservation obligations. This argument concerns the admitted sources. It does not establish that a manually mapped source fragment captures every behavior of an external application.

## What this comparison adds

`demand_evaluator.evaluate_demand` computes the comparison decision and the canonical diagnostic using RepairSeal's own frontend, source reconstruction and word rules. CBMC preprocesses and analyzes the retained C directly, then solves its verification conditions using its own implementation. Agreement therefore supplies an external check of this source semantics and whole-domain decision. It is stronger evidence than comparing two traversal schedules over the same reconstructed DAG.

CBMC receives all the same source, guard and finite-domain information. It does not receive the direct result, canonical witness, obligation vectors or any expected output. The strong direct result is computed and stored separately. There is no cross-request semantic cache in either arm of this experiment.

The decision comparison does not make the two output contracts identical. The direct result includes the required least diagnostic; CBMC may report any failing property and a corresponding counterexample. The driver compares only `ACCEPT` and `REFUTED`. It never compares the first CBMC counterexample to the direct minimum, treats CBMC as a witness validator, or claims that a CBMC result is a validated standard verification witness. This experiment is an independent solver comparison.

## Tool and execution record

The retained comparison used CBMC 6.6.0 and MiniSAT from the Debian amd64 packages, with the shared library supplied through the child process's library search path. The runner performs no downloads. The exact executable, dependency and command records are in `data/c-verification/tool-profile.json`.

Each output contains `tool-profile.json`, recording the executable hash, actual version output, shared-library hashes, GCC preprocessor identity, resource-limiter identity, Python/platform information, command flags and resource limits. `protocol.json` records the planned population and input/implementation hashes before execution. The implementation and inputs are hashed again at the end; a changed source or input invalidates a completed comparison.

Each request directory retains:

- The request, exact C source files, guard and generated harness.
- `invocation.json` with the complete argument vector and resource limits.
- The unmodified CBMC stdout JSON and stderr bytes, their hashes and process exit code.
- Parsed property identifiers, descriptions, source locations, statuses and classifications.
- The separate strong-direct result, per-arm wall-time observation and decision comparison.

The default per-process limit is 30 seconds wall time and 2,048 MiB address space. A process group is terminated on timeout, including its preprocessor descendants. The completed campaign used four concurrent workers. These wall times are execution records, not a controlled performance ranking: CBMC includes process startup and preprocessing, the direct time is an in-process API time, parallel workers share resources, and only the direct arm computes the canonical minimum.

## Result classification

`ACCEPT` requires CBMC's final `success`, exit code 0 and no failed or unresolved generated property. `REFUTED` requires final `failure`, exit code 10 and at least one classified failed property. A single actual violation refutes a universal conjunction even when CBMC leaves a later property `UNKNOWN`, which can happen after an earlier undefined operation. Unknown properties never establish acceptance. Unexpected property types, malformed or incomplete output, inconsistent exit/status pairs and tool errors remain `ERROR`. Wall-clock termination remains `TIMEOUT`; no completed verdict is inferred from a partial timeout log.

## Retained results

The completed comparison is `data/c-verification`. All 804 requests produced coherent decisions agreeing with the strong direct evaluator, with no timeout, tool error or status disagreement. Input and implementation fingerprints were unchanged between the start and end of the run.

| Population | Requests | ACCEPT | REFUTED | Unresolved |
|---|---:|---:|---:|---:|
| Core | 380 | 95 | 285 | 0 |
| Grammar | 400 | 100 | 300 | 0 |
| Natural-source domains | 24 | 15 | 9 | 0 |
| Total | 804 | 210 | 594 | 0 |

The 24 natural-source requests include overlapping domains and repeated source versions; they are not 24 independent defects. The generated populations are conformance workloads. The result supports agreement on these finite tasks, not unrestricted correctness of either implementation. The test suite executes 22 independent semantic controls when CBMC is enabled. Their outputs are written under the selected reproduction directory.

## Reproduction

Supply an already available CBMC executable. For an extracted Debian package, also supply the directory containing `libminisat.so.2`. From the project root:

```bash
python artifact/tests/cbmc_comparison.py \
  --cbmc /absolute/path/to/cbmc \
  --library-dir /absolute/path/to/extracted/usr/lib \
  --output /absolute/path/to/fresh-cbmc-results \
  --population core grammar natural \
  --jobs 4 --timeout 30 --memory-mib 2048
```

Omit `--library-dir` for an ordinary installation whose libraries are already discoverable. The default inputs are the 380 core requests, 400 grammar requests and 24 retained natural-source requests. Custom locations are accepted through `--proof-data` and `--natural-data`; the expected population sizes are checked. `--limit` is only an explicitly recorded pilot prefix. A populated or symlink output destination is refused, and the driver refuses Python `-O` and `-OO`.

The runner returns 0 when all requests have coherent, agreeing decisions and its source/input bindings stayed fixed. It returns 1 for a disagreement or changed binding and 2 if some results are unresolved. The summary retains every request in the denominator, including errors and timeouts.

Run the independent semantic controls with:

```bash
CBMC_BINARY=/absolute/path/to/cbmc \
CBMC_LIBRARY_DIR=/absolute/path/to/extracted/usr/lib \
CBMC_CONTROL_OUTPUT=/absolute/path/to/fresh-control-results \
python -m unittest discover -s artifact/tests -p test_cbmc_comparison.py -v
```

The control suite includes unsigned wrap, division and remainder faults, an undefined overwritten assignment, invalid shift distances, skipped references/originals, short-circuit guards, exact-domain exclusion and expansion, bare-CR comments, parameter `f` under macro renaming, and a known failure followed by another property. Boundary tests additionally check preservation of raw source bytes, rejection before external execution, fresh outputs, refusal under optimized Python and incomplete-result handling. Without `CBMC_BINARY`, external execution is explicitly skipped; local harness boundary tests still run.

## Primary documentation

- [CPROVER property checks](https://www.cprover.org/cprover-manual/properties/) documents the separately selectable arithmetic and shift checks.
- [CBMC command-line manual](https://diffblue.github.io/cbmc/man/cbmc.html) documents model selection, default check groups, JSON output and resource-related options. The delivered tool profile records the actual version used, rather than assuming the current online manual is version-identical.
- [CBMC project](https://www.cprover.org/cbmc/) describes its verification role. This comparison uses the verifier directly. Standard-witness production and receiving are documented separately in `witness-interoperability.md`.
