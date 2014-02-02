'''
bw.bwconstraint
===============

Manages validity tests of Python objects.

Constraint Basics
=================

To create a constraint object, start with ISA, EXPR, ANY or ALL and provide
the desired constraints:

    >>> from bw import ISA, ANY, ALL, BWC
    >>> any_str = ISA(str)
    >>> any_int_less_than_5 = ALL(int, BWC < 5)
    >>> any_number = ISA(int, float, complex)
    >>> color_enum = ANY('red', 'blue', 'green')

To check a value against a constraint, use the "in" operator:

    >>> 'hello' in any_str
    True
    >>> 3 in any_int_less_than_5
    True
    >>> 2 in any_number
    True
    >>> 'green' in color_enum
    True

    >>> 5 in any_str
    False
    >>> 3.0 in any_int_less_than_5
    False
    >>> 8 in any_int_less_than_5
    False
    >>> 'hello' in any_number
    False
    >>> 'gray' in color_enum
    False

Constraints can be negated via NOT:

    >>> from bw import NOT
    >>> 'white' in NOT(color_enum)
    True

Function Constraints
====================

The FN constraint takes a function to call and an optional name.  Providing
a name makes it easier to debug constraints.  If the name contains a '#',
then the function name is displayed as-is as opposed to a functiuonal
style:

    >>> from bw import FN
    >>> FN(lambda x: x < 7)
    <lambda>(#)
    >>> FN(lambda x: x < 7, '# < 7')
    # < 7

A generic EXPR option is provided, though it is not (necessarily)
recommended.  It exists since this could have been easily emulated
elsewhere and its use generates a warning.  This example shows how to
disable the warning message:

    >>> from bw import EXPR
    >>> import warnings
    >>> warnings.filterwarnings('ignore', 'bw-expr:')
    >>> EXPR('# < 7')
    # < 7

Safe Comparison Constraints
===========================

The BWC object allows for comparison constraint generation by simply
applying operators to it in Python.  BWC is assumed to be whatever is
checked when constraints are applied.  This technique should be limited to
some-what trivial cases, but as noted in the examples, some degree of
expressibility is possible:

    >>> from bw import BWC
    >>> 3 in (BWC < 5)
    True
    >>> 2 in (BWC > 5)
    False
    >>> 4 in ALL(BWC >= 1, BWC < 7)
    True
    >>> 9 in ALL(BWC > 1, BWC <= 7)
    False
    >>> 'hello' in (BWC == 'world')
    False
    >>> 'ack' in (BWC != 'oop')
    True

Even arithmatic operations are supported:

    >>> 1 in (BWC + 1 == BWC * 2)
    True
    >>> 2 in (BWC + 1 == BWC * 2)
    False

Attribute, item, and method accesses are also possible:

    >>> d = dict(a=5, b=7)
    >>> d in (BWC['a'] == 5)
    True
    >>> d in (BWC.get('b') == 7)
    True

BWC operations remain as BWC objects.  To convert a BWC object into a
constraint, use the +(...) operator.  This happens automatically with the
in operator, but to use a constraint methods, the BWC needs to be converted
first:

    >>> bwc = BWC + 5 < 10
    >>> bwc.filter
    (((#) + (5)) < (10)).filter
    >>> list((+bwc).filter([2, 3, 4, 5]))
    [2, 3, 4]

Constraints can be safely +'d as well.  In fact, the constraint of a BWC is
cached (so it is safe and efficient to re-+ a BWC):

    >>> +bwc is ++bwc
    True
    >>> +++bwc is ++++bwc
    True

Think of a BWC as a lightwieght and safe EXPR constructor.

Protection Checks
=================

To check a value and throw an exception on failure, use the constraint as a
callable:

    >>> any_number('hello')
    Traceback (most recent call last):
        ...
    ValueError: 'hello' not valid for ISA(int, float, complex)

The value is returned if it is valid:

    >>> any_number(7)
    7

Multiple values can be checked simulatneously, but are not returned:

    >>> any_number(7, 8, 9)

Filtering
=========

The .filter and .filter_out methods provide means to return the included or
excluded sets of inputs that match the constraint.  A generator is
produced, so the result needs to be wrapped in other constructs if desired:

    >>> list(any_number.filter(('hello', 7, 8)))
    [7, 8]
    >>> list(any_number.filter_out(('hello', 7, 8)))
    ['hello']

Conversions
===========

Type constraints can also be used to coerce values.  To do this, the >>
or << operator is applied to the constraint:

    >>> ANY(int) << 7.0
    7
    >>> ANY(int, float) << '7'
    7
    >>> ISA(int) << 'hello'
    Traceback (most recent call last):
        ...
    TypeError: Cannot convert 'hello' into ISA(int)

Results of conversions are checked to make sure they produce a reasonable
value:

    >>> ALL(int, BWC < 7) << '5'
    5

In this case, '8' will get converted (because int worked first), but will
fail because it still doesn't match the FN:

    >>> ALL(int, BWC < 7) << '8'
    Traceback (most recent call last):
        ...
    TypeError: Cannot convert '8' into ALL(ISA(int), (#) < (7))

Compare to this, which is okay simply because an int conversion occurred: 

    >>> ANY(int, BWC < 7) << '8'
    8

Functions can be used for conversion as well if via INTO():

    >>> from bw import INTO
    >>> max_5 = INTO(lambda x: min(x + 0, 5), '# < 5')
    >>> max_5 << 3
    3
    >>> max_5 << 7
    5

Errors in INTO functions are silently ignored, but may still trigger
constraint failures:

    >>> 'hello' >> max_5
    Traceback (most recent call last):
        ...
    TypeError: Cannot convert 'hello' into INTO(# < 5)

Coersions that are already valid do not affect the source:

    >>> class X(object): pass
    >>> x = X()
    >>> (ANY(X) << x) is x
    True

Never and Always
================

Occasionally a constraint placeholder is necessary that is always or never
true:

    >>> from bw import NEVER, ALWAYS
    >>> 5 in NEVER
    False
    >>> 7 in ALWAYS
    True

These will either pass-through or always reject conversions:

    >>> 5 >> ALWAYS
    5
    >>> 5 >> NEVER
    Traceback (most recent call last):
        ...
    TypeError: Cannot convert 5 into NEVER

These can also be used to defeat other constraints:

    >>> NEVER & ISA(int)
    ALL(NEVER, ISA(int))
    >>> ALWAYS | ISA(int)
    ANY(ALWAYS, ISA(int))

ISA, IS, and IN
===============

Sometimes it is necessary to be explicit about the type of checking being
performed to avoid generic coersions:

    >>> from bw import ISA, IS, IN
    >>> 5 in ANY(IN(int))
    False
    >>> int in ANY(IN(int))
    True

IS differs from IN the same way as == differs from "is":

    >>> class X(object):
    ...     def __eq__(self, other):
    ...         return type(other) is type(self)
    >>> x1 = X()
    >>> x2 = X()
    >>> x3 = X()
    >>> x3 in IN(x1, x2)
    True
    >>> x3 in IS(x1, x2)
    False

ANY and ALL behave like ALWAYS when empty:

    >>> 5 in ANY()
    True
    >>> 5 in ALL()
    True

Chaining Constraints
====================

The &, |, and ~ operators work like ANY, ALL, and NOT:

    >>> ISA(int) & +(BWC < 7)
    ALL(ISA(int), (#) < (7))
    >>> ISA(int) | ISA(float)
    ANY(ISA(int), ISA(float))
    >>> IN('red') | IN('blue', 'green')
    ANY(IN('red'), IN('blue', 'green'))
    >>> ~IS(None)
    NOT(IS(None))

'''

