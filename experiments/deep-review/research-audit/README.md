# Scientific review and diagnostic-order control

This directory contains a new scientific audit of the delivered manuscript and
one freshly executed, authored mechanism control. It does not modify the
historical `paper/` tree or relabel old campaign receipts as new executions.

## Files

- `scientific-review-zh.md`: detailed Chinese assessment, evidence boundaries,
  actionable manuscript findings, and completion criteria.
- `manuscript-corrections.json`: 13 exact replacements for a separate revised
  manuscript. Each replacement includes its original text, relative paper path,
  expected occurrence count, and reason. The original manuscript is unchanged.
- `trace_order_counterexample.py`: a two-request control run through an
  independent statement interpreter and the full, direct, and demand receivers.
- `trace-order-results/`: actual local output, requests, packets, environment,
  and source fingerprints from this run.
- `primary-sources.json`: primary sources consulted for the scientific scope
  review. This is a limited targeted review, not a systematic literature search.
- `review_order_reduction.py`, `independent-order-review.json`: an independent
  review of the subsequently added order-type analysis, using recursive ordered
  partitions and adversarial profile controls. The review reports 13 sources,
  417 successful source/class executions, and 12 boundary controls. It launches
  no native processes and is not a theorem-prover certificate.

## Reproduce the new control

From `artifact/`, select a new output directory:

```sh
python3 -B experiments/deep-review/research-audit/trace_order_counterexample.py \
  --output /path/to/new/trace-order-results
```

Expected: `PASS`, two requests, four concrete candidate/input observations,
six agreeing complete-receiver results, zero disagreements. No native compiler
or external verifier is executed by this control. It is not a new real-world
bug population and should not be added to the paper's 780 archived requests.

## What the counterexample establishes

Both candidate programs return the wrong value `1` for `x=0` and `x=1` against
a reference returning `0`. Their conditionals only update an unused scratch
variable. For the first program, the trace for `x=1` has three nested events
and precedes the single-event trace for `x=0`. The canonical receiver therefore
returns the numerically later, deeper input. Exchanging the two branches of
the outer conditional, while negating its guard, preserves all returned values
and changes the canonical witness to `x=0`.

This falsifies claims that trace-first order necessarily selects a shallowest
path, refines numeric input order, or identifies the causal branch of a defect.
It does not falsify the specified lexicographic order or receiver equivalence.

The additional order-type review can be repeated without a native compiler:

```sh
python3 -B experiments/deep-review/research-audit/review_order_reduction.py \
  --data experiments/deep-review/real-validation/records \
  --output /path/to/new/independent-order-review.json
```
