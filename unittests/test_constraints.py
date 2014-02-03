import unittest, math
from bw.bwconstraint import *

class TestSimpleConstraints(unittest.TestCase):
    def test_isa(self):
        self.assertIn(5, ISA(int))
        self.assertNotIn(7.0, ISA(int))

    def test_in(self):
        self.assertIn(5, IN(4, 5, 6))
        self.assertNotIn(3, IN(4, 5, 6))

    def test_is(self):
        class X(object): pass
        x = X()
        self.assertIn(x, IS(x))
        self.assertNotIn(X(), IS(x))

    def test_constraint_passthru(self):
        a = ANY()
        self.assertIs(a, CHECK(a))

    def test_any(self):
        self.assertIn(5, ANY(int, float))
        self.assertNotIn('hello', ANY(int, float))
        self.assertIn(5, ANY(5, 6, 7))

    def test_multi(self):
        # These should pass...
        ANY(5, 6, 7)[5]
        ANY(5, 6, 7)[6]
        ANY(5, 6, 7)[7]

        # These should bomb...
        self.assertRaises(ValueError, lambda x: ANY(5, 6, 7)[x], 8)
        self.assertRaises(ValueError, lambda x: ANY(5, 6, 7)[x,], 8)

    def test_filter(self):
        l = list(range(10))
        t = tuple(l)
        g = (n for n in l)
        self.assertEqual([6, 7, 8, 9], CHECK(BWC > 5).filter(l))
        self.assertEqual([0, 1, 2, 3, 4, 5], CHECK(BWC > 5).filter_out(l))
        self.assertEqual([6, 7, 8, 9], list(CHECK(BWC > 5).filter(g)))
        self.assertEqual((6, 7, 8, 9), CHECK(BWC > 5).filter(t))

    def test_convert(self):
        self.assertEqual(7, INTO(int) << '7')
        self.assertEqual(7, INTO(int) << 7)
        self.assertRaises(TypeError, lambda x: INTO(int) << x, 'hello')

    def test_never(self):
        self.assertNotIn(5, NEVER)
        self.assertRaises(TypeError, lambda: NEVER << 5)

    def test_always(self):
        self.assertIn(5, ALWAYS)
        self.assertEqual(5, ALWAYS.convert(5, None))

    def test_coerce(self):
        class X(object): pass
        x = X()
        self.assertIs(x, CHECK(X).coerce(x))

class TestCompoundConstraints(unittest.TestCase):
    def test_or(self):
        self.assertIn(5, ISA(int) | ISA(float))
        self.assertNotIn(5j, ISA(int) | ISA(float))

    def test_and(self):
        self.assertIn(6, ISA(int) & +(BWC > 5))
        self.assertNotIn(4, ISA(int) & +(BWC > 5))
        self.assertNotIn(6.0, ISA(int) & +(BWC > 5))

    def test_not(self):
        self.assertIn(6, ~CHECK(5))

    def test_empty(self):
        self.assertIn(5, ANY())
        self.assertIn(5, ALL())

    def test_convert(self):
        self.assertEqual(5, ANY(ISA(int)) << '5')
        self.assertEqual(5, ALL(ISA(int), BWC == 5) << '5')
        self.assertIs(None, ANY(ISA(float)).coerce('hello'))
        self.assertIs(None, ALL(ISA(float)).coerce('hello'))

class TestFunctionConstraint(unittest.TestCase):
    def test_fail(self):
        self.assertNotIn('hello', FN(lambda x: x / 0))

    def test_expr(self):
        import warnings
        warnings.filterwarnings('ignore', 'bw-expr:')
        self.assertIn(5, EXPR('# == 5'))