import warnings

try:
    from StringIO import StringIO
except ImportError:         # -nodt, -nout
    from io import StringIO

INVALID = type(None)        # TODO: Better singleton constant

class BWConstraintGenerator(str):   # -nodt (just too many...)
    def __neg__(self):
        return BWConstraintGenerator('-(%r)' % self)

    def __abs__(self):
        return BWConstraintGenerator('abs(%r)' % self)

    def __invert__(self):
        return BWConstraintGenerator('~(%r)' % self)

    def __add__(self, other):
        return BWConstraintGenerator('(%r) + (%r)' % (self, other))

    def __radd__(self, other):
        return BWConstraintGenerator('(%r) + (%r)' % (other, self))

    def __sub__(self, other):
        return BWConstraintGenerator('(%r) - (%r)' % (self, other))

    def __rsub__(self, other):
        return BWConstraintGenerator('(%r) - (%r)' % (other, self))

    def __mul__(self, other):
        return BWConstraintGenerator('(%r) * (%r)' % (self, other))

    def __rmul__(self, other):
        return BWConstraintGenerator('(%r) * (%r)' % (other, self))

    def __div__(self, other):           # -nout
        return BWConstraintGenerator('(%r) / (%r)' % (self, other))

    def __rdiv__(self, other):          # -nout
        return BWConstraintGenerator('(%r) / (%r)' % (other, self))

    def __truediv__(self, other):       # -no-py2-ut
        return BWConstraintGenerator('(%r) / (%r)' % (self, other))

    def __rtruediv__(self, other):      # -no-py2-ut
        return BWConstraintGenerator('(%r) / (%r)' % (other, self))

    def __mod__(self, other):
        return BWConstraintGenerator('(%r) %% (%r)' % (self, other))

    def __rmod__(self, other):
        return BWConstraintGenerator('(%r) %% (%r)' % (other, self))

    def __pow__(self, other):
        return BWConstraintGenerator('(%r) ** (%r)' % (self, other))

    def __rpow__(self, other):
        return BWConstraintGenerator('(%r) ** (%r)' % (other, self))

    def __floordiv__(self, other):
        return BWConstraintGenerator('(%r) // (%r)' % (self, other))

    def __rfloordiv__(self, other):
        return BWConstraintGenerator('(%r) // (%r)' % (other, self))

    def __divmod__(self, other):
        return BWConstraintGenerator('divmod(%r, %r)' % (self, other))

    def __lshift__(self, other):
        return BWConstraintGenerator('(%r) << (%r)' % (self, other))

    def __rlshift__(self, other):
        return BWConstraintGenerator('(%r) << (%r)' % (other, self))

    def __rshift__(self, other):
        return BWConstraintGenerator('(%r) >> (%r)' % (self, other))

    def __rrshift__(self, other):
        return BWConstraintGenerator('(%r) >> (%r)' % (other, self))

    def __and__(self, other):
        return BWConstraintGenerator('(%r) & (%r)' % (self, other))

    def __rand__(self, other):
        return BWConstraintGenerator('(%r) & (%r)' % (other, self))

    def __or__(self, other):
        return BWConstraintGenerator('(%r) | (%r)' % (self, other))

    def __ror__(self, other):
        return BWConstraintGenerator('(%r) | (%r)' % (other, self))

    def __xor__(self, other):
        return BWConstraintGenerator('(%r) ^ (%r)' % (self, other))

    def __rxor__(self, other):
        return BWConstraintGenerator('(%r) ^ (%r)' % (other, self))

    def __eq__(self, other):
        return BWConstraintGenerator('(%r) == (%r)' % (self, other))

    def __ne__(self, other):
        return BWConstraintGenerator('(%r) != (%r)' % (self, other))

    def __ge__(self, other):
        return BWConstraintGenerator('(%r) >= (%r)' % (self, other))

    def __le__(self, other):
        return BWConstraintGenerator('(%r) <= (%r)' % (self, other))

    def __gt__(self, other):
        return BWConstraintGenerator('(%r) > (%r)' % (self, other))

    def __lt__(self, other):
        return BWConstraintGenerator('(%r) < (%r)' % (self, other))

    def __getattr__(self, name):
        return BWConstraintGenerator('(%r).%s' % (self, name))

    def __getitem__(self, key):
        return BWConstraintGenerator('(%r)[(%r)]' % (self, key))

    def __call__(self, *_args, **_kw):
        args = []
        for arg in _args:
            args.append(repr(arg))
        for name in _kw:
            args.append('%s=%r' % (name, _kw[name]))
        return BWConstraintGenerator('%r(%s)' % (self, ', '.join(args)))

    def __pos__(self):
        constraint = self.__dict__.get('___BWCONSTRAINT___')
        if constraint is None:
            constraint \
                = FN(eval('lambda ____:' + str.replace(self, '#', '____')),
                     str(self))
            self.__dict__['___BWCONSTRAINT___'] = constraint
        return constraint

    def __contains__(self, nominee):
        return nominee in +self

    def __repr__(self):                 # -nout
        return str(self)

