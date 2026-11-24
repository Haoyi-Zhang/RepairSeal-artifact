"""Optional native correspondence for the matched natural-domain study.

Only the four previously reviewed, byte-pinned Codeflaws units execute.  The
separate macro harness is project-authored and contains two reviewed pure
arithmetic definitions.  External sources and executables stay outside the
artifact; public output consists of derived observations and identities.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
from codeflaws_cases import CASES, legal_input, value
from codeflaws_source_study import ReviewedNativeRunner, validate_native_integer_model
from macro_bridge import translate


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def macro_harness(axes):
    metadata = json.loads((ROOT / "public-data/ceil-div-source.json").read_text())
    points = list(itertools.product(axes["m"], axes["n"]))
    if not points or len(points) > 4096 or any(not 0 <= m < 2**32 or not 1 <= n < 2**32 for m, n in points):
        raise ValueError("macro harness requires bounded pure unsigned inputs and nonzero divisors")
    definitions = [metadata[role]["line"].replace("#define CEIL_DIV(", "#define " + name + "(", 1)
                   for role, name in (("before", "OLD_CEIL"), ("after", "NEW_CEIL"))]
    lowerings = [translate(metadata[role]["line"], ["m", "n"])["source"].replace("unsigned f(", "unsigned " + name + "(", 1)
                 for role, name in (("before", "old_lowered"), ("after", "new_lowered"))]
    literals = ",\n".join("{" + str(m) + "u," + str(n) + "u}" for m, n in points)
    code = "\n".join((
        "#include <stdio.h>", "#include <limits.h>",
        '_Static_assert(UINT_MAX == 4294967295u, "requires unsigned32");',
        *definitions, *lowerings, "static const unsigned inputs[][2] = {" + literals + "};",
        "int main(void) { for (unsigned i=0;i<" + str(len(points)) + "u;++i) {",
        "unsigned m=inputs[i][0],n=inputs[i][1];",
        'printf("%u,%u,%u,%u\\n", OLD_CEIL(m,n), NEW_CEIL(m,n), old_lowered(m,n), new_lowered(m,n));',
        "} return 0; }", "",
    ))
    return code, points


def run(out, work, chosen, axes, macro_axes, compilers):
    work = work.resolve()
    if work == ROOT or ROOT in work.parents:
        raise ValueError("native work must stay outside the distributable artifact")
    if work.exists() or work.is_symlink():
        raise ValueError("native work must be a new private directory")
    whitelist = {(case, role): identity[1] for case, data in CASES.items() for role, identity in data["sources"].items()}
    if set(chosen) != set(whitelist) or any(type(chosen[key]) is not bytes or hashlib.sha256(chosen[key]).hexdigest() != expected
                                          for key, expected in whitelist.items()):
        raise ValueError("only the four reviewed complete sources may execute")
    if set(axes) != set(CASES) or any(not axis or axis != sorted(set(axis)) or any(not legal_input(case, x) for x in axis)
                                    for case, axis in axes.items()):
        raise ValueError("native scalar domain")
    compilers = [path.resolve() for path in compilers]
    if not 1 <= len(compilers) <= 2 or len(set(compilers)) != len(compilers) or any(not path.is_file() for path in compilers):
        raise ValueError("one or two distinct local compiler executables required")
    work.mkdir(parents=True)
    codeflaws_rows = []; macro_rows = []; compiler_rows = []
    code, points = macro_harness(macro_axes)
    (out / "macro-native-harness.c").write_text(code)
    try:
        for index, compiler in enumerate(compilers, 1):
            label = "compiler-" + str(index)
            directory = work / label; directory.mkdir()
            runner = ReviewedNativeRunner(directory, compiler, False)
            version, stdout, _stderr = runner.diagnostic("version")
            if version["outcome"] != "ok":
                raise ValueError("native compiler identity query failed")
            version_line = stdout.decode("utf-8", errors="replace").splitlines()[0]
            macros, stdout, _stderr = runner.diagnostic("macros")
            if macros["outcome"] != "ok":
                raise ValueError("native integer model query failed")
            integer_model = validate_native_integer_model(stdout.decode("ascii"))
            compiler_row = dict(id=label, executable=str(compiler), version_first_line=version_line,
                                integer_model=integer_model, source_compile_flags=["-std=c11", "-O0"],
                                macro_compile_flags=["-std=c11", "-O2"], compiled_source_units=0)
            compiler_rows.append(compiler_row)
            for (case, role), data in chosen.items():
                compiled, _stdout, _stderr = runner.compile_reviewed(case, role, data)
                if compiled["outcome"] != "ok":
                    raise ValueError("reviewed source compilation failed")
                compiler_row["compiled_source_units"] += 1
                for x in axes[case]:
                    result = runner.observe(case, role, (str(x) + "\n").encode())
                    expected = value(case, role, x)
                    row = dict(compiler=label, case=case, candidate="original" if role == "buggy" else "supplied",
                               input=x, source_sha256=whitelist[(case, role)], expected_model=expected,
                               observed=result["decoded_output"], outcome=result["outcome"],
                               model_agreement=result["outcome"] == "ok" and result["decoded_output"] == expected,
                               matches_task_reference=result["outcome"] == "ok" and result["decoded_output"] == value(case, "reference", x),
                               process_index=result["index"])
                    codeflaws_rows.append(row)
                    if not row["model_agreement"]:
                        raise ValueError("native/source-model disagreement")
            harness = directory / "macro-harness.c"; harness.write_text(code)
            executable = directory / "macro-harness"
            command = [str(compiler), "-std=c11", "-O2", str(harness), "-o", str(executable)]
            compiled = subprocess.run(command, capture_output=True, timeout=20, check=False)
            save(directory / "macro-compile.json", dict(command=command, returncode=compiled.returncode,
                                                        stdout_sha256=hashlib.sha256(compiled.stdout).hexdigest(),
                                                        stderr_sha256=hashlib.sha256(compiled.stderr).hexdigest()))
            (directory / "macro-compile.stdout").write_bytes(compiled.stdout)
            (directory / "macro-compile.stderr").write_bytes(compiled.stderr)
            if compiled.returncode:
                raise ValueError("reviewed arithmetic harness compilation failed")
            result = subprocess.run([str(executable)], capture_output=True, timeout=5, check=False)
            (directory / "macro-run.stdout").write_bytes(result.stdout)
            (directory / "macro-run.stderr").write_bytes(result.stderr)
            if result.returncode or len(result.stdout) > 4096 * 48:
                raise ValueError("reviewed arithmetic harness process failed")
            lines = result.stdout.decode("ascii").splitlines()
            if len(lines) != len(points):
                raise ValueError("native macro observation coverage")
            for point, line in zip(points, lines):
                m, n = point; actual = [int(token) for token in line.split(",")]
                old = ((m + n - 1) % (2**32)) // n; target = (m + n - 1) // n
                row = dict(compiler=label, input=[m, n], old_macro=actual[0], new_macro=actual[1],
                           old_lowered=actual[2], new_lowered=actual[3],
                           model_agreement=actual == [old, target, old, target])
                macro_rows.append(row)
                if not row["model_agreement"]:
                    raise ValueError("native macro/lowering/formula disagreement")
            compiler_row.update(macro_harness_sha256=hashlib.sha256(code.encode()).hexdigest(),
                                macro_compile_returncode=compiled.returncode, macro_run_returncode=result.returncode)
    finally:
        save(out / "native-compilers.json", compiler_rows)
        save(out / "codeflaws-native-observations.json", codeflaws_rows)
        save(out / "macro-native-observations.json", macro_rows)
    result = dict(compilers=len(compiler_rows), distinct_external_translation_units=4,
                  compiled_external_translation_units=sum(row["compiled_source_units"] for row in compiler_rows),
                  codeflaws_distinct_inputs={case: len(axis) for case, axis in axes.items()},
                  codeflaws_process_executions=len(codeflaws_rows),
                  codeflaws_model_agreements=sum(row["model_agreement"] for row in codeflaws_rows),
                  macro_input_rows=len(macro_rows), macro_scalar_observations=4 * len(macro_rows),
                  macro_model_agreements=sum(row["model_agreement"] for row in macro_rows),
                  native_branch_traces_measured=False, upstream_application_executed=False,
                  scope="Distinct normalized legal-input executions; no raw test-payload reexecution or benchmark-wide inference")
    save(out / "native-summary.json", result)
    return result
