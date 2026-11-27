# Observed domain-scale re-analysis

This directory addresses the optional domain-size question using the exact
delivered full-index census. It is a new, reproducible analysis of retained
records, not a claim of fresh benchmark execution.

```sh
python -B experiments/natural-domains-review/analyze_scale.py --verify
```

`source-arity-census.csv` has one row for each of the 7,806 indexed original or
reference occurrences. It preserves the source member and SHA-256. The signed
profile established arity for 223 occurrences; the remaining 7,583 are explicitly
unknown because they failed admission. They are not assigned zero inputs and are
not silently excluded from the inventory. Repeated occurrences are retained;
there are 7,425 distinct source hashes.

`test-projection-scale.csv` uses every repair and held-out input for all 100
complete-I/O subjects. For each coordinate, it counts the distinct values seen
in those inputs and multiplies those counts. This records the cost of replacing
an observed correlated point set with independent axes. It does **not** establish
that every Cartesian combination is legal for the task, defined for the source,
or already verified. The actual point-set and the product must be read separately.

In the 100-subject cohort, 50 products exceed 4,096. Among the 95 subjects defined
on all their given tests, 46 products exceed the cap. The largest product is
50,056,151,040, for three related 560-B subjects whose retained input set has 101
points. This illustrates loss of correlation, not billions of independently
collected test inputs.

The eight-values-per-coordinate column is an explicitly hypothetical scaling
scenario. It exceeds 4,096 for all admitted sources with at least five inputs,
37 occurrences in the retained census. It is not an inferred full legal domain.

`summary.json` binds both input records and this script, includes distributions,
and binds the output CSV bytes. `--verify` recomputes every row and requires exact
agreement. The undefined-subject cohort is kept visible; its largest retained
point set differs from the 95-subject all-defined cohort used in the paper.

## Fresh whole-archive cross-check

The separate `recollect_census.py` campaign subsequently fetched no derived
statistics from this summary: it reread the complete, SHA-256-verified Codeflaws
archive and reran source admission, test parsing, and concrete interpretation.
`fresh-census/recollection.json` records the actual execution and implementation
identities. All six generated records are byte-identical to the corresponding
original census records: 3,903 indexed subjects, 7,806 source occurrences,
223 admitted occurrences, 101 syntactically compatible pairs, 100 complete-I/O
subjects, and 95 all-defined subjects. This is a fresh collection using the same
frontend, not an independent whole-C semantics proof or a native compilation
campaign; its fresh native-execution count is explicitly zero.

```sh
python3 -B experiments/natural-domains-review/recollect_census.py --verify
# A new collection requires the pinned external archive and a new output path:
python3 -B experiments/natural-domains-review/recollect_census.py \
  --archive /path/to/codeflaws.tar.gz --output ../fresh-codeflaws-census
```

The first command verifies the new collection receipts and their complete
inventory without requiring the archive. The second actually rereads the
archive; it must not be described as a fresh native run.
