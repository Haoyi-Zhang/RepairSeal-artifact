# Original-package baseline records

These are new executions of the **unchanged attached project**, extracted into
separate disposable directories. No paper build ran in the delivery tree.
`provenance.json` binds the input archive. `summary.json` derives the baseline
status from the evaluator reports and preserves failures as failures.

The initial environment had two mismatched Python package versions, no Clang,
and no usable LaTeX format tree. It also needed an explicit writable `TMPDIR`
outside `artifact/`. `initial/` and `pinned-no-clang/` retain these unsuccessful
attempts; none is reported as successful scientific execution.

After the Python/Clang/temp-directory fixes, `with-clang/` records successful
preflight and smoke checks, 36/36 packaged-result checks, and the complete fresh
analysis, functional, demand and header stages. Its original 366-test suite
passes with one unavailable-CBMC skip. Its 55/55 fresh result checks pass. That
core command remains `FAIL` because it was launched before the TeX/font setup
and its paper step failed. `paper-ready/` then records a separate successful
paper evaluation with the complete environment, producing 39 and 18 pages.

The official Debian package manifests, archive hashes and native Clang smoke
execution are retained next to these reports. The subsequently installed CBMC
6.6.0 and Clang 19.1.7 executable identities match the original artifact's
retained identities. TeX packages, fonts, binaries and installation directories
are not part of the deliverable.

`run_baseline.py --artifact <disposable-project>/artifact --output <new-path>
--label <label>` records all six requested gates. Source the appropriate local
tool environment first and provide a writable `TMPDIR` outside the project.
The evaluator's original interface has no `--paper-dir` option; copying the
complete `artifact/` plus companion `paper/` layout avoids editing the supplied
paper while exercising the unchanged evaluator. Every evaluator invocation
uses a new output directory. The runner refuses its own delivery artifact.

The log bundle retains evaluator/reproduction reports, stdout/stderr, fresh
result verification and deterministic summaries. Large duplicate regenerated
certificate bodies are omitted from this log bundle; their production remains
fully specified by the existing reproduction driver. These records do not
represent a fresh full external CBMC/CPAchecker campaign. The final updated
project's regression records are separate from this original-package baseline.
