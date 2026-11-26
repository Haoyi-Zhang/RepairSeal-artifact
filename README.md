# RepairSeal: artifact

Artifact for the paper **Receiving Obligations Determine the Computational Value
of Repair Evidence** by Huaijin Ran, Haoyi Zhang, Xunzhu Tang and Kisub Kim (submitted to ACM TOSEM).

RepairSeal implements receiving contracts for finite repair validation. A
request fixes source semantics, a candidate repair, repair/preservation/
definedness obligations, a finite input domain, and the result the receiver
must return. The artifact compares three distinct settings:

- a complete decision or complete materialized record;
- confirmation of a supplied violating input; and
- reuse of a prior acceptance when support coverage authorizes it.

The settings deliberately do not share a single success criterion. Detecting
one failure is not a complete-domain acceptance result, and failure of a
coverage check is `no conclusion`, not a refutation.

## Repository layout

| Path | Contents |
| --- | --- |
| `evaluate.sh`, `evaluator.py` | Evaluator entry point (`preflight`, `smoke`, `core`, `external`, ...). |
| `reproduce.py` | Lower-level scientific driver; every stage writes to a new directory. |
| `verify_expected_results.py`, `expected-results.json` | Exact checks of the numbers reported in the paper against named record fields and record hashes. |
| `src/` | Receivers, checkers, producers, demand evaluator, domain transport. |
| `tests/` | Unit tests (366) and the study drivers invoked by `reproduce.py`. |
| `data/`, `proof-data/`, `experiments/`, `results/` | Retained study records (inputs, outputs, protocols, hash inventories). |
| `public-data/`, `inputs/` | Small public inputs (Codeflaws metadata, CEIL_DIV source, fixture requests). |
| `figures/` | Figure generators used by the paper build (see `figures/README.md`). |
| `docs/`, `proofs/`, `formats.md` | Protocols, proof notes, and certificate formats. |
| `claim_evidence_ledger.csv` | Claim-to-evidence map (paths relative to this directory). |
| `evaluation-record/` | Path-normalized record of the authors' final acceptance run. |
| `audit_delivery.py`, `audit_data_integrity.py` | Packaging audit (paths, licenses, caches, bindings) and parse check of every data file (`python3 -B audit_data_integrity.py`; 10-25 s on a local Linux file system, about 7 min on a Windows drive mounted in WSL; prints counts and `"errors": []`, exit code 0). |
| `external-inputs.json`, `external-stages.json`, `external_resources.csv` | Identities and sources of external tools/data that are not redistributed. |
| `licenses/`, `THIRD_PARTY_NOTICES.md`, `LICENSE` | License texts. |

## Requirements

- **OS:** Linux x86-64. Every mode below (including `paper`, `external` and `all`)
  was run end to end on **Debian 13 "trixie"** (glibc 2.41, the environment of the
  retained runs) under WSL2; the local modes were also run on Ubuntu 24.04. The
  local stages need a POSIX host (`resource`, process groups, executable bits);
  native Windows is not supported (about 20 unit tests fail there for that reason).
  macOS was not tested.
- **Python 3.12** with the pinned packages in `requirements-evaluator.txt`
  (`pycparser`, `matplotlib`, `numpy`, `PyMuPDF`, `pillow`). The authors' retained
  runs used CPython 3.12.14 (needed for `external`, see below); other 3.12.x
  interpreters work for the local modes.
- **GCC and Clang** (two distinct executables) for the `functional` and `headers`
  stages and the Codeflaws stages (retained runs: GCC 14.2.0 and Clang 19.1.7 from
  Debian 13; the local stages were also checked with GCC 13.3 and Clang 20.1).