BWC = BWConstraintGenerator('#')

class BWConstraint(object):
    @classmethod
    def from_generic(cls, obj, **_kw):
        if isinstance(obj, BWConstraintGenerator):
            return +obj
        if isinstance(obj, BWConstraint):
            return obj(**_kw)
        if isinstance(obj, type):
            return cls.constraint_pytype(obj, **_kw)
        else:
            return cls.constraint_pyobject(obj, **_kw)

    def __call__(self, *_checks, **_kw):
        if _checks:
            for check in _checks:
                if check not in self:
                    raise ValueError('%r not valid for %r' % (check, self))
            else:
                if len(_checks) == 1:
                    return _checks[0]
        else:
            return self

    def convert(self, source, invalid):
        return invalid                  # -nout

    @classmethod
    def register(cls, name):
        def registrar(target_cls):
            setattr(cls, name, target_cls)
            return target_cls
        return registrar

    @classmethod
    def singleton(cls, name, **_kw):
        def registrar(target_cls):
            setattr(cls, name, target_cls(**_kw))
            return cls
        return registrar

    def filter(self, src):
        return (item for item in src if item in self)

    def filter_out(self, src):
        return (item for item in src if item not in self)

    def __contains__(self, nominee):
        return self.check(nominee)

    def __lshift__(self, source, INVALID=INVALID):
        result = self.coerce(source, INVALID)
        if result is INVALID:
            raise TypeError('Cannot convert %r into %r' % (source, self))
        else:
            return result
    __rrshift__ = __lshift__

    def coerce(self, source, invalid=None):
        if self.check(source):
            return source
        return self.convert(source, invalid)

    def __pos__(self):
        return self             # Compatibility with BWC

    def __or__(self, other):
        return ANY(self, other)

    def __and__(self, other):
        return ALL(self, other)

    def __invert__(self):
        return NOT(self)
