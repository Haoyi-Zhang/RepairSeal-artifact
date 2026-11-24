# Coverage of original signed-program test extensions

This study asks whether an acceptance on the original repair inputs can cover the original held-out inputs using the paper's sufficient support criterion. It uses all 739 retained candidate–subject combinations, reconstructed from the verified Codeflaws archive and normalized corpus. Candidate selection depends on source eligibility and interface compatibility. No input is added, changed or selected by coverage or by the enlarged-domain result.

For every reconstructed obligation, the driver derives global syntactic input support from the circuit. Bottom-up propagation and a separate backward traversal must agree. It projects the actual repair and union tuples onto each support; it never replaces correlated tuples with a Cartesian product. Coverage requires every union projection to occur among the repair projections. The full coverage record is written before union outcomes are joined, and its content is checked again afterward.

## Results

All 1,478 Boolean stage results agree with the retained signed-contract experiment. The population contains 95 own-reference controls, 95 own-original controls and 549 cross-source combinations. Repair acceptance holds for the 95 own-reference controls and 325 cross-source combinations, giving 420 cases to which acceptance reuse could apply.

Every one of these 420 unions contains a new full input tuple. None satisfies support coverage. All have at least one nonempty syntactic obligation support; none has all three roots already folded to literal true. In 418 cases, an obligation support contains every input coordinate. The remaining two are own-reference controls for problem 513-A: their four-input programs have obligation support on the first two coordinates, but the union introduces new pairs on those coordinates as well.

Uncovered inputs do not imply an incorrect repair. Fresh union evaluation retains 328 of the 420 acceptances and refutes 92; the refutations are all cross-source combinations. These results establish no natural opportunity for this support criterion on the observed held-out extensions. They also show why the controlled beyond-containment examples do not establish a corresponding benefit on these programs. Nonempty syntactic support is a conservative dependency description, not a proof that the predicate changes with every included input.

This is an applicability study of the sufficient criterion. It does not implement a signed-domain history consumer or measure a receiving-time saving.

## Retained records

`experiments/signed-coverage/` contains the declared protocol, all 739 coverage records before the union-result join, the corresponding complete records afterward, role and problem aggregates, and the independent verification result. Each record retains the circuit nodes, obligation roots, input order, exact point sets, derived supports and missing projected keys. It therefore supports structural and Boolean recomputation without the source archive. Original C source strings are not included in these records.

`tests/verify_signed_coverage_study.py` imports neither the study writer nor the receiver. It recomputes root supports by graph traversal, evaluates the retained circuit's total word rules on every actual point, checks the projections and root classifications, reconciles the source/point identities and stage outcomes with the reference records, and recalculates all aggregates. This verifies the retained derivation; the separate native experiments test correspondence to C execution.

## Reproduction

From the artifact directory, provide the normalized corpus, its verified external archive, and the retained signed-contract record directory:

```sh
python3 -B tests/signed_coverage_study.py \
  --corpus PATH_TO_NORMALIZED_CORPUS \
  --archive PATH_TO_VERIFIED_ARCHIVE \
  --reference PATH_TO_SIGNED_CONTRACT_RECORDS \
  --output NEW_RESULT_DIRECTORY
```

The result directory must be new. The driver checks source, corpus, archive and reference-record continuity. Recompute an existing result without the external archive using:

```sh
python3 -B tests/verify_signed_coverage_study.py \
  --study experiments/signed-coverage \
  --reference PATH_TO_SIGNED_CONTRACT_RECORDS
```

The optional verifier `--output` argument writes its report to a new file. Both commands require assertions to remain enabled.
