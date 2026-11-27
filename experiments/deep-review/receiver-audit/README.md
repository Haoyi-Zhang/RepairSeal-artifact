# Source-attribute admission audit

## Result

This review found and fixed a concrete gap at the source boundary of the signed
receiver. The historical `codeflaws_int32_bridge.py` admitted declarations such
as `_Alignas(3) int x` and signatures such as `int main(const void)`. Its concrete
interpreter and symbolic receiver silently ignored those attributes. GCC rejected
the corresponding C11 source, while the historical complete receivers could
return `ACCEPT` when all three supplied roles contained the same invalid source.

The correction is in `artifact/current/src/codeflaws_int32_bridge.py`. It rejects
all alignment attributes and requires an unqualified `(void)` parameter form.
Alignment appears in pycparser's `align` attribute and is not traversed by
`Node.children()`, so the check explicitly inspects attributes on every node.
The check includes unreachable code and all original/candidate/reference roles.
Valid C alignments are also outside this closed profile: rejection means
`unsupported`, not a semantic refutation or an undefined-behavior witness.

`artifact/src/` remains the exact historical implementation for reproducing the
frozen studies. `source-versions.json` compares every one of its 16 modules with
the attached original archive. All are byte-identical. `current/src/` contains
the complete inventory and changes only the bridge. No old request, result,
protocol, source binding, expected count, or hash was changed by this fix.

## Executed evidence

| Check | Observed result | Record |
| --- | --- | --- |
| Owned adversarial and positive controls | 18 source programs | `run/controls.json` |
| Unsupported control sources admitted by historical bridge | 14/14 | Same |
| Of those, native C11 compilation rejected | 11/14 | Same, exact compiler commands/stdout/stderr |
| False historical full/direct acceptances among native-rejected controls | 11/11 | Same |
| Current rejection of unsupported controls | 14/14 | Same |
| Positive sources still admitted | 4/4 | Same |
| Native endpoint outputs on positive sources | 20/20 match | Same |
| New regression test methods | 6 passed | `test-run.json` |
| Existing signed receiver/frontend test methods under current bridge | 43 passed | `current-compatibility-tests.json` |
| Historical source inventory | 16/16 byte-identical to original ZIP | `source-versions.json` |

The three unsupported controls that compile successfully are local alignments
`_Alignas(0)`, `_Alignas(8)`, and `_Alignas(int)`. Their rejection is conservative
profile narrowing. They must not be included in the 11 native-rejected controls.
The four positive controls cover `(void)`, an empty parameter list, the admitted
two-parameter main form, and attribute words occurring only in comments. Each
was run natively at `INT_MIN`, `-1`, `0`, `1`, and `INT_MAX`.

The existing suite checks signed arithmetic and definedness, exact-point
membership, compact request binding, trace tampering, nonleast witnesses,
reference faults, source header admission, and deterministic diagnostic rules.
Its nested historical determinism subprocesses retain their original behavior;
this is compatibility testing, not a rerun of every retained scientific study.

## Retained-source compatibility census

The audit reads every `.c` member under `RepairSeal_TOSEM/artifact/` in the
original attached ZIP, deduplicates by byte hash, and parses each unique source
with both bridge versions. It found **8,659 occurrences / 3,336 distinct source
byte strings**. Of the distinct sources, **22** were admitted by the historical
closed signed profile. All **3,336** retained their admission result and,
when admitted, their AST/interface identity. No retained source changed status.

These are source-file counts, not independent bugs, repairs, or full semantic
executions. Most retained C files are generated verifier programs outside this
closed profile. The external Codeflaws source archive is not part of the
delivery and is not covered by this compatibility census. Its record is
`run/retained-source-census.json`, including original archive hash and a
representative archive member for every source hash.

## Reproduction

From `artifact/`, with the declared Python dependencies and GCC available:

```sh
python3 -B -m unittest discover -s tests -p test_source_attribute_admission.py -v
python3 -B experiments/deep-review/receiver-audit/run_audit.py \
  --output /path/to/new-source-audit
python3 -B experiments/deep-review/receiver-audit/verify_audit.py \
  --output /path/to/new-offline-verification.json
```

Add `--archive /path/to/original-delivery.zip` for the optional retained-source
census. The driver requires a new output directory, compiles only the owned
control strings, and never compiles or executes source files read from that ZIP.
`--bridge` and `--preimage` allow explicit version selection; defaults are the
current bridge and the retained historical preimage. The dedicated unittest
also accepts `REPAIRSEAL_CURRENT_BRIDGE_PATH` and scopes module redirection to
each test, leaving the historical suite's module binding unchanged.

`verify_audit.py` needs neither a compiler nor the original ZIP. Its callable
`verify(audit_dir)` checks `audit-manifest.json`, both source inventories and
run source bindings, then freshly recomputes the 18 source-admission outcomes,
36 legacy full/direct decisions, eight current positive decisions, 28 current
unsupported-source rejections, and 20 model-to-retained-native output
comparisons. It reduces the retained native/census receipts without claiming
that the compiler or original archive census was rerun. As elsewhere in this
artifact, hashes are integrity bindings, not authentication against someone
able to replace the manifest and the data together.

`run/environment.json` records actual compiler identity, Python and pycparser
versions, timestamps and source hashes. `source-hardening.patch` is the complete
bridge change. `initial-reproducer.json` retains the four minimal examples that
first demonstrated the gap, before the larger controlled audit.

## What this establishes

Source hashes bind bytes; they do not establish that a frontend correctly admits
and models those bytes. A trusted source-admission layer must validate attributes
and signatures as well as the statement/expression tree. The new controls catch
one specific failure of that requirement and the current receiver rejects it
before returning a semantic result.

This audit used one available native compiler. No Clang, CBMC or CPAchecker
campaign was run here. The controls are constructed regression cases, not
observations about the incidence of these features in real APR patches. The
finite compatibility census does not prove the whole frontend sound; source
admission remains part of the trusted implementation.
