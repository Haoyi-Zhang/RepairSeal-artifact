"""Independent semantic and execution-gate regressions for the signed bridge."""
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codeflaws_int32_bridge import (admit_source, evaluate, parse_input, canonical_output,
                                   UnsupportedSource, InvalidInput, INT_MIN, INT_MAX)


def unit(body, signature="int main(void)"):
    return ("#include <stdio.h>\n" + signature + " {" + body + "}\n").encode()


class ClosedSignedBridgeTests(unittest.TestCase):
    def arithmetic(self, expression, values):
        source = unit('int a,b;scanf("%d%d",&a,&b);printf("%d",' + expression + ');return 0;')
        return evaluate(admit_source(source), values)

    def test_negative_division_and_remainder_follow_c(self):
        self.assertEqual(self.arithmetic("a/b", [-7, 3]).value, "-2")
        self.assertEqual(self.arithmetic("a%b", [-7, 3]).value, "-1")
        self.assertEqual(self.arithmetic("a/b", [-7, -3]).value, "2")
        self.assertEqual(self.arithmetic("a%b", [7, -3]).value, "1")

    def test_signed_exception_boundaries(self):
        for expression, values, reason in (
            ("a+b", [INT_MAX, 1], "signed-overflow"),
            ("a-b", [INT_MIN, 1], "signed-overflow"),
            ("a*b", [INT_MIN, -1], "signed-overflow"),
            ("a/b", [INT_MIN, -1], "signed-div-overflow"),
            ("a%b", [INT_MIN, -1], "signed-div-overflow"),
            ("a/b", [7, 0], "division-by-zero"),
            ("-a", [INT_MIN, 0], "signed-overflow"),
        ):
            with self.subTest(expression=expression, values=values):
                result = self.arithmetic(expression, values)
                self.assertFalse(result.defined)
                self.assertEqual(result.undefined_reason, reason)
                self.assertIsNone(result.value)

    def test_short_circuit_and_conditional_expression_are_lazy(self):
        self.assertEqual(self.arithmetic("a && (b/a)", [0, 7]).value, "0")
        self.assertEqual(self.arithmetic("a || (b/a)", [1, 7]).value, "1")
        self.assertEqual(self.arithmetic("a ? b/a : 9", [0, 7]).value, "9")
        self.assertFalse(self.arithmetic("a ? 9 : b/a", [0, 7]).defined)

    def test_early_return_and_original_if_preorder_trace(self):
        source = unit('int x;scanf("%d",&x);if(x<0){puts("NO");return 0;}if(x>2)puts("YES");else puts("NO");return 0;')
        admitted = admit_source(source)
        self.assertEqual(evaluate(admitted, [-1]).trace, ((0, 1),))
        self.assertEqual(evaluate(admitted, [3]).trace, ((0, 0), (1, 1)))
        self.assertEqual(evaluate(admitted, [1]).value, "NO")

    def test_parameter_may_be_overwritten_before_read(self):
        raw = unit('scanf("%d",&n);printf("%d",n/10);return 0;', "int main(int n,char *argv[])")
        admitted = admit_source(raw)
        self.assertEqual(admitted.input_targets, ("n",))
        self.assertEqual(evaluate(admitted, [-101]).value, "-10")
        raw = unit('int x;scanf("%d",&x);argc=4;printf("%d",argc+x);return 0;', "int main(int argc,char **argv)")
        self.assertEqual(evaluate(admit_source(raw), [3]).value, "7")

    def test_source_bytes_and_comment_line_numbers_are_preserved(self):
        raw = b'#include <stdio.h>\n/* one\n two */\nint main(void){int x;scanf("%d",&x);\nif(x)puts("Y");else puts("N");return 0;}\n'
        program = admit_source(raw)
        self.assertEqual(program.raw, raw)
        self.assertEqual(program.source_sha256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(program.if_nodes[0].coord.line, 5)

    def test_unreachable_external_actions_are_rejected(self):
        prefix = 'int x;scanf("%d",&x);printf("%d",x);return 0;'
        for tail in ('system("x");', 'while(1){}', 'for(;;){}', 'int a[4];',
                     'int *p;', 'fopen("x","w");', 'asm("nop");'):
            with self.subTest(tail=tail), self.assertRaises(UnsupportedSource):
                admit_source(unit(prefix + tail))

    def test_lexical_scope_and_uninitialized_reads_are_rejected(self):
        bodies = [
            'int x;scanf("%d",&x);{int y=2;}printf("%d",y);return 0;',
            'int x;scanf("%d",&x);if(x){int y=2;}printf("%d",y);return 0;',
            'int x,y;scanf("%d",&x);if(x)y=1;printf("%d",y);return 0;',
            'int x;scanf("%d",&x);{int x=1;printf("%d",x);}return 0;',
            'int x;scanf("%d",&x);printf("%d",argc);return 0;',
        ]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(UnsupportedSource):
                admit_source(unit(body, "int main(int argc,char **argv)"))

    def test_side_effects_pointer_uses_and_unsafe_formats_are_rejected(self):
        bad = [
            'int x;scanf("%n",&x);printf("%d",x);return 0;',
            'int x;scanf("%2d",&x);printf("%d",x);return 0;',
            'int x;scanf("%d",&x);printf("%n",&x);return 0;',
            'int x;scanf("%d",&x);printf("%d",x++);return 0;',
            'int x;scanf("%d",&x);printf("%d",(x=1));return 0;',
            'int x;scanf("%d",&x);printf("%d",*(&x));return 0;',
            'int x;scanf("%d",&x);puts(1);return 0;',
            'int x;scanf("%d",&x);if(x)scanf("%d",&x);printf("%d",x);return 0;',
        ]
        for body in bad:
            with self.subTest(body=body), self.assertRaises(UnsupportedSource):
                admit_source(unit(body))

    def test_preprocessing_and_main_signature_are_closed(self):
        body = 'int x;scanf("%d",&x);printf("%d",x);return 0;'
        bad = [unit(body).replace(b'#include <stdio.h>', b'#include "stdio.h"'),
               b'#define scanf system\n' + unit(body),
               b'#pragma once\n' + unit(body),
               unit(body).replace(b'printf', b'prin\\\ntf'),
               unit(body).replace(b'printf', b'prin??/\ntf'),
               unit(body, 'int main(int argc,int argv)'),
               unit(body, 'int main(int argc,char *argv)'),
               unit(body, 'int main(int argc,char ***argv)'),
               unit(body).replace(b'#include <stdio.h>\n', b'')]
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises(UnsupportedSource):
                admit_source(raw)

    def test_output_codec_never_normalizes_wrong_decimal_spelling(self):
        for token in (b"04", b"+4", b"-0", b"2147483648", b"1 2"):
            with self.subTest(token=token), self.assertRaises(InvalidInput):
                canonical_output(token, "numeric")
        self.assertEqual(canonical_output(b" \t-4\n", "numeric"), "-4")
        self.assertEqual(canonical_output(b"YES\n", "label"), "YES")

    def test_original_raw_input_profile_matches_scanf_domain(self):
        self.assertEqual(parse_input(b" -7\t+3\r\n", 2), (-7, 3))
        for raw in (b"1\x1c2", b"2147483648", b"1x", b"1 2 3"):
            with self.subTest(raw=raw), self.assertRaises(InvalidInput):
                parse_input(raw, 2 if b"2" in raw and raw.startswith(b"1") else 1)


if __name__ == "__main__":
    unittest.main()