class TestBWC(unittest.TestCase):
    def test_arith(self):
        self.assertIn(1, CHECK(BWC + 5 < 7))
        self.assertIn(1, CHECK(5 + BWC < 7))
        self.assertIn(10, CHECK(BWC - 5 > 1))
        self.assertIn(10, CHECK(5 - BWC == -5))
        self.assertIn(2, CHECK(BWC * 5 == 10))
        self.assertIn(2, CHECK(5 * BWC == 10))
        self.assertIn(10, CHECK(BWC / 5 == 2))
        self.assertIn(10, CHECK(50 / BWC == 5))
        self.assertIn(10, CHECK(BWC // 5 == 2))
        self.assertIn(10, CHECK(500 // BWC == 50))
        self.assertIn(10, CHECK(BWC % 5 == 0))
        self.assertIn(10, CHECK(34 % BWC == 4))
        self.assertIn(10, CHECK(BWC ** 2 == 100))
        self.assertIn(10, CHECK(2 ** BWC == 1024))
        self.assertIn(10, CHECK(divmod(BWC, 5) == (2, 0)))

    def test_unary(self):
        self.assertIn(10, CHECK(-BWC == -10))
        self.assertIn(10, CHECK(~BWC == -11))
        self.assertIn(-10, CHECK(abs(BWC) == 10))

    def test_bitwise(self):
        self.assertIn(1, CHECK(BWC << 2 == 4))
        self.assertIn(1, CHECK(4 << BWC == 8))
        self.assertIn(16, CHECK(BWC >> 2 == 4))
        self.assertIn(1, CHECK(4 >> BWC == 2))
        self.assertIn(13, CHECK(BWC & 3 == 1))
        self.assertIn(13, CHECK(3 & BWC == 1))
        self.assertIn(13, CHECK(BWC | 3 == 15))
        self.assertIn(13, CHECK(3 | BWC == 15))
        self.assertIn(16, CHECK(BWC ^ 3 == 0x13))
        self.assertIn(16, CHECK(3 ^ BWC == 0x13))

    def test_logical(self):
        self.assertIn(10, CHECK(BWC == 10))
        self.assertIn(11, CHECK(BWC != 10))
        self.assertIn(9, CHECK(BWC < 10))
        self.assertIn(11, CHECK(BWC > 10))
        self.assertIn(10, CHECK(BWC <= 10))
        self.assertIn(10, CHECK(BWC >= 10))
        self.assertNotIn(11, CHECK(BWC == 10))
        self.assertNotIn(10, CHECK(BWC != 10))
        self.assertNotIn(10, CHECK(BWC < 10))
        self.assertNotIn(10, CHECK(BWC > 10))
        self.assertNotIn(11, CHECK(BWC <= 10))
        self.assertNotIn(9, CHECK(BWC >= 10))

    def test_deep(self):
        d = dict(a=7, b=5)
        self.assertIn(d, CHECK(BWC['a'] == 7))
        self.assertIn(d, CHECK(BWC.get('b') - 3 == 2))

        class X(object):
            def y(self, x):
                return x
        self.assertIn(X(), BWC.y(x=5) == 5)

    def test_pos(self):
        bwc = BWC < 5
        self.assertIs(+bwc, +bwc)
        self.assertIs(+bwc, ++bwc)

class TestCollectionConstraints(unittest.TestCase):
    def test_list(self):
        self.assertIn([2, 3, 4], LIST())
        self.assertNotIn((2, 3, 4), LIST())
        self.assertIn([2, 3, 4], LIST(int))
        self.assertNotIn(['hello', 3, 4], LIST(int))

    def test_tuple(self):
        self.assertIn((2, 3, 4), TUPLE())
        self.assertNotIn([2, 3, 4], TUPLE())
        self.assertIn((2, 3, 4), TUPLE(int))
        self.assertNotIn(('hello', 3, 4), TUPLE(int))

    def test_array(self):
        self.assertIn((2, 3, 4), ARRAY())
        self.assertIn([2, 3, 4], ARRAY())
        self.assertIn((2, 3, 4), CHECK([int]))
        self.assertNotIn(('hello', 3, 4), ARRAY(int))

class TestSequenceConstraints(unittest.TestCase):
    def test_simple(self):
        self.assertIn((3, 4, 5), CHECK((int, int, int)))

    def test_addition(self):
        self.assertIn((3, 4, 5), SEQ(int, int) + ISA(int))
        self.assertIn((3, 4, 5), SEQ(int, int) + SEQ(int))
        self.assertIn((3, 4, 5), ISA(int) + SEQ(int, int))
        self.assertIn((3, 4, 5), ISA(int) + ISA(int) + ISA(int))

    def test_multiplication(self):
        self.assertIn((3, 4, 5), ISA(int) * 3)
        self.assertIn((3, 4, 5), 3 * ISA(int))

    def test_collection_sequence(self):
        self.assertIn((3, 4, 5), CHECK([ISA(int) * 3]))
        self.assertNotIn((3, 4, 'hello'), CHECK([ISA(int) * 3]))

    def test_non_iterable(self):
        self.assertNotIn(3, CHECK([ISA(int) * 3]))

    def test_bad_lengths(self):
        self.assertNotIn((3, 4), CHECK([ISA(int) * 3]))
        self.assertNotIn((3, 4, 5, 6), CHECK([ISA(int) * 3]))

