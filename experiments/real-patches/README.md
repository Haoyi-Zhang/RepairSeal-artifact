# Published C patch campaign

This directory contains a new execution study of published Angelix repair
candidates. It uses actual published unified diffs, not newly invented repairs.
The original paper and all older experiment records remain separate.

## Provenance and license

The source is Xuan-Bach D. Le's [Zenodo record 1012686](https://doi.org/10.5281/zenodo.1012686),
*Overfitting in semantics-based program repair*, published 16 October 2017.
The deposited metadata states **CC BY 4.0**. The complete fetched metadata is
retained in `source-audit/angelix-zenodo.json`. The original IntroClass source
notice is also retained in `source-audit/introclass-license.txt` (**BSD 3-Clause**,
Copyright 2015 ProgramRepair). These third-party materials keep those licenses;
they are not relicensed under RepairSeal's own license. Reconstructed candidate
files are exact applications of the released diffs. Attribution, original source
paths, patch identities, and the fact of reconstruction are retained in
`corpus.json`. See the [original IntroClass project](https://repairbenchmarks.cs.umass.edu/)
and its [license](https://repairbenchmarks.cs.umass.edu/IntroClass/LICENSE).

The outer ZIP is `esemdata-20171016T065923Z-002.zip`, 1,088,378,260 bytes,
MD5 `8347801dc54761bbbf1a9f8dc156e3f2` (the depositor's checksum), and SHA-256
`65814e170d5887074b04cbb0dee958f078b12e5da49671364a6f7f2a6f7f7c7e`
(computed over the complete new download). The selected inner archive is
`esemdata/CVC4/instrumented_IntroClass_0.5_4.zip`, 99,566,658 bytes, SHA-256
`c58e955a9cc417ecfc8e9b7512de1391105b07a07b0b65231662e96f6d67c6d1`.
Neither complete archive is redistributed here.

The inner directory contains patches with historical dates from different
runs. Its name is not sufficient to attribute every patch to one synthesis
configuration. Therefore the tool column is **Angelix (published patch
inventory)**, and the synthesis configuration is explicitly not attributed.

The source survey also inspected the original IntroClass repository at commit
`897fd9ca72a4cd2fa0884b6d2d9d09a95603cb65`. Its GenProg/AE logs require a
GenProg/CIL reconstruction; they are not mistaken for ready-to-execute patches.
Codeflaws' repository has a MIT notice, but this alone does not establish that
the externally hosted source archive is covered by that notice. No Codeflaws
source bytes are redistributed by this campaign.

## Sampling and denominator

`protocol.json` freezes the selection rule before outcomes are measured. It
enumerates the median and smallest `src/*.patch` members of the selected inner
archive. `inventory.json` contains every occurrence and every exclusion.
Application must match the original hunk positions and every context line,
without offsets or fuzz. Duplicate `(original source SHA-256, applied candidate
SHA-256)` pairs count once. For each distinct original source, the first two
candidate hashes in lexical order are selected. This is a deterministic,
bounded sample, not a random sample of all C repairs. `all-unique-candidates.json`
also records candidates omitted by the fixed two-per-original sampling rule.

The selected sample includes unsupported and non-compiling cases; those are
reported as `other`. They are not silently removed from the denominator.
Duplicate occurrences are provenance, not independent observations.

## What is executed

`sources/` contains unchanged original and reference bytes, and exact applied
candidate bytes. `patches/` contains the released diffs. All original blackbox
and whitebox inputs and outputs are retained under `tests-data/`. The ordinary
test criterion follows the published Angelix numeric output oracle, retained in
`upstream-oracles/`: candidates must print precisely the expected integer and
newline. The process must also terminate with status zero. Extra output is not
silently removed. Teacher reference programs retain their original stdin and
prompt interface; the known answer after the prompt is the oracle's declared
scalar observation.

The published candidate/original wrappers read decimal integer command-line
arguments and use the published identity macro `ANGELIX_OUTPUT`. Some omit the
standard declaration of `atoi`; native compilation explicitly supplies
`-include stdlib.h`. No source byte is silently rewritten. GCC and Clang each
compile every selected unique source in plain and UBSan modes. Tool identities,
flags, compiler diagnostics, binary hashes, exit statuses, raw stdout/stderr,
and stream hashes are retained in `records/`.

The declared finite evaluation set is the union of every supplied test input
and the complete Cartesian grid: median `{-2,-1,0,1,2}^3`; smallest
`{-1,0,1,2}^4`. `points.json` is the exact enumerated set. These grids exercise
ties, all relative orderings, zero, and negative values. A bounded `correct`
label makes no assertion about inputs outside that union, large-integer
overflow, or general production software.

## Labels and definedness

`scalar_semantics.py` independently executes a closed signed-int32 source
profile. It does not use the RepairSeal circuit or receiver. It checks all
syntax, keeps uninitialized variables uninitialized, implements C truncating
division and short-circuit evaluation, and reports arithmetic failures.
Every defined semantic observation is compared to both native compilers, in
both plain and UBSan modes. Unsupported source syntax, compilation problems,
reference failures, or correspondence mismatches yield `other`.

UBSan does not establish the absence of undefined behavior and does not detect
all uninitialized reads. Uninitialized-read labels are established by the
closed source execution, with a read site and input. Raw native executions are
retained alongside them; accidental numerical agreement on such an execution
does not turn undefined C behavior into a defined result. Read-site line numbers
refer to the checked parser representation after removal of the verified
identity preprocessor wrapper.

The repair region is operationally defined as inputs where the original is
undefined, prints a different result from the reference, or terminates with a
nonzero status. The preservation region
contains the remaining inputs where both are defined and agree. This is a
reference-based experimental definition, not an inference of the developer's
unstated intended repair region. A reference failure cannot be used to infer a
candidate failure.

The nonexclusive labels `definedness`, `repair-region`, and `preservation`
are reported separately. O1/O2 witnesses are defined candidate executions;
O0 witnesses are reported as O0. The primary table uses the fixed precedence
O0, O1, O2, then bounded `correct`. This gives an additive primary table without
discarding overlap. `tests-pass-but-wrong` is an overlay requiring **all**
published blackbox **and** whitebox cases to pass on **both** plain compilers,
and a concrete finite-domain violation. Both its sample denominator and its
all-tests-passing denominator are reported.

No human inter-annotator agreement was measured. Any independent automated
review is reported under its actual method and must not be described as two
human annotators.

## Reproduce and verify

From the artifact root, with the pinned dependencies, GCC, and Clang available:

```sh
python3 -B experiments/real-patches/verify.py
python3 -B -m unittest discover -s tests -p test_real_patch_study.py -v
```

The offline verifier requires no network or external compiler. It re-applies
the exact diffs, replays the closed source observations, verifies full native
coverage and stream hashes, rebuilds all labels and witnesses, and recomputes
every reported count. It also checks the retained file hash inventory.

The final file inventory binds the collection/validation implementations and
all three new unit-test modules as well as all retained data. The separate
`independent_review.py` uses a mathematical median/minimum reference and native
receipt set partitions; `independent-review.json` reports its measured agreement.
It shares the retained definedness flags, so it is not a second semantic proof
of O0. Run it independently with:

```sh
python3 -B experiments/real-patches/independent_review.py
```

The additional `independent_definedness.py` has its own narrow path executor.
It independently confirms one concrete uninitialized-read witness for each of
the nine O0-labelled patches, recording declarations, actual assignments,
taken branches, and the read site in the original source. It does not import
the primary interpreter or classifier. This establishes the existence of
those nine failures; it does not independently reclassify every input in the
finite domains. `independent-definedness.json` records its result, and four
negative controls test that initialization and branch changes remove the
reported failure and that unsupported syntax is rejected. Run it with:

```sh
python3 -B experiments/real-patches/independent_definedness.py
python3 -B -m unittest discover -s tests -p test_independent_definedness.py -v
```

Independent implementation review corrected four general profile boundaries;
`source-audit/review-fixes.json` records them. After those corrections, the entire
native and semantic campaign was run again from the immutable source copies in
`executed-sources/`. `collection-identity.json` records the pre-execution file
hashes, actual entry-point command, Python identity, completion status, and
post-execution verification of the frozen bytes and inputs. The delivered
`records/` are from this final complete execution, not from the preliminary run.
The snapshot copies of the collector, interpreter, and validators are the actual
bytes used by that execution. Supporting downloader and regression-test sources
are separately identified. The preliminary run is retained only as hashes and
counts in `source-audit/prior-collection-summary.json`; its absent contemporaneous
script snapshot does not apply to the delivered final run. Labels and summary
counts were unchanged by the full rerun. Raw undefined-behavior outputs need not
be identical across runs and are never used as evidence of definedness.

The independent O0 witness check was added after that complete campaign. The
current `verify.py` subsequently extended only its file-inventory allowlist to
bind that check's test module. The native collector, source interpreter, label
computation, and frozen executed validator were not changed. This small
post-collection validator difference is recorded in
`source-audit/post-collection-review.json`.

For a fresh native campaign, copy the artifact tree to a new output location
(preserving the three unit tests bound by relative path), remove the copied
`experiments/real-patches/records/`, and remove `collection-identity.json`,
`independent-review.json`, and `independent-definedness.json` from its
`experiments/real-patches/` directory (those identities describe the retained
run). From the original artifact root, run:

```sh
python3 -B experiments/real-patches/study.py run --root /absolute/fresh-artifact/experiments/real-patches --jobs 4 --gcc /path/to/gcc --clang /path/to/clang
```

To rebuild corpus selection, use a new empty output directory and the complete
downloaded archive:

```sh
python3 -B experiments/real-patches/study.py prepare --archive /path/to/esemdata-20171016T065923Z-002.zip --output /absolute/new-corpus
```

The checksum-verifying downloader is:

```sh
python3 -B experiments/real-patches/fetch_source.py --output /absolute/external/esemdata.zip
```

`summary.json` and `labels.json` are generated from execution records. They are
not hand-entered result tables. `verification.json` records the collection
run's offline verification outcome.
