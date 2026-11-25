# Third-party and external resources

RepairSeal's own implementation is distributed under `LICENSE`.  The artifact
also refers to external tools, data, publication templates, and fonts.  Their
presence in documentation does not mean their binaries or source payloads are
redistributed.

- **Codeflaws.** Metadata and normalized observations are included; the pinned
  original source/test archive is an external input.  The repository notice is
  retained in `licenses/Codeflaws-MIT.txt`.
- **CBMC and CPAchecker.** Process products and retained outputs are included;
  verifier binaries are external prerequisites for fresh campaigns.
- **GCC and Clang.** Compiler binaries are not included.  Every fresh native run
  records the executable path, hash, version output, and flags.
- **llama.cpp.** The artifact retains the source-linked CEIL_DIV edit and finite
  mechanism model; it does not redistribute or execute the full upstream
  application.  The supplied upstream notice is in `public-data/ceil-div-LICENSE.txt`.
- **ACM acmart.** Used only by the companion paper sources (not part of this
  repository), which carry the class, bibliography style, and `acmart-LICENSE.txt`.
- **Fonts.** No font binaries are distributed in this delivery.  Figure scripts
  use an installed Times New Roman face (the delivered figures embed Times New
  Roman subsets) with matplotlib's bundled STIX fonts for mathematics, and a
  documented installed fallback (Liberation Serif, then DejaVu Serif); see
  `figures/README.md`.  `fonts/OFL-1.1.txt` (Linux Libertine) is retained only
  as provenance for earlier builds.

`external_resources.csv` gives the role, source, local use, and execution
boundary for each resource.
