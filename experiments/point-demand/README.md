# Point-local demand evaluation

This experiment tests whether sharing values across input projections is useful enough to offset its supporting work on the original signed C requests. It compares four receivers on the same complete canonical decision:

| Receiver | Stored semantic values |
| --- | --- |
| Full checking | Every reconstructed node at every actual input, compared with the supplied packet. |
| Live-node evaluation | Every node in the obligation/event dependency closure at every actual input. |
| Support demand | Requested nodes memoized by their global input-support projection. |
| Point-local demand | Requested nodes memoized separately at each actual input. |

The point-local control keeps obligation priority, conditional operand rules, delayed event evaluation and trace/input minimization. It removes global-support analysis, representative selection and cross-input sharing. Both demand receivers retain fine-grained traversal counters. Consequently, their elapsed difference measures a combined implementation change; it does not separately time support analysis, projection construction, dictionary access or source reconstruction.

## Results

All 1,478 requests retain the concrete reference's complete canonical decision. The run completed 5,912 preflight receiving calls and 70,944 timed receiving calls. The independent raw-record verifier returned `PASS_INDEPENDENT_POINT_DEMAND_RECOMPUTATION`; all eight focused unit-test methods passed.

| Stage | Full values | Live-node values | Point-demand values | Support-demand values |
| --- | ---: | ---: | ---: | ---: |
| Repair inputs | 919,166 | 751,387 | 542,611 | 489,688 |
| Union inputs | 4,220,215 | 3,416,866 | 2,639,026 | 2,175,382 |

| Stage | Point / support time | Point / live time | Point faster than support | Point faster than live |
| --- | ---: | ---: | ---: | ---: |
| Repair inputs | 0.858 | 1.119 | 693 / 739 requests | 101 / 739 requests |
| Union inputs | 0.727 | 1.597 | 733 / 739 requests | 2 / 739 requests |

Time ratios are medians of paired ratios formed from each request's twelve-call medians. Aggregating request medians within each problem makes point-local demand faster than support-demand in all 35 problems at both stages. It is faster than live-node evaluation in two repair-stage problems and no union-stage problems. The 549 cross-source combinations retain the same direction: median point/support ratios are 0.851 and 0.722; median point/live ratios are 1.118 and 1.614.

Giving up cross-input sharing increased semantic work while decreasing whole-call time relative to support-demand. The remaining comparison still favors the simpler live-node receiver on most of these natural requests. Logical work in `logical-work.json` records the removed support-coordinate operations and the added per-point evaluations. Those counts do not assign elapsed time to individual phases.

## Execution design

The complete original-source workload contains 1,478 requests: 739 on original repair inputs and 739 on their union with original held-out inputs. No request is selected by measured cost. Each receiving call reconstructs its source task. The full receiver starts from a decoded packet; packet production and transport decoding are outside the measured interval.

Each request receives twelve measured calls to every arm after one untimed call. A four-arm Williams design is repeated three times, so each arm appears three times at every position and each ordered pair of distinct arms occurs three times as immediate neighbors. Request order is shuffled separately in every repetition. Every measured result and work counter is checked after its timer stops against the preflight result. Preflight decisions must also match the retained concrete-oracle record.

The study is a separate execution from the earlier five-arm measurement. Ratios involving the point-local receiver use its co-measured controls. The raw durations are retained in `measurements/timings.jsonl`; the protocol, per-request work, per-request timing summaries and aggregate analysis are adjacent files.

## Correctness and resource accounting

At any actual input, induction over the DAG identifies every demand value with its complete-vector denotation. Conditional evaluation can omit an unselected total term; source-definedness remains a checked obligation. Each `(input, node)` address is computed at most once. If there are `M` actual inputs and `L` live nodes, point-local demand therefore computes at most `L × M` local values. After choosing the first failed obligation, it examines every actual input and minimizes the same trace/input diagnostic key.

Dense memo rows are allocated only when an input is first visited. Each row reserves a slot for every reconstructed node, including slots that remain unused. Allocated slots are recorded separately from computed values; fewer semantic values is not a claim of lower memory usage.

## Reproduction

The driver is `tests/int32_point_demand_study.py`. It requires the normalized original-source corpus, its external archive and the retained signed-contract record directory. Use `--help` for the exact argument list and supply a new output directory. `--cpu` accepts an allowed processor affinity when supported by the host.

The eight methods in `tests/test_int32_point_demand.py` include signed arithmetic boundaries, empty-domain rejection, a singleton domain, correlated input tuples, canonical trace priority, skipped faulty operands and early returns. `tests/verify_point_demand_study.py` independently recomputes schedule balance and all reported paired ratios from raw durations, and checks canonical results against the retained reference. This verification needs the result directory and retained reference JSON, without the external source archive.
