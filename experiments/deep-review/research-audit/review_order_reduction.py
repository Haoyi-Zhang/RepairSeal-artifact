"""Independent enumeration and boundary review of the new order quotient.

This is a review of the comparison/copy analysis, not a mechanized proof or a
new native campaign. It enumerates ordered set partitions recursively instead
of calling the study's Cartesian rank-pattern generator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / "real-validation"
sys.path.insert(0, str(STUDY))
from order_types import Program, OutsideProfile, patterns


def ordered_partitions(n):
    partitions = [((0,),)]
    for coordinate in range(1, n):
        updated = []
        for blocks in partitions:
            for i in range(len(blocks)):
                updated.append(blocks[:i] + (blocks[i] + (coordinate,),) + blocks[i+1:])
            for i in range(len(blocks) + 1):
                updated.append(blocks[:i] + ((coordinate,),) + blocks[i:])
        partitions = updated
    result = []
    for blocks in partitions:
        ranks = [None] * n
        for rank, block in enumerate(blocks):
            for coordinate in block:
                ranks[coordinate] = rank
        result.append(tuple(ranks))
    if len(result) != len(set(result)):
        raise AssertionError("partition recurrence duplicated a weak order")
    return sorted(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=STUDY / "records")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("review output must not exist")
    protocol = json.loads((args.data / "protocol.json").read_text())
    enumerations = {}
    for n, expected in ((1, 1), (2, 3), (3, 13), (4, 75)):
        independent = ordered_partitions(n)
        if len(independent) != expected or independent != patterns(n):
            raise AssertionError("independent class enumeration disagreement")
        enumerations[str(n)] = len(independent)
    checks = []
    base = '#include <stdio.h>\nint main(void) { int x; scanf("%d", &x); BODY return 0; }'
    variants = {
        "zero-comparison": 'if (x == 0) { printf("%d\\n", x); } else { printf("%d\\n", x); }',
        "truthiness": 'if (x) { printf("%d\\n", x); } else { printf("%d\\n", x); }',
        "arithmetic": 'x = x + x; printf("%d\\n", x);',
        "cast": 'x = (int)x; printf("%d\\n", x);',
        "hex-format": 'printf("\\x25d\\n", x);',
        "integer-constant-copy": 'x = 0; printf("%d\\n", x);',
        "loop": 'while (x == x) { } printf("%d\\n", x);',
    }
    for name, body in variants.items():
        source = base.replace("BODY", body).encode()
        try:
            Program(source)
        except OutsideProfile:
            checks.append({"control": name, "result": "REJECTED"})
        else:
            raise AssertionError("profile unexpectedly admitted " + name)
    for name in ("EOF", "stdin", "_x"):
        source = base.replace("BODY", 'printf("%d\\n", x);').replace(" x", " " + name).replace("&x", "&" + name).encode()
        try:
            Program(source)
        except OutsideProfile:
            checks.append({"control": "identifier-" + name, "result": "REJECTED"})
        else:
            raise AssertionError("profile unexpectedly admitted " + name)
    uninitialized = Program(base.replace("BODY", 'int y; printf("%d\\n", y);').encode())
    if uninitialized.evaluate((0,))["defined"]:
        raise AssertionError("uninitialized read was treated as valid")
    checks.append({"control": "uninitialized-path", "result": "ANALYSIS_FAILED"})
    double_output = Program(base.replace("BODY", 'printf("%d\\n", x); printf("%d\\n", x);').encode())
    if double_output.evaluate((0,))["defined"]:
        raise AssertionError("two-output path was treated as valid")
    checks.append({"control": "two-output-path", "result": "ANALYSIS_FAILED"})
    classes = 0
    source_bindings = {}
    for ident, spec in protocol["sources"].items():
        source = args.data / "sources/normalized" / (ident + ".c")
        raw = source.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != spec["normalized_sha256"]:
            raise AssertionError("normalized source binding")
        source_bindings[ident] = actual
        program = Program(raw)
        for rank in ordered_partitions(program.arity):
            if not program.evaluate(rank)["defined"]:
                raise AssertionError("selected source failed complete quotient analysis")
            classes += 1
    result = {
        "status": "PASS",
        "review_kind": "independent recursive class enumeration and adversarial profile review",
        "enumerated_class_counts": enumerations,
        "source_identities": len(source_bindings),
        "successful_source_order_classes": classes,
        "profile_controls": checks,
        "native_processes_launched_by_this_review": 0,
        "human_annotators": 0,
        "review_conclusion": "The weak-order reduction is sound under the stated comparison/copy, successful int32 I/O, and exhaustive-valid-path premises. This review checks the implementation boundary and enumeration but is not a theorem-prover certificate.",
        "source_bindings": source_bindings,
        "reviewed_files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (STUDY / "order_types.py", STUDY / "proof.md", Path(__file__))},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "sources": len(source_bindings),
                      "classes": classes, "controls": len(checks),
                      "independent_class_counts": enumerations}))


if __name__ == "__main__":
    main()
