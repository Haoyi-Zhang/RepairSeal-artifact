"""Owned-source controls for header/predefined-name admission.

Ordinary unittest discovery checks the closed parser and symbolic entry point.
The explicit --native-audit command additionally compiles only the strings
defined here, probes the selected compilers' macro namespaces, and writes the
observed return codes and outputs.  It never compiles benchmark source.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import codeflaws_int32_bridge as bridge
import int32_circuit as circuit


def identity(name="x", headers=("stdio",), signature="int main(void)"):
    return ("".join("#include <" + h + ".h>\n" for h in headers)
            + signature + '{int ' + name + ';scanf("%d",&' + name
            + ');printf("%d",' + name + ');return 0;}\n').encode("ascii")


def parameter_identity(name="n", argv="argv"):
    return ('#include <stdio.h>\nint main(int ' + name + ',char **' + argv + '){'
            'scanf("%d",&' + name + ');printf("%d",' + name + ');return 0;}\n').encode("ascii")


def cases():
    records = {}
    for name, header in (("EOF", "stdio"), ("BUFSIZ", "stdio"),
                         ("L_tmpnam", "stdio"), ("NULL", "stdio"),
                         ("EXIT_SUCCESS", "stdlib"), ("MB_CUR_MAX", "stdlib"),
                         ("NAN", "math"), ("math_errhandling", "math")):
        records[header + "_" + name] = {
            "source": identity(name, ("stdio",) if header == "stdio" else ("stdio", header)),
            "admitted": False, "code": "header-macro-identifier", "native_compiles": False,
        }
    # Some macro names do not change these exact C tokens, but the closed
    # profile excludes their namespace uniformly instead of expanding macros.
    for name, header in (("stdin", "stdio"), ("isalpha", "ctype")):
        records[header + "_" + name] = {
            "source": identity(name, ("stdio",) if header == "stdio" else ("stdio", header)),
            "admitted": False, "code": "header-macro-identifier", "native_compiles": True,
        }
    for name in ("__LINE__", "__STDC__", "_Private", "_local"):
        records["implementation_" + name] = {
            "source": identity(name), "admitted": False, "code": "reserved-identifier",
            "native_compiles": not name.startswith("__"),
        }
    for name, argv in (("EOF", "argv"), ("n", "EOF"), ("__LINE__", "argv")):
        records["parameter_" + name + "_" + argv] = {
            "source": parameter_identity(name, argv), "admitted": False,
            "code": "reserved-identifier" if name.startswith("_") else "header-macro-identifier",
            "native_compiles": False,
        }
    records["unreachable_macro"] = {
        "source": identity().replace(b"return 0;}", b"return 0;int EOF;}"),
        "admitted": False, "code": "header-macro-identifier", "native_compiles": False,
    }
    for tag, header in (("leading", b"< stdio.h>"), ("trailing", b"<stdio.h >")):
        records["header_internal_space_" + tag] = {
            "source": identity().replace(b"<stdio.h>", header), "admitted": False,
            "code": "preprocessing-directive", "native_compiles": False,
        }
    records["late_include"] = {
        "source": identity().replace(b"int x;", b"int x;\n#include <stdlib.h>\n"),
        "admitted": False, "code": "header-after-source-token",
    }
    for name in ("x", "MY_VALUE", "NAN", "EXIT_SUCCESS", "isalpha"):
        records["ordinary_" + name] = {
            "source": identity(name), "admitted": True, "native_compiles": True,
            "inputs": [[-7], [0], [2147483647]], "outputs": ["-7", "0", "2147483647"],
        }
    records["all_headers_arithmetic"] = {
        "source": (b"#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
                   b"#include <math.h>\n#include <ctype.h>\n"
                   b'int main(void){int x,y;scanf("%d%d",&x,&y);'
                   b'printf("%d",(x/y)*10+x%y);return 0;}\n'),
        "admitted": True, "native_compiles": True,
        "inputs": [[-7, 3], [7, -3], [-7, -3]], "outputs": ["-21", "-19", "19"],
    }
    records["comments_and_strings"] = {
        "source": (b'/* EOF __LINE__ */\n# include <stdio.h> /* NULL */\n'
                   b'int main(void){int x;scanf("%d",&x);puts("EOF");return 0;}\n'),
        "admitted": True, "native_compiles": True,
        "inputs": [[7]], "outputs": ["EOF"],
    }
    records["crlf_and_duplicate_header_prefix"] = {
        "source": (b"#include<stdio.h>\r\n# include <stdio.h>\r\n"
                   b'int main(void){int x;scanf("%d",&x);printf("%d",x);return 0;}\n'),
        "admitted": True, "native_compiles": True,
        "inputs": [[7]], "outputs": ["7"],
    }
    records["ordinary_parameters"] = {
        "source": parameter_identity(), "admitted": True, "native_compiles": True,
        "inputs": [[-9]], "outputs": ["-9"],
    }
    return records


CASES = cases()


class HeaderAdmissionTests(unittest.TestCase):
    def test_header_and_predefined_identifiers_are_rejected(self):
        for name, case in CASES.items():
            if case["admitted"]:
                continue
            with self.subTest(case=name), self.assertRaises(bridge.UnsupportedSource) as caught:
                bridge.admit_source(case["source"], name)
            self.assertEqual(caught.exception.code, case["code"])

    def test_header_macro_exclusion_covers_all_declared_macro_names(self):
        for header, names in bridge.HEADER_MACROS.items():
            for name in sorted(names):
                headers = ("stdio",) if header == "stdio" else ("stdio", header)
                with self.subTest(header=header, name=name), self.assertRaises(bridge.UnsupportedSource) as caught:
                    bridge.admit_source(identity(name, headers))
                self.assertEqual(caught.exception.code, "header-macro-identifier")

    def test_positive_sources_keep_bytes_and_math(self):
        for name, case in CASES.items():
            if not case["admitted"]:
                continue
            with self.subTest(case=name):
                admitted = bridge.admit_source(case["source"], name)
                self.assertEqual(admitted.raw, case["source"])
                self.assertEqual(admitted.source_sha256, hashlib.sha256(case["source"]).hexdigest())
                for point, output in zip(case["inputs"], case["outputs"]):
                    concrete = bridge.evaluate(admitted, point)
                    symbolic = circuit.evaluate_program(admitted, point)
                    self.assertTrue(concrete.defined)
                    self.assertEqual(concrete.value, output)
                    self.assertTrue(symbolic["defined"])
                    self.assertEqual(symbolic["value"], output)

    def test_public_symbolic_request_readmits_macro_source(self):
        source = identity("EOF").decode("ascii")
        request = {"kind": circuit.PROFILE, "id": "owned-header-macro",
                   "policy": "reference-everywhere", "points": [[7]],
                   "sources": dict.fromkeys(("original", "candidate", "reference"), source)}
        with self.assertRaises((bridge.UnsupportedSource, ValueError)):
            circuit.build_task(request)


def native_audit(args):
    output = args.native_audit.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("native audit output must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    preimage = None
    if args.preimage:
        spec = importlib.util.spec_from_file_location("header_admission_preimage", args.preimage)
        preimage = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = preimage
        spec.loader.exec_module(preimage)
    records = []
    for name, case in CASES.items():
        row = {key: value for key, value in case.items() if key != "source"}
        row.update(id=name, source_sha256=hashlib.sha256(case["source"]).hexdigest())
        (output / (name + ".c")).write_bytes(case["source"])
        if preimage:
            try:
                admitted = preimage.admit_source(case["source"], name)
            except preimage.UnsupportedSource as error:
                row["preimage"] = {"admitted": False, "code": error.code}
            else:
                row["preimage"] = {"admitted": True,
                    "observation_at_seven": preimage.evaluate(admitted, [7] * admitted.input_arity).as_dict()}
                row["preimage"]["symbolic_at_seven"] = circuit.evaluate_program(admitted, [7] * admitted.input_arity)
        try:
            admitted = bridge.admit_source(case["source"], name)
        except bridge.UnsupportedSource as error:
            row["current"] = {"admitted": False, "code": error.code, "detail": error.detail}
        else:
            row["current"] = {"admitted": True}
        if row["current"]["admitted"] != case["admitted"]:
            raise AssertionError((name, row["current"]))
        row["native"] = []
        records.append(row)
    identities = []
    with tempfile.TemporaryDirectory(prefix="repairseal-owned-headers-") as directory:
        work = Path(directory)
        for family, path in (("gcc", args.gcc), ("clang", args.clang)):
            executable = path.resolve(strict=True)
            version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, check=True, timeout=20)
            flags = ["-std=c99", "-O1", "-Werror=implicit-function-declaration", "-Werror=format"]
            if family == "gcc":
                flags += ["-fsanitize=undefined", "-fno-sanitize-recover=all"]
            identities.append({"family": family, "path": str(executable),
                               "sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                               "version": version.stdout.strip(), "flags": flags})
            for header in (None, *sorted(bridge.HEADERS)):
                source = b"" if header is None else ("#include <" + header + ".h>\n").encode("ascii")
                command = [str(executable), "-std=c99", "-O1", "-dM", "-E", "-x", "c", "-"]
                proc = subprocess.run(command, input=source, capture_output=True, check=True, timeout=20)
                names = set(name.decode("ascii") for name in re.findall(rb"^#define ([A-Za-z_][A-Za-z_0-9]*)", proc.stdout, re.M))
                public = {name for name in names if not name.startswith("_")}
                unmatched = public - (bridge.HEADER_MACROS[header] if header else set())
                if unmatched:
                    raise AssertionError((family, header, "unaccounted macro names", sorted(unmatched)))
                (output / (family + "-" + (header or "predefined") + "-macros.txt")).write_bytes(proc.stdout)
            for row in records:
                name = row["id"]; case = CASES[name]
                source = work / (name + ".c"); binary = work / (family + "-" + name)
                source.write_bytes(case["source"])
                command = [str(executable), *flags, str(source), "-o", str(binary)]
                proc = subprocess.run(command, capture_output=True, timeout=20)
                native = {"family": family, "command": command, "compile_returncode": proc.returncode,
                          "stderr": proc.stderr.decode("utf-8", errors="replace"), "runs": []}
                if "native_compiles" in case and (proc.returncode == 0) != case["native_compiles"]:
                    raise AssertionError((name, family, proc.returncode, native["stderr"]))
                if case["admitted"]:
                    for point, expected in zip(case["inputs"], case["outputs"]):
                        stdin = (" ".join(map(str, point)) + "\n").encode("ascii")
                        run = subprocess.run([str(binary)], input=stdin, capture_output=True, timeout=5)
                        if run.returncode or run.stdout.decode("ascii").strip() != expected:
                            raise AssertionError((name, family, point, run.returncode, run.stdout, run.stderr))
                        native["runs"].append({"inputs": point, "returncode": run.returncode,
                                               "stdout": run.stdout.decode("ascii"), "expected": expected})
                row["native"].append(native)
    report = {"schema": "repairseal-owned-header-admission-v1", "bridge_sha256": hashlib.sha256((ROOT / "src/codeflaws_int32_bridge.py").read_bytes()).hexdigest(),
              "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "preimage_sha256": hashlib.sha256(args.preimage.read_bytes()).hexdigest() if args.preimage else None,
              "case_count": len(records), "compiler_count": len(identities), "compiler_identities": identities,
              "native_compilations": sum(len(row["native"]) for row in records),
              "native_executions": sum(len(native["runs"]) for row in records for native in row["native"]),
              "records": records,
              "scope": "Owned controls only. Macro coverage is checked for these exact compiler paths and strict C99 flags, not every possible C implementation or compiler command line. These checks do not rerun the natural corpus or release gates."}
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({key: report[key] for key in ("case_count", "compiler_count", "native_compilations", "native_executions")}))


if __name__ == "__main__":
    if "--native-audit" in sys.argv:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--native-audit", type=Path, required=True)
        parser.add_argument("--gcc", type=Path, required=True)
        parser.add_argument("--clang", type=Path, required=True)
        parser.add_argument("--preimage", type=Path)
        native_audit(parser.parse_args())
    else:
        unittest.main()
