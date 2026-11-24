# Packaged evaluation record

This directory contains the public, path-normalized record of the final local artifact acceptance run. It is evidence, not an input to the scientific implementation.

- `core-evaluation.json`: unified local `core` result.
- `fresh-reproduction.json`: fresh analysis, functional, demand, and header-stage report.
- `key-result-trace.json`: exact named-field and record-binding checks.
- `delivery-audit.json`: claim paths, licenses, dependencies, figure bindings, caches, symlinks, and font-distribution audit.
- `complete-unit-suite.log`: transcript of the complete unit suite (`python3 -B -m unittest discover -s tests -p 'test_*.py' -v`). The transcript of the original acceptance run was not retained (its summary, 366 tests with two skips, is in `core-evaluation.json`); this file is a later re-run of the same command on a standalone copy of the artifact (Ubuntu 24.04 under WSL2, CPython 3.12.3, pinned requirements): 366 tests, `OK (skipped=2)`, the two skips naming the CPython 3.12.14 receipt identity and the external CBMC binary.
- `fresh-results/`: selected exact fresh outputs used by the checker.
- `paper-evaluation.json`: final paper rebuild after the artifact-language synchronization.
- `external-gate.json`: explicit `FAILED_PRECONDITION` result with zero scientific studies started.
- `clean-install-attempt.json`: the isolated installation attempt, distinguished from scientific execution.

Paths are normalized to `$PROJECT`, `$CORE_OUTPUT`, `$PAPER_OUTPUT`, `$PREFLIGHT_OUTPUT`, `$EXTERNAL_OUTPUT`, and `$TMP`. Scientific values are not changed. The full evaluator can regenerate unsanitized run records in a new evaluator-owned output directory.