- **External campaigns only:** CBMC 6.6.0, CBMC 6.11.0, CPAchecker 4.3 with Java 21,
  `prlimit`, and the pinned Codeflaws archive (identities in `expected-results.json`
  and `external-inputs.json`). None of these is bundled; see
  [Installing the external tools](#installing-the-external-tools).
- **Paper build only** (`paper` mode, paper step of `core`): `pdflatex`/`bibtex` with
  the acmart dependencies, `pdffonts`/`pdfinfo` (poppler), and an installed Times New
  Roman face for the figures (STIX mathematics is bundled with matplotlib; see
  `figures/README.md`).
- **Hardware/disk:** any recent laptop; about 0.7 GB for the repository plus a few
  hundred MB for outputs. The external tools add about 0.8 GB (CBMC 6.11.0, CPAchecker,
  Codeflaws archive) and an external run writes about 0.5 GB; the TeX/font packages
  for the paper build take about 2.5 GB; the external campaign used about 3 GB RAM
  (four CPAchecker workers with the default 1.2 GB heap limit). No GPU, no network access needed after installation.

## Installation

```sh
cd <this repository>
python3.12 -m venv ../repairseal-venv          # keep the venv outside the repository
. ../repairseal-venv/bin/activate
python -m pip install -r requirements-evaluator.txt
```

`requirements.txt` (pycparser only) suffices for the stdlib-only kernel and the
signed-C frontend; `requirements-evaluator.txt` adds the plotting/PDF packages.
If `python3.12` is not available, `uv python install 3.12.14` (https://github.com/astral-sh/uv)
provides the exact retained interpreter in user space.

### Installing the external tools

Only `paper`, `external` and `all` need these. The commands reproduce the
environment of the retained runs (no root needed except for `apt-get`; on Windows,
an official Debian 13 root filesystem can be imported as a per-user WSL distribution
with `wsl --import`):

```sh
# Debian 13 packages: GCC 14.2.0, Clang 19.1.7, CBMC 6.6.0, Java 21, TeX Live 2024, poppler
# (figure text: Times New Roman, e.g. contrib's ttf-mscorefonts-installer; see figures/README.md)
sudo apt-get install --no-install-recommends gcc-14 gcc clang-19 clang libc6-dev cbmc \
  openjdk-21-jre-headless util-linux unzip python3-venv poppler-utils fontconfig \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
  texlive-fonts-extra texlive-bibtex-extra texlive-science texlive-pictures texlive-plain-generic
# CPython 3.12.14 (historical receipt replay)
uv python install 3.12.14                    # then: PY312=$(uv python find 3.12.14)
# CBMC 6.11.0 (witness producer): official release package, unpacked without installing
curl -LO https://github.com/diffblue/cbmc/releases/download/cbmc-6.11.0/ubuntu-24.04-cbmc-6.11.0-Linux.deb
dpkg-deb -x ubuntu-24.04-cbmc-6.11.0-Linux.deb ../cbmc-6.11.0   # -> ../cbmc-6.11.0/usr/bin/cbmc
# CPAchecker 4.3 (official Zenodo record 24339049)
curl -L -o CPAchecker-4.3-unix.zip https://zenodo.org/api/records/24339049/files/CPAchecker-4.3-unix.zip/content
unzip -q CPAchecker-4.3-unix.zip -d ..       # -> ../CPAchecker-4.3-unix/bin/cpachecker
# Codeflaws archive (265,695,532 bytes, sha256 2673fc16...2eea82b11), fetched and verified
python3 -B tests/fetch_codeflaws.py --output ../codeflaws.tar.gz
```

With these, the tool identities match the retained records exactly: `/usr/bin/cbmc`
(sha256 `346f5ff6...e49e498`), the unpacked CBMC 6.11.0 binary (`a62af25d...382995`),
`cpachecker.jar` (`8bcef651...e1e2b`), `x86_64-linux-gnu-gcc-14` (`a23ecab8...635f`)
and `llvm-19/bin/clang` (`0a3c5593...41ca1a`).

All commands below are run from the repository root. Every evaluator and driver
invocation needs an output path that does not exist yet and lies outside the
repository; existing evidence is never overwritten. (Without `--output`, the
evaluator writes to `../evaluation-output/<UTC>-<mode>/`.)

## Quick check (about 1 minute)

```sh
./evaluate.sh preflight --output ../rs-out/preflight   # files, pinned versions, hygiene, 36 result checks, delivery audit
./evaluate.sh smoke     --output ../rs-out/smoke       # receiving, transport, header-admission, journal, ledger tests
python3 -B verify_expected_results.py --output ../rs-out/verify
```

Expected: the two evaluator calls print `{"status": "PASS", ...}`, and the
checker prints `{"status": "PASS_KEY_RESULT_SOURCE_TRACE", "checks": 36, "failures": 0, ...}`.
Each evaluator run stores commands, environment, logs, and results in
`<output>/evaluation.json`. Missing external tools do not fail `preflight`.

## Reproducing the paper's results

| Paper result | Command | Output | Expected | Time |
| --- | --- | --- | --- | --- |
| All bound numbers in `expected-results.json` (780 requests, transport targets, witness, coverage, timing and overhead medians) | `python3 -B verify_expected_results.py --output ../rs-out/verify` | `../rs-out/verify/result.json` | `PASS_KEY_RESULT_SOURCE_TRACE`, 36 checks | seconds |
| 780 canonical complete decisions; 5,308,130 support-keyed vs 39,276,283 live-node semantic values (fresh execution) | `python3 -B reproduce.py --checks demand --output ../rs-out/demand` then `python3 -B verify_expected_results.py --output ../rs-out/v-demand --fresh-demand ../rs-out/demand/unsigned-demand` | `reproduction.json`, `unsigned-demand/summary.json` | `PASS_SELECTED_CHECKS`; then `PASS_KEY_RESULT_SOURCE_TRACE`, 44 checks | ~2-3 min |
| Timing, coverage, counter-overhead and witness-search summaries (recomputed from retained raw records) | `python3 -B reproduce.py --checks analysis --output ../rs-out/analysis` | `../rs-out/analysis/reproduction.json` | `PASS_SELECTED_CHECKS` | seconds |
| Functional campaign (780 reloaded requests, 380 full / 285 compact certificates, 6,000 tamper rejections) and native header controls | `python3 -B reproduce.py --checks functional headers --gcc $(which gcc) --clang $(which clang) --output ../rs-out/fh` then `python3 -B verify_expected_results.py --output ../rs-out/v-fh --fresh-functional ../rs-out/fh/functional --fresh-headers ../rs-out/fh/header-admission` | `functional/complete-reproduction.json`, `header-admission/report.json` | `PASS_SELECTED_CHECKS`; then `PASS_KEY_RESULT_SOURCE_TRACE`, 47 checks | ~4-6 min |
| Unit suite | `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` | console | `Ran 366 tests`, `OK (skipped=2)`; `OK (skipped=1)` under CPython 3.12.14; `OK` with 3.12.14 and `CBMC_BINARY=/usr/bin/cbmc` | ~1 min |
| Everything local in one go (analysis, functional, demand, headers, unit suite, fresh verification; plus the paper build when `../paper` exists) | `./evaluate.sh core --output ../rs-out/core` | `../rs-out/core/evaluation.json` | `PASS` | ~7-12 min |
| Paper build (only with `../paper`; see below) | `./evaluate.sh paper --output ../rs-out/paper` | `../rs-out/paper/evaluation.json` | `PASS` | ~30 s |
| CBMC/CPAchecker, Codeflaws, timing campaigns, historical receipts | see [External campaigns](#external-campaigns) | `<output>/evaluation.json` | `PASS`; without the inputs `FAILED_PRECONDITION` (exit 3) with zero studies started | ~1.5-2 h (witness ~70 min, Codeflaws ~30-35 min, CBMC <1 min) |
| `core` + paper + `external` | `./evaluate.sh all ...` (options as for `external`) | `<output>/evaluation.json` | `PASS` | ~2 h |

Times were measured on a 20-core x86-64 laptop (WSL2, repository on the Linux
file system); the first run of `demand` and `functional` can be slower on a
network or Windows-mounted file system.

Tables and figures of the paper are built from these records by the paper's own
build (`paper/build.sh`, not part of this repository). When the repository is
checked out as `artifact/` next to the paper sources, `./evaluate.sh paper` and
the paper step of `core` build it; in a standalone checkout these steps are
reported as skipped (`paper` mode returns `FAILED_PRECONDITION`, exit code 3), and
the claim-ledger entries pointing to `../paper/` are marked `SKIPPED` by the
delivery audit. Figure regeneration is described in `figures/README.md`.
The paper build needs the TeX/poppler/font packages listed under
[Installing the external tools](#installing-the-external-tools); it rewrites the
PDFs inside `../paper`, so run it on a copy if the delivered PDFs must stay
untouched. The build produces `main.pdf` (39 pages, nine figures: five statistical
figures generated from the retained records and four conceptual figures reserved as
framed slots of their final size) and `supplementary.pdf` (18 pages, one conceptual
figure slot). All statistical-figure text is Times New Roman with STIX mathematics;
the figure atlas and `figure-manifest.json` bind each figure to its generator and
source records. A
rebuild keeps the page counts and the manuscript text; bytes and extracted-text
details depend on the installed TeX release (review line-number placement, math
glyph extraction) and font files.

`reproduce.py --help` lists all stages; `docs/reproduction.md` describes each
stage, its inputs, and its completion criteria.

## External campaigns

```sh
./evaluate.sh external --output ../rs-out/external --python312 "$PY312" \
  --cbmc66 /usr/bin/cbmc --cbmc611 ../cbmc-6.11.0/usr/bin/cbmc \
  --cpachecker ../CPAchecker-4.3-unix/bin/cpachecker --archive ../codeflaws.tar.gz \
  --gcc /usr/bin/gcc --clang /usr/bin/clang --jobs 4
```

This runs the historical receipt replay, the CBMC 6.6.0 Boolean comparison (804
requests), the CBMC 6.11.0 + CPAchecker 4.3 witness campaign with its four
follow-up checks, and the six Codeflaws stages (`native`, `signed`, `coverage`,
`timing`, `point-timing`, `counter-overhead`), and prints `{"status": "PASS", ...}`.
`./evaluate.sh all` (same options) runs `core`, the paper build and `external`.
`--jobs` is capped at 4 (the retained witness configuration); timing stages are serial.
Without the tools and the archive these modes stop with `FAILED_PRECONDITION`
and zero studies started; the retained outputs are in `data/` and `experiments/`,
and `verify_expected_results.py` and `reproduce.py --checks analysis` check and
recompute the reported numbers from them.

What a fresh external run reproduces (checked against the retained records):
the CBMC comparison (`summary.json`, all 804 per-case statuses), the Codeflaws
corpus, native execution summary (15,368 executions), signed records (1,478,
apart from `timing_ms`), coverage and union outcomes (739), and the work records
of all three timing campaigns are identical. The witness campaign is complete
with no producer or validator disagreement, but CPAchecker outcomes that hit the
30 s CPU limit are host- and load-dependent: in each of four fresh runs on the
test host, 5-12 of the 5,418 CPAchecker validator runs (the 5,628 arm records
minus the 210 input arms that are not applicable to accepted requests; all on
requests 644, 656, 696, 733 and 801)
that were `UNKNOWN` in the retained run finished within the limit with a definite
`TRUE`/`FALSE`; no definite retained outcome changed. In one run the witness search
statistics were identical to the retained ones (594 planned refutations, 593 matched
confirmations); in the other three the trivial arm of request 733 also finished,
giving 594 matched confirmations. The
signed `requests.json` differs from the retained file only in `timing_ms`. The
paper's numbers remain bound to the retained records (`verify_expected_results.py`).

## What a fresh run does not reproduce

- **Fresh timings** depend on the host; a fresh run reproduces decisions and
  deterministic work counts, not the retained nanoseconds.
- **Historical receipt replay** needs the exact retained interpreter, CPython
  3.12.14. Under another interpreter the unit suite skips only that assertion
  (one of the two expected skips) and still runs the current-runtime controls.
- The second expected skip needs `CBMC_BINARY` pointing at a CBMC executable.

## Notes on the retained data

- Some retained records are byte-identical copies of each other (about 110 MB in
  total), e.g. `data/core-study/` (the complete snapshot of the core run) repeats
  files from `proof-data/`, `results/`, `data/natural-domains/`, and
  `data/domain-controls/` = `data/domain-study/`. They are kept on purpose: the
  study drivers and tests read `proof-data/` and `data/domain-controls/`, while the
  paper build and its hash-bound data checks read `data/core-study/` and
  `data/domain-study/`. Removing either copy would break one of these bindings.
- `data/unsigned-demand/protocol.json` binds an earlier revision of
  `tests/demand_comparison.py`; a fresh `--checks demand` run is a current-driver
  re-execution, not an exact source-identity replay (see `docs/reproduction.md`).
- No file exceeds 50 MB.

## Evidence map

| Location | Evidence type |
| --- | --- |
| `data/unsigned-demand/` | Complete canonical comparisons and work counts for the unsigned finite requests. |
| `data/contract-study/` | Direct receiving and controlled acceptance transport. |
| `data/receiving-time/` | Retained five-arm timing calls and paired summaries. |
| `experiments/point-demand/` | Retained point-local ablation. |
| `experiments/counter-overhead/` | Retained instrumented/uninstrumented receiver comparison. |
| `experiments/signed-coverage/` | Retained coverage-before-union records and union outcomes. |
| `experiments/witness-interoperability/` | Retained external process products, controls, and search statistics. |
| `results/upstream-ceil/` | Freshly executable 42-point mechanism example and negative controls. |
| `claim_evidence_ledger.csv` | Claim-level links to local evidence. |

The package directly supports its finite-domain mechanism and work-count
claims. It does not turn retained external outputs into fresh CBMC/CPAchecker
execution, infer speed from semantic-cell counts, treat archive partitions as
independent samples, or claim application-level Vulkan execution.

## License

Code, documentation, and the retained records produced by the authors are released
under the MIT License (`LICENSE`). Third-party material keeps its own license:
Codeflaws metadata (`licenses/Codeflaws-MIT.txt`), the llama.cpp CEIL_DIV excerpt
(`public-data/ceil-div-LICENSE.txt`), and the font license kept for provenance
(`fonts/OFL-1.1.txt`); see `THIRD_PARTY_NOTICES.md` and `licenses/NOTICE.txt`.
No third-party binaries, fonts, or archives are redistributed.
