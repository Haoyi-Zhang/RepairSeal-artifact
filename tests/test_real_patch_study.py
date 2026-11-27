"""Controls for public-patch reconstruction and closed source execution."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]/'experiments/real-patches'
sys.path.insert(0,str(ROOT))
import scalar_semantics as scalar
from patch_study import strict_patch


def program(body):
    return ('#include <stdio.h>\nint main(int argc, char *argv[]) {'+body+'}').encode()


class RealPatchControls(unittest.TestCase):
    def test_exact_unified_patch_and_context_rejection(self):
        old=b'int f(void) {\n return 0;\n}\n'
        diff=b'--- a/a.c\n+++ b/a.c\n@@ -1,3 +1,3 @@\n int f(void) {\n- return 0;\n+ return 1;\n }\n'
        self.assertEqual(strict_patch(old,diff),b'int f(void) {\n return 1;\n}\n')
        with self.assertRaises(ValueError):strict_patch(b'/* inserted */\n'+old,diff)

    def test_uninitialized_is_not_zero_initialized(self):
        p=scalar.parse(program('int x,z; x=atoi(argv[1]); if(x>0) z=x; printf("%d\\n",z); return 0;'),1)
        self.assertTrue(scalar.evaluate(p,[2])['defined'])
        self.assertEqual(scalar.evaluate(p,[0])['undefined_reason'],'uninitialized-read:z')

    def test_short_circuit_does_not_evaluate_undefined_arm(self):
        p=scalar.parse(program('int x,z; x=atoi(argv[1]); z=(x!=0 && 10/x>1); printf("%d\\n",z); return 0;'),1)
        self.assertEqual(scalar.evaluate(p,[0])['stdout'],'0\n')

    def test_signed_division_and_remainder(self):
        p=scalar.parse(program('int x; x=atoi(argv[1]); printf("%d\\n",x%3); return 0;'),1)
        self.assertEqual(scalar.evaluate(p,[-4])['stdout'],'-1\n')

    def test_signed_overflow_and_zero_division(self):
        p=scalar.parse(program('int x; x=atoi(argv[1]); printf("%d\\n",x+1); return 0;'),1)
        self.assertEqual(scalar.evaluate(p,[2**31-1])['undefined_reason'],'signed-overflow')
        q=scalar.parse(program('int x; x=atoi(argv[1]); printf("%d\\n",4/x); return 0;'),1)
        self.assertEqual(scalar.evaluate(q,[0])['undefined_reason'],'division-by-zero')

    def test_unknown_macro_and_unreachable_loop_rejected(self):
        with self.assertRaises(scalar.Unsupported):
            scalar.parse(b'#include <stdio.h>\n#define MAGIC 3\nint main(){return 0;}',1)
        with self.assertRaises(scalar.Unsupported):
            scalar.parse(program('if(0){while(1){}} return 0;'),1)

    def test_identity_macro_and_no_extra_output_stripping(self):
        p=scalar.parse(b'#include <stdio.h>\n#ifndef ANGELIX_OUTPUT\n#define ANGELIX_OUTPUT(type, expr, id) expr\n#endif\nint main(int argc,char*argv[]){int x;x=atoi(argv[1]);printf("prefix %d\\n",ANGELIX_OUTPUT(int,(int)x,"stdout"));return 0;}',1)
        self.assertEqual(scalar.evaluate(p,[4])['stdout'],'prefix 4\n')

    def test_unsequenced_side_effects_rejected(self):
        with self.assertRaises(scalar.Unsupported):
            scalar.parse(program('int x; x=0; printf("%d\\n",x++ + x++);return 0;'),1)

    def test_macro_does_not_gain_parentheses(self):
        p=scalar.parse(b'#include <stdio.h>\n#ifndef ANGELIX_OUTPUT\n#define ANGELIX_OUTPUT(type, expr, id) expr\n#endif\nint main(){printf("%d\\n",2*ANGELIX_OUTPUT(int,1+2,"stdout"));return 0;}',1)
        self.assertEqual(scalar.evaluate(p,[0])['stdout'],'4\n')

    def test_octal_literal_and_shift_exclusion(self):
        p=scalar.parse(program('printf("%d\\n",012);return 0;'),1)
        self.assertEqual(scalar.evaluate(p,[0])['stdout'],'10\n')
        with self.assertRaises(scalar.Unsupported):
            scalar.parse(program('printf("%d\\n",(-1)>>1);return 0;'),1)


if __name__=='__main__':unittest.main()
