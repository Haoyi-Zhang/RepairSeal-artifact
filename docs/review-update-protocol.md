# Empirical update: interpretation and evidence rules

This update adds executable evidence to the delivered artifact. The companion
`paper/` is an unchanged input, including its PDFs. Existing retained campaigns
remain historical records; a recomputation of their summaries is not a new
execution of the external tools.

## Units and provenance

An automatically generated patch is counted as such only when its exact edit or
repaired source comes from an identified public release. A buggy Codeflaws
submission is an original-program control or an existing-source candidate; it
is not relabeled as an automatically generated repair. Repeated patch files,
same-source candidates, candidate/subject combinations, subjects, and distinct
problems are different denominators. Every reported fraction states its unit.

Fixed archive hashes, member paths, source hashes, exact applied edits, retained
test names, and compiler identities make the selection reproducible. Archive
scripts are not required to interpret a result. Unsupported sources, failed
compilations, timeouts, and missing execution are exclusions or inconclusive
records, never semantic counterexamples or successful repairs.

## Failure labels

For a declared finite input set and an executable reference, use the following
operational repair region when a benchmark provides no independent selector:

`R(u) = original is undefined at u OR original exits nonzero OR original output differs from reference`.

The complementary preservation region requires a defined original, zero exit
status, and the declared correct observation.

This is an experimental coding rule based on the original/reference pair. It is
not a recovered developer intention. A reference that is undefined, absent, or
unsupported at a needed point does not authorize a correctness label there.

The primary diagnostic order is candidate definedness, repair-region mismatch,
then preservation mismatch. Where a patch has multiple kinds of failing inputs,
retain all observed labels and a witness for each as well as the ordered primary
label. Mutually exclusive primary counts and overlapping label counts must not
be added together.

`correct` means agreement and definedness on the explicitly declared checked
inputs. It is not whole-program correctness, and it is not an extrapolation to
all int32 values. A finite counterexample is enough to refute such a bounded
claim; a finite acceptance has exactly the domain written in its request.

## Tests that pass despite a defect

Maintain separate outcomes for the repair/training tests, the held-out tests,
and their full published union. Passing the first set while failing held-out
tests is not counted as passing all provided tests. A strict
`tests-pass-but-wrong` observation must retain successful execution against the
complete given test set and a concrete failure on the declared semantic domain.

Two mechanisms are distinct. An additional input can expose an output mismatch
that was not tested. Alternatively, ordinary native executions can produce the
expected output while an undefined source operation remains; in this case the
source fault must be established by an explicit semantic or path-execution
witness. A sanitizer confirmation is retained when the sanitizer detects that
fault class; silence does not prove definedness. The independent path review
for this update's uninitialized-read witnesses is separate from UBSan. A timeout, crash without an explained
source fault, or missing output is not evidence for this latter mechanism.

## Independence and correspondence

Automatic labels and an independent rule implementation can be compared for
agreement. This is implementation agreement, not inter-human agreement. The
number of human annotators is not inferred from the number of checking scripts
or execution roles. Record disagreements and their resolution, and distinguish
an oracle error from a candidate error.

Signed source admission avoids per-case manual unsigned rewrites. Concrete AST
evaluation, symbolic lowering, and native GCC/Clang outputs provide separate
checks. Full and direct receivers share the symbolic frontend, so their mutual
agreement alone does not independently validate that frontend. Native runs
check outputs and sanitizer diagnostics; they do not observe the model's exact
source-branch trace unless separately instrumented.

The new signed compact receiver establishes the submitted violating input. It
does not establish that the input is the canonical least counterexample, and
cannot establish acceptance. Full-vector and direct complete-domain decisions
continue to have the stronger canonical diagnostic contract.

## Limits of the empirical argument

The three obligations were defined before this study. Applying them as a coding
scheme can show which failures occur in the sampled real patches, but cannot
show that they were discovered from those patches or uniquely exhaust all
possible software defects. Definedness is logically implied by guarded repair
and preservation together; retaining it separately supplies diagnostic priority.
The empirical contribution is evidence of the usefulness and observed incidence
of these diagnoses in the named sample.

Selection after inspecting historical evidence is exploratory even when the
new run's domain is frozen before execution. Such cases are useful mechanism
examples, not an unbiased prevalence sample. Same-problem subjects, repeated
student submissions, and repeated repair attempts are dependent observations.

For scaling, a product of observed coordinate cardinalities describes the size
of a Cartesian expansion. It does not assert that all combinations are valid,
defined, or present in the benchmark. Unsupported source arities are reported as
unknown rather than guessed from text or assigned zero.