CHECK = BWConstraint.from_generic

@BWConstraint.register('constraint_not')
class BWNotConstraint(BWConstraint):
    def __init__(self, constraint):
        self.constraint = constraint

    def check(self, nominee):
        return nominee not in self.constraint

    def __repr__(self):             # -nout
        return 'NOT(%r)' % self.constraint
NOT = BWNotConstraint

class BWManyInputConstraint(BWConstraint):
    '''
    Base class for constraints with zero or more inputs.
    '''

    def __init__(self, *_constraints, **_kw):
        self.constraints = _constraints

    def check(self, nominee):
        return self.check_in(nominee, self.constraints)

    def convert(self, source, invalid):
        return self.convert_in(source, self.constraints, invalid)

    def __repr__(self):             # -nout
        return self.repr_in(map(repr, self.constraints))

    @classmethod
    def from_multi(cls, *seq, **_kw):
        return cls(*(cls.from_generic(item) for item in seq), **_kw)

@BWConstraint.singleton('constraint_never')
class BWNeverConstraint(BWConstraint):
    def check(self, nominee):
        return False

    def convert(self, source, invalid):
        return invalid

    def __repr__(self):             # -nout
        return 'NEVER'
NEVER = BWNeverConstraint.constraint_never

@BWConstraint.singleton('constraint_always')
class BWAlwaysConstraint(BWManyInputConstraint):
    def check(self, nominee):
        return True

    def convert(self, source, invalid):
        return source           # -nodt -- won't be reached since check
                                #           happens first

    def __repr__(self):             # -nout
        return 'ALWAYS'
ALWAYS = BWAlwaysConstraint.constraint_always

