# Complete-source signed-C and upstream test-stage study

This experiment applies one source frontend to every indexed subject in a fixed Codeflaws archive. The frontend reads the original complete C translation units. A separate concrete interpreter, GCC with UndefinedBehaviorSanitizer, and ordinary Clang check agreement on the original supplied input files. For each problem, the staged workload pairs every eligible archived candidate with every compatible subject and preserves the correlations in its test inputs.

The observations are finite and explicit: one canonical decimal or literal output token for each supplied input vector. The experiment does not establish behavior on every legal contest input, execute the upstream shell harnesses, observe native branch traces, or measure production stale-result incidents.

## Reproduce

Python 3.11 or later and the pinned optional parser are required. Native reproduction requires a POSIX host, GCC with its UBSan runtime, and Clang. The original unsigned kernel does not depend on this parser.

```sh
python3 -m pip install -r artifact/requirements-codeflaws.txt
python3 artifact/tests/fetch_codeflaws.py --output /path/outside/artifact/codeflaws.tar.gz
python3 -B artifact/tests/codeflaws_staged_study.py \
  --archive /path/outside/artifact/codeflaws.tar.gz \
  --output /path/to/new/inspection-results
```

For original-source native correspondence:

```sh
python3 -B artifact/tests/codeflaws_staged_study.py \
  --archive /path/outside/artifact/codeflaws.tar.gz \
  --output /path/to/new/native-results \
  --execute-admitted \
  --native-work /path/outside/artifact/new-private-native-work \
  --compiler /absolute/path/to/gcc \
  --compiler /absolute/path/to/clang
```

The output and native-work directories must be new or empty as required by the command. Native-work must not be inside the artifact. The source and executable copies remain there; they are not part of the redistributable results. An existing archive can be checked without downloading it:

```sh
python3 artifact/tests/fetch_codeflaws.py \
  --output /path/outside/artifact/codeflaws.tar.gz --verify-only
```

