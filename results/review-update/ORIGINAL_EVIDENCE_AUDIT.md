# Preservation of the originally supplied project

The first audit reads the original attached `RepairSeal_TOSEM(2).zip` directly
and compares every member with the updated project. It does not use the earlier
extracted copy as the source of truth, and it does not copy the ZIP into the
deliverable.

The supplied ZIP has SHA-256
`9481ba49b8d3f122f590606914a136839b0e484e2f8798fd8a6fdc554f4b4b1d`,
80,716,914 compressed bytes, 63,881 files, and 567,232,880 uncompressed bytes.

`original-evidence-integrity.json` is the source-comparison receipt. Its `paper`
section records an original and current SHA-256 for each of the 71 paper files.
The historical evidence check covers all original files under these directories:

| Original directory | Original files |
| --- | ---: |
| `artifact/data/` | 13,433 |
| `artifact/proof-data/` | 2,270 |
| `artifact/experiments/` | 47,367 |
| Subtotal requested by the preservation audit | 63,070 |
| `artifact/results/` | 458 |
| `artifact/evaluation-record/` | 16 |
| Total historical scientific evidence | 63,544 |

All 71 paper files and all 63,544 historical scientific-evidence files match the
original bytes. No originally supplied file was deleted. New experiment and
report files have no counterpart in the ZIP, so they are not confused with edits
to old results.

`original-evidence-manifest.json` retains the original SHA-256 and byte length for
the 63,615 protected paper/evidence files. It also retains the original expected
result fields from the ZIP. Its bytes are bound by the source-comparison receipt,
and it supports verification without the original ZIP. Additions to
`expected-results.json` are allowed; changing or removing an original expectation
is rejected.

`original-code-differences.diff` records the code/documentation differences at the
time of the source comparison. Changed code is not silently treated as historical
data. The original-evidence hash manifest remains stable while approved code and
documentation are updated. The source-comparison receipt is a dated snapshot;
code edited subsequently should be reviewed in a newly generated diff. Hashes
alone cannot prove the semantics of arbitrary code edits. In the initial reviewed
verifier diff, the old packaged and fresh checks remained present, the new update
checks were added, and numeric/container comparison was made stricter.

## Offline preservation check

From `artifact/`:

```sh
python -B tests/audit_original_evidence.py --verify-record
```

This requires no archive, compiler, network, or toolchain. It rehashes every
protected current file and checks the original expectation fields. It reports
missing files, altered bytes, nonregular paths, duplicate manifest paths, or
changed old expectations as failures.

The importable entry point is:

```python
verify(root=None, record=None)
```

`root` denotes the artifact directory. The returned mapping contains `status`,
`errors`, `files_checked`, and per-directory counts. A different result output can
be retained with `--output`; it should not replace the source-comparison receipt.

## Repeat the source comparison

With the original ZIP available outside the project:

```sh
python -B tests/audit_original_evidence.py \
  --original-zip /path/to/original.zip \
  --output results/review-update/original-evidence-integrity.json
```

This refreshes the receipt, protected manifest, and code diff. The final package
should continue to exclude the original ZIP, downloaded research archives,
compiler installations, virtual environments, and Python caches.