@BWConstraint.register('constraint_any')
class BWAnyConstraint(BWManyInputConstraint):
    def check_in(self, nominee, constraints):
        if len(constraints):
            for constraint in constraints:
                if nominee in constraint:
                    return True
            else:
                return False
        else:
            return True

    def convert_in(self, source, constraints, invalid):
        for constraint in constraints:
            result = constraint.convert(source, invalid)
            if result is not INVALID and self.check(result):
                return result
        else:
            return invalid      # -nodt

    def repr_in(self, constraint_reprs):        # -nout
        return 'ANY(%s)' % ', '.join(constraint_reprs)
ANY = BWAnyConstraint.from_multi

@BWConstraint.register('constraint_all')
class BWAllConstraint(BWManyInputConstraint):
    def check_in(self, nominee, constraints):
        if len(constraints):
            for constraint in constraints:
                if nominee not in constraint:
                    return False
            else:
                return True
        else:
            return True

    def convert_in(self, source, constraints, invalid):
        for constraint in constraints:
            result = constraint.convert(source, invalid)
            if result is not INVALID and self.check(result):
                return result
        else:
            return invalid

    def repr_in(self, constraint_reprs):        # -nout
        return 'ALL(%s)' % ', '.join(constraint_reprs)
ALL = BWAllConstraint.from_multi

@BWConstraint.register('constraint_pyobject')
class BWInConstraint(BWConstraint):
    def __init__(self, *comparisons):
        self.comparisons = comparisons

    def check(self, nominee):
        return nominee in self.comparisons

    def __repr__(self):             # -nout
        return 'IN(%s)' % ', '.join(map(repr, self.comparisons))
IN = BWInConstraint

@BWConstraint.register('constraint_pyobject_is')
class BWIsConstraint(BWConstraint):
    def __init__(self, *choices):
        self.choices = choices

    def check(self, nominee):
        return any(nominee is choice for choice in self.choices)

    def __repr__(self):         # -nout
        return 'IS(%s)' % ', '.join(map(repr, self.choices))
IS = BWIsConstraint

class BWBareFunctionConstraint(BWConstraint):
    def __init__(self, fn, name=None, **_kw):
        self.fn = fn
        self.name = name or fn.__name__
        self.kw = _kw

    def check(self, nominee):
        return self.fn(nominee, **self.kw)

    def __repr__(self):         # -nout
        if '#' in self.name:
            return self.name
        else:
            return '%s(#)' % self.name
BARE_FN = BWBareFunctionConstraint

@BWConstraint.register('constraint_function')
class BWFunctionConstraint(BWBareFunctionConstraint):
    def check(self, nominee):
        try:
            return super(BWFunctionConstraint, self).check(nominee)
        except:                         # -nodt
            return False
FN = BWFunctionConstraint

@BWConstraint.register('constraint_expression')
class BWExpressionConstraint(BWFunctionConstraint):
    def __init__(self, expr, name=None, **_kw):
        warnings.warn('bw-expr: EXPR being used', RuntimeWarning, stacklevel=2)
        fn = eval('lambda ____:' + expr.replace('#', '____'))
        super(BWExpressionConstraint, self).__init__(fn, name or expr, **_kw)
EXPR = BWExpressionConstraint

@BWConstraint.register('constraint_conversion')
class BWConversionConstraint(BWConstraint):
    def __init__(self, fn, name=None, **_kw):
        self.fn = fn
        self.name = name or self.fn.__name__

    def check(self, nominee):
        return False

    def convert(self, source, invalid):
        try:
            return self.fn(source)
        except:
            return invalid

    def __repr__(self):         # -nout
        if '#' in self.name:
            return 'INTO(%s)' % self.name
        else:
            return 'INTO(%s(#))' % self.name    # -nodt
INTO = BWConversionConstraint

@BWConstraint.register('constraint_pytype')
class BWIsaConstraint(BWConstraint):
    def __init__(self, *types):
        self.types = types

    def check(self, nominee):
        return isinstance(nominee, self.types)

    def convert(self, source, invalid, **_kw):
        for to_type in self.types:
            try:
                return to_type(source, **_kw)
            except:
                pass
        else:
            return invalid

    def __repr__(self):         # -nout
        return 'ISA(%s)' % ', '.join(type.__name__ for type in self.types)
ISA = BWIsaConstraint