The fetcher verifies the archived input before the experiment begins and fails if the upstream bytes change. The upstream [Codeflaws repository](https://github.com/codeflaws/codeflaws) identifies the download and distinguishes repair and held-out test suites. The project includes the archive member identities, derived observations and reconstruction code; the source archive is obtained separately through the fetch command.

## Population and deterministic selection

The index member `codeflaws/codeflaws-defect-detail-info.txt` contains 3,903 distinct subject rows in the studied archive. This is the experiment's population; the [published benchmark paper](https://codeflaws.github.io/postercameraready.pdf) describes 3,902 defects. The additional directory `369-C-bug-5354958-5359647` is not indexed and is excluded.

Every indexed pair is inspected. Eligibility does not depend on whether a candidate agrees with the oracle. A pair must have compatible admitted source interfaces, every provided test must fit the input/output profile, and both original and reference programs must be defined at every provided input. If any supplied test violates a condition, the whole subject is excluded. No replacement tests are selected and no difficult input is dropped from a retained subject.

The final recorded funnel is:

| Stage | Count |
|---|---:|
| Indexed subjects | 3,903 |
| Indexed source member occurrences | 7,806 |
| Source occurrences admitted by the closed syntax profile | 223 |
| Pairs with compatible admitted interfaces | 101 |
| Pairs whose complete supplied tests fit the I/O profile | 100 |
| Pairs with both versions defined at every supplied input | 95 |
| Programming problems represented by these 95 pairs | 35 |
| Defect classes represented | 16 |

The 100 I/O-compatible pairs contain five whole-subject definedness exclusions:

| Subject | Version(s) | Recorded cause |
|---|---|---|
| `171-B-bug-1463121-1463124` | Original | Signed overflow |
| `227-A-bug-4213239-4213257` | Original and accepted reference | Signed overflow |
| `515-A-bug-16019620-16019646` | Original | Signed overflow |
| `675-A-bug-18264119-18264212` | Original | Signed overflow |
| `675-A-bug-18264177-18264212` | Original | Division by zero |

The accepted submission label is therefore not treated as a C-language definedness guarantee. The JSON records retain each exclusion, its source hash, a concrete supplied input, and its source line.

## Closed source profile

The trusted bridge is `src/codeflaws_int32_bridge.py`. Its closed signed-C profile admits one `int main`, with either no parameters, `void`, or the standard two-parameter form with `char **` / `char *[]` as the second parameter. The argument vector cannot be read. A reachable read of the scalar main argument requires a prior assignment or input conversion. Reusing that parameter as a scalar `scanf` target is supported.

All program variables have exactly type `int`. The machine model is 32-bit two's-complement signed integers. The admitted expressions are decimal integer literals within `INT_MAX`, scalar variables, the ordinary arithmetic and comparison operators, bitwise `&`, `|`, `^`, `~`, logical operators, and conditional expressions. There are no casts, shifts, floating-point values, mixed signedness, or implicit widening. Side effects occur only in standalone assignments, compound assignments, and increments/decrements. Function arguments and arithmetic operands are otherwise pure, so their C evaluation order does not introduce an unmodeled side effect.

Statements are declarations, those scalar updates, `if`/`else`, compound blocks, permitted I/O, and `return 0`. Declarations obey lexical scope, and shadowing is rejected. A separate structural pass visits every statement, including statements after a return. Loops, arrays or pointer operations in the body, user-defined functions, globals, structures, unions, switches, jumps, assembly, and every nonallowlisted call are rejected even when unreachable. A conservative data-flow pass requires initialized reads and exactly one scalar output on every syntactic terminating path.

The preprocessor gate accepts complete angle-bracket includes of `stdio.h`, `stdlib.h`, `string.h`, `math.h`, and `ctype.h`; `stdio.h` is required. Header names must be exact, without whitespace inside the brackets, and all includes must precede source tokens. Local and parameter declarations exclude leading-underscore identifiers and macro names belonging to the included headers. This admits ordinary names while preventing, for example, an `EOF` declaration from being interpreted as a scalar variable after an include has been removed. The gate also rejects macros, conditional compilation, pragmas, local headers, line splicing, trigraphs, unsupported source characters and unsupported literal escapes. Comments are removed only for parsing, with source line numbers preserved. Native correspondence compiles the unchanged original bytes.

Input calls are unconditional initial `scanf` statements with a literal sequence of `%d` conversions and whitespace. Each argument is the address of a declared scalar. Test files must contain exactly the declared number of ASCII decimal integers, all representable in signed int32. Input order and repeated writes to the same scalar follow the original calls. The original test bytes are retained for native execution; a normalized integer vector is used only by the interpreters and finite-domain consumers.

Output is one `printf` with a single `%d`, one literal token, or one `puts` whose argument is a literal token or a conditional choice of such literals. Mixed numeric/literal output is admitted only when every literal is the canonical spelling of an int32. In particular, the bridge never silently equates `04` or `+4` with `4`, or `-0` with `0`. Leading and trailing whitespace are projected away. This scalar-token projection is part of the observation contract, not a claim of arbitrary byte-for-byte process-output equivalence.

## Signed semantics and independent correspondence

The interpreter uses mathematical integers together with explicit int32 range checks. Addition, subtraction, multiplication, negation and updates reject overflow. Division truncates toward zero. Remainder follows the corresponding C quotient. Division by zero and `INT_MIN / -1` or `INT_MIN % -1` are undefined. Logical `&&`, `||`, and conditional expressions evaluate only the selected operand or branch. These rules follow C99 expression and formatted-input requirements; see [WG14 N1256](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf), clauses 6.5, 6.5.5, and 7.19.6.2.

The concrete interpreter is independent of the RepairSeal circuit evaluator. Its public API is:

```python
admitted = admit_source(original_bytes, filename=archive_member)
evaluation = evaluate(admitted, signed_input_tuple)
```

`AdmittedSource` exposes the parsed `tree`, exact `source_sha256`, raw bytes, canonical `input_names`, original `input_targets`, `output_kind`, literal output labels, and source `if_nodes` in preorder. `Evaluation` reports `defined`, canonical token `value`, source-If trace, undefinedness reason/line, counters, and steps. Source-If traces contain only original `if` statements; arithmetic checks do not create new trace events.

Native confirmation compiles each distinct raw source with GCC and Clang. GCC uses `-fsanitize=undefined -fno-sanitize-recover=all`; Clang is explicitly recorded as unsanitized. Both use C99, `-O1`, and format/declaration diagnostics. A small project-authored target probe checks the int32 representation, and a separate GCC control must detect intentional signed overflow before any external source is run.

Only sources that pass the full gate are compiled. Native execution uses no shell, no upstream scripts, and no source transformation. Every run is limited to two wall-clock seconds, one CPU second, 256 MiB address space, zero regular-file output bytes, 32 file descriptors, no core dump, and 4,096 bytes per captured stream. Compiler processes receive separate limits that permit object and executable output. Timeouts, excessive output, nonzero exits and codec failures are recorded as execution failures, not semantic refutations.

The final native study compiled 176 distinct external translation units with each compiler, for 352 compiled units. Each compiler's 33,726 logical test occurrences maps to 7,684 distinct `(source hash, original input-byte hash)` executions. Thus 15,368 external-program executions were performed. All 15,368 agreed with the concrete interpreter; there were no execution, codec or sanitizer failures. This supports correspondence on the observed finite inputs. It is not a proof of frontend correctness on all source programs or all input values.

## Constructing the staged workload

For each eligible programming problem, take every distinct source hash occurring in its retained original/reference pairs. Apply each of those candidates to every eligible subject for that problem. This complete rule yields 176 distinct archived programs and 739 candidate-by-subject combinations. The rule uses neither candidate correctness nor a desired stage outcome to choose combinations.

The first request contains exactly the subject's original repair tests. The next request adds its original held-out tests. These are upstream partitions, not newly generated input sets. Equal integer vectors may be deduplicated for a finite point-set consumer, but neither domain is expanded to the Cartesian product of its coordinate projections. Native reproduction uses the original bytes for every distinct input file content and records the aliases of duplicated logical occurrences.

The recorded scalar-token outcomes are:

| Repair stage | Held-out stage | Candidate-by-subject combinations |
|---|---|---:|
| Pass | Pass | 328 |
| Pass | Fail | 92 |
| Fail | Pass | 7 |
| Fail | Fail | 312 |

The 92 first-stage passes that fail the later stage involve 40 subjects, 49 distinct candidate hashes, and 19 programming problems. All cross-subject candidate/input observations were checked for definedness; none was undefined in this workload. An undefined cross-subject case would be retained as a separate result and would not be executed natively.

For example, archived submission `104-A-11691779.c`, when used as a candidate for subject `104-A-bug-11691772-11691810`, matches all four repair-test observations. Its held-out input `21` produces `0`, while the stored expected token is `4`. The same candidate bytes have not changed; the obligations have grown. The complete 739-combination enumeration, rather than this illustrative example, is the reported experiment.

This is a constructed replay of real source submissions and real benchmark test stages. It is not a chronological production request log, a sample of operational stale-cache incidents, or a repair-tool effectiveness experiment. A cache keyed by the complete current request can already reject a receipt for a different domain. This workload establishes that the scope change carries real additional obligations and supplies natural positive and negative cases for evaluating a receiving protocol against such an appropriate baseline.

## Records and checks

The output directory contains the archive and implementation bindings, every indexed source admission/rejection, every fixed test slot, a normalized corpus, concrete observations, all 739 staged requests, the native execution plan and logical occurrence mapping, compiler identities and compilation records, per-compiler native JSONL observations, and aggregate summaries. The normalized corpus contains all 100 I/O-compatible subjects with eligibility flags and exclusions, including the five undefined subjects. Source entries contain archive member names and hashes, not source text.

The 95 retained pairs cover 4,760 supplied test-file occurrences: 811 repair and 3,949 held-out occurrences. They contain 3,923 distinct subject/input-vector pairs. The upstream partition labels are not disjoint at the vector level: 93 subjects repeat at least one vector across the two partitions, for 778 overlapping subject/vector pairs. Within-partition duplicates also remain as distinct archived file occurrences. Finite point-set requests deduplicate vectors while preserving the original occurrence audit. Every one of the 92 repair-pass/union-refute combinations has a recorded first failing held-out vector that is absent from that subject's repair vectors, so the reversals are caused by newly added points rather than repeated ones. All 95 reference programs match their stored scalar-token oracles, and all 95 original programs have at least one mismatching observation. Five retained subjects have negative inputs. These are observed results after the rule-based cohort selection; they are not conditions used to select it.

Run the bridge and native-resource controls independently:

```sh
python3 -B -m unittest discover -s artifact/tests -p test_codeflaws_int32_bridge.py -v
python3 -B -m unittest discover -s artifact/tests -p test_codeflaws_native_runner.py -v
```

The bridge tests check signed arithmetic boundaries, lazy evaluation, original branch numbering, early returns, scalar main-parameter reuse, byte identities and line numbers, whole-source rejection of unreachable unsafe constructs, lexical scope, initialization, format restrictions, preprocessor restrictions, exact include placement, reserved header names, exact decimal output spelling, and the original-input scanner profile. Four process controls check excessive output, timeout, nonzero exit and the regular-file-size limit. Native confirmation then checks the actual eligible corpus against two separate compilers. The measured source/hash bindings are verified again at study completion so a result cannot silently span two implementation versions.
