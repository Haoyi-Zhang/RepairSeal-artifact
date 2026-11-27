# Final validation of the review update

`summary.json` is the fixed entry point. It is derived from completed execution records; the last attempt passes all six requested gates. Previous attempts retain their original status, stdout, stderr, commands, timestamps, exit codes, generated receipts and source bindings.

## Final gate results

| Gate | Status | Exit code | Elapsed seconds |
| --- | --- | ---: | ---: |
| preflight | PASS | 0 | 19.05 |
| smoke | PASS | 0 | 27.52 |
| expected-results | PASS | 0 | 11.98 |
| core | PASS | 0 | 976.77 |
| paper | PASS | 0 | 226.73 |
| audit-data-integrity | PASS | 0 | 77.61 |

The packaged result check passes **203/203** checks. The fresh core result check passes **222/222** checks. The smoke suite executes **47 tests, 0 skipped**; the formal complete suite executes **422 tests, 0 skipped**.

The complete suite record is in `attempt-2/core/evaluation.json` and its named logs. An earlier separately run unit precheck is not substituted for this formal suite.

## Preserved unsuccessful attempt

Attempt 1 failed in the functional stage of the core gate. `round2 reproduction failed: 4` identifies command index 4, not four failed tests: one of eight original driver-contract tests failed because the exact declared source-addition inventory did not yet include the new `src/int32_refutation.py` module. The other five top-level gates passed. `attempt-1/diagnosis.json` identifies the failed test and preserves its source preimages. No failure has been rewritten as a success.

The integration fix declares the one new path and pins its exact SHA-256. Historical source hashes, scientific fields, the existing three source additions, and receiver identity checks remain exact. Negative controls reject unknown modules and changes to the declared module. The successful attempt reruns all six gates from new full project copies.

## Paper preservation and build isolation

All **71** delivery paper files match the originally supplied ZIP byte for byte. `paper-original-integrity.json` records the input ZIP hash and every original/current paper file hash. No paper build command ran inside the delivery tree.

Core and standalone paper evaluation use two separate full project copies. The standalone rebuilt outputs have 39 main pages, 18 supplementary pages, and 5 atlas pages. Their hashes and byte counts are retained in `attempt-2/paper/evaluation.json`; the separate direct PDF inspection is recorded beside it. These generated PDFs do not replace the original paper. Disposable project copies may be removed after successful capture; original absolute execution paths remain in the logs.

## Environment and rerun

The evaluator reports record Python package versions and GCC/Clang executable identities. The complete run used the pinned dependencies, a writable temporary directory outside the project, and the locally provisioned TeX/font environment. Tool binaries and fonts are not redistributed in this record bundle. CBMC 6.6.0 was available for the unit semantic controls; these gates do not claim a fresh full CBMC/CPAchecker external campaign.

With the required environment configured, run:

```sh
python3 -B artifact/results/review-update/final-validation/run_final_validation.py \
  --source /absolute/path/to/RepairSeal_TOSEM \
  --work /absolute/path/to/a/new-disposable-directory
```

The work directory must be new and outside the source project. The runner executes each gate with a new output directory and never overwrites earlier evidence. `collect_final_validation.py` checks the completed results and original ZIP before moving attempt report directories into a new archive directory; its `--help` lists the arguments.

## Execution-only compiler links

The four temporary `fresh-core/tool-bin/{gcc,clang}` symbolic links from the
two attempts are not distributed. Their original targets and exclusion reason
are retained in `../delivery-audits/packaging-exclusions.json`. These links were
execution infrastructure, not result records; compiler identities, scientific
outputs, commands, and original log bytes remain unchanged. The reproduction
driver creates new compiler links in each new run output.
