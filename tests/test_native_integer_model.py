"""A native target premise depends on values rather than compiler spelling."""
import unittest

from codeflaws_source_study import validate_native_integer_model


class NativeIntegerModelTests(unittest.TestCase):
    def test_gcc_hex_and_clang_decimal_describe_the_same_model(self):
        for maximum in ('2147483647', '0x7fffffff', '0X7FFFFFFF', '017777777777'):
            result=validate_native_integer_model('#define __SIZEOF_INT__ 4\n#define __INT_MAX__ '+maximum+'\n')
            self.assertEqual(result, {'__SIZEOF_INT__':4,'__INT_MAX__':2147483647})

    def test_wrong_missing_or_duplicate_premises_are_refused(self):
        good='#define __SIZEOF_INT__ 4\n#define __INT_MAX__ 0x7fffffff\n'
        for wrong in (good.replace(' 4\n',' 8\n'), good.replace('0x7fffffff','0x7fff'),
                      good.replace('0x7fffffff','0xffffffff'), '',
                      '#define __SIZEOF_INT__ 4\n', good+'#define __INT_MAX__ 2147483647\n'):
            with self.subTest(wrong=wrong),self.assertRaises(ValueError):validate_native_integer_model(wrong)

    def test_macro_expressions_and_malformed_integer_tokens_are_not_evaluated(self):
        for token in ('(2147483647)', '2**31-1', 'OTHER', '08', '0x', '1.0', '__import__("os")', '2147483647;'):
            with self.subTest(token=token),self.assertRaises(ValueError):
                validate_native_integer_model('#define __SIZEOF_INT__ 4\n#define __INT_MAX__ '+token+'\n')


if __name__=='__main__':unittest.main()
