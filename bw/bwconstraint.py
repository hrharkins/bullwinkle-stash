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

Collection Constraints
======================

Deeper structures can be modelled by using various constraint types:

    >>> from bw import LIST, TUPLE, ARRAY
    >>> [] in LIST()
    True
    >>> () in LIST()
    False

ARRAY acts like LIST or TUPLE:

    >>> () in ARRAY()
    True
    >>> [] in ARRAY()
    True

The specification itself can define constraints for the members of the
collection:

    >>> [2, 3, 4] in LIST(int)
    True
    >>> ['hello', 3, 4] in LIST(int)
    False

And can be checked deeply:

    >>> [(2, 3), 5] in LIST(TUPLE(int), int)
    True

Unfortunately, this does require validating all of the members, so the
inner checks should only be used if performance allows.

ARRAY can also be defined by wrapping the constraints in [ ... ] in ANY,
ALL, CHECK, etc:

    >>> ANY([])
    ANY(ARRAY())
    >>> (1, 2, 3) in ANY([])
    True
    >>> [1, 2, 3] in ANY([])
    True
    >>> ([1, 2], ['hello']) in ANY([[int],[str]])
    True

Sequence Constraints
====================

Like collections, the individual elements of sequences can be checked:

    >>> from bw import SEQ
    >>> (1, 2, 'hello') in SEQ(int, int, str)
    True
    >>> (1, 'hello', 'hello') in SEQ(int, int, str)
    False

These can be combined with collection constraints to check both the type of
collection and the sequence of elements.  In addition, sequences can be
short-formed by using tuple:

    >>> [1, 2, 'hello'] in ANY([(int, int, str)])
    True
    >>> [1, 'hello', 'hello'] in ANY([(int, int, str)])
    False

The sequence lengths must match up:

    >>> [1, 2] in SEQ(int, int, int)
    False
    >>> [1, 2, 3, 4] in SEQ(int, int, int)
    False

Sequences can also be combined via addition:

    >>> ISA(int) + ISA(int)
    SEQ(ISA(int), ISA(int))
    >>> SEQ(int, int) + SEQ(int)
    SEQ(ISA(int), ISA(int), ISA(int))
    >>> SEQ(int, int) + ISA(int)
    SEQ(ISA(int), ISA(int), ISA(int))
    >>> ISA(int) + SEQ(int, int)
    SEQ(ISA(int), ISA(int), ISA(int))

Multiplication also works, but only in a brute-force manner currently:

    >>> 3 * ISA(int)
    SEQ(ISA(int), ISA(int), ISA(int))
    >>> (3, 4, 5, 'hello') in ISA(int) * 3 + ISA(str)
    True

Dictionary Constraints
======================

Python dictionaries can also be checked:

    >>> from bw import DICT
    >>> dict(x=5) in DICT(x=int)
    True
    >>> dict(x='hello') in DICT(x=int)
    False

A default constraint can be specified without a keyword argument:

    >>> dict(x=1) in DICT(int)
    True
    >>> dict(x=1.0) in DICT(int, float)
    True

If any keys are provided, only the keys specified are allowed.  Use ALWAYS
as the default constraint to do otherwise:

    >>> from bw import ALWAYS, NEVER
    >>> DICT(x=int)
    DICT(NEVER, x=ISA(int))
    >>> dict(x=1, y='hello') in DICT(x=int)
    False
    >>> dict(x=1, y='hello') in DICT(ALWAYS, x=int)
    True

If no constraints are specified, any dictionary is allowed:

    >>> dict(x=1) in DICT()
    True

Like collections, dictionary constraints can be created in shorthand.  They
are created in ALWAYS mode by default  Provide a None key to check
otherwise:

    >>> from bw import DEFAULT
    >>> dict(x=1) in ANY([], {'x': int})
    True
    >>> dict(x=1, y=1) in ANY([], {'x': int})
    True
    >>> dict(x=1, y=1) in ANY([], {DEFAULT: NEVER, 'x': int})
    False

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
dictionary:

    >>> any_number['hello']
    Traceback (most recent call last):
        ...
    ValueError: 'hello' not valid for ISA(int, float, complex)

The value is returned if it is valid:

    >>> any_number[7]
    7

If a tuple, or multiple arguments are provided, they are returned as such:

    >>> any_number[7, 8, 9]
    (7, 8, 9)
    >>> any_number['hello',]
    Traceback (most recent call last):
        ...
    ValueError: 'hello' not valid for ISA(int, float, complex)

Filtering
=========

The .filter and .filter_out methods provide means to return the included or
excluded sets of inputs that match the constraint.  By default, the input
type is preserved:

    >>> any_number.filter(['hello', 7, 8])
    [7, 8]
    >>> any_number.filter_out(['hello', 7, 8])
    ['hello']

Generators are also acceptable, but returns a generator in turn:

    (Necessary for Python2/3 unified doctests)
    >>> try: ignore = xrange
    ... except NameError: xrange = range 

    >>> type((+(BWC < 5)).filter(xrange(10))).__name__
    'generator'

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
AUTO = type(None)           # TODO: Better singleton constant
DEFAULT = type(None)        # TODO: Better singleton constant

# TODO: Move to util
def filtration(src, srctype, factory=AUTO):
    '''
    Convenience function to create an output for src generator based on the
    factory and srctype specified.
    '''

    if factory is AUTO:
        if issubclass(srctype, (tuple, list, set, frozenset)):
            factory = srctype
        else:
            factory = None
    if factory is not None:
        return factory(src)
    else:
        return src

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

    def __div__(self, other):           # -no-py3-ut (deprecated)
        return BWConstraintGenerator('(%r) / (%r)' % (self, other))

    def __rdiv__(self, other):          # -no-py3-ut (deprecated)
        return BWConstraintGenerator('(%r) / (%r)' % (other, self))

    def __truediv__(self, other):       # -no-py2-ut (py3/future)
        return BWConstraintGenerator('(%r) / (%r)' % (self, other))

    def __rtruediv__(self, other):      # -no-py2-ut (py3/future)
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
        if type(obj) is dict:
            default = obj.pop(DEFAULT, ALWAYS)
            return cls.constraint_dict(default, **obj)
        if type(obj) is list:
            return cls.constraint_array(*obj, **_kw)
        if type(obj) is tuple:
            return cls.constraint_sequence(*obj, **_kw)
        if isinstance(obj, type):
            return cls.constraint_pytype(obj, **_kw)
        else:
            return cls.constraint_pyobject(obj, **_kw)

    def __call__(self, *_checks, **_kw):
        return self

    def __getitem__(self, checks):
        if isinstance(checks, tuple):
            for check in checks:
                if check not in self:
                    raise ValueError('%r not valid for %r' % (check, self))
        else:
            if checks not in self:
                raise ValueError('%r not valid for %r' % (checks, self))
        return checks

    def convert(self, source, invalid):
        return invalid                  # -nout

    @classmethod
    def register(cls, name, attr=None):
        def registrar(target_cls):
            if attr is None:
                factory = target_cls
            else:
                factory = getattr(target_cls, attr)
            setattr(cls, name, factory)
            return target_cls
        return registrar

    @classmethod
    def singleton(cls, name, **_kw):
        def registrar(target_cls):
            setattr(cls, name, target_cls(**_kw))
            return cls
        return registrar

    def filter(self, src, make=AUTO):
        return filtration((item for item in src if item in self),
                          type(src), make)

    def filter_out(self, src, make=AUTO):
        return filtration((item for item in src if item not in self),
                          type(src), make)

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

    def __add__(self, other):
        if isinstance(other, BWSequenceConstraint):
            return other.__radd__(self)
        else:
            return SEQ(*(self, other))

    def __mul__(self, count):
        return SEQ(*(self,) * count)

    def __rmul__(self, count):
        return SEQ(*(self,) * count)

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
        return self.repr_in(self.repr_constraint(c) for c in self.constraints)

    def repr_constraint(self, constraint):
        return repr(constraint)

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

class BWCollectionConstraint(BWManyInputConstraint):
    collection_types = ()
    collection_fmt = '%s'

    def check_in(self, nominee, constraints):
        check_all = False
        check_all_okay = False
        for constraint in constraints:
            fn = getattr(constraint, 'check_all', None)
            if fn is not None:
                check_all = True
                if fn(nominee):
                    check_all_okay = True
                    break
        if check_all and not check_all_okay:
            return False
        if isinstance(nominee, self.collection_types):
            if constraints:
                for item in nominee:
                    for constraint in constraints:
                        if (not hasattr(constraint, 'check_all')
                            and item in constraint):
                            return True
                    else:
                        # Allow True result if check_all occurred and
                        # we got here (so they passed).
                        return check_all
            else:
                return True
        else:
            return False

    def repr_in(self, constraint_strs): # -nout
        return self.collection_fmt % ', '.join(constraint_strs)

@BWConstraint.register('constraint_list', 'from_multi')
class BWListConstraint(BWCollectionConstraint):
    collection_types = (list,)
    collection_fmt = 'LIST(%s)'
LIST = BWListConstraint.from_multi

@BWConstraint.register('constraint_tuple', 'from_multi')
class BWTupleConstraint(BWCollectionConstraint):
    collection_types = (tuple,)
    collection_fmt = 'TUPLE(%s)'
TUPLE = BWTupleConstraint.from_multi

@BWConstraint.register('constraint_array', 'from_multi')
class BWArrayConstraint(BWListConstraint, BWTupleConstraint):
    collection_types = (list, tuple)
    collection_fmt = 'ARRAY(%s)'
ARRAY = BWArrayConstraint.from_multi

@BWConstraint.register('constraint_dict', 'from_dict')
class BWDictionaryConstraint(BWConstraint):
    def __init__(_self, _default_constraint=ALWAYS, **_key_constraints):
        _self.default_constraint = _default_constraint
        _self.key_constraints = _key_constraints

    def check(self, nominee):
        default = self.default_constraint
        for key in nominee:
            check = self.key_constraints.get(key, default)
            if check is not None:
                if nominee[key] not in check:
                    return False
        else:
            return True

    @classmethod
    def from_dict(_cls, *_default_constraint, **_kw):
        if len(_default_constraint) > 1:
            _default_constraint = ANY(*_default_constraint)
        elif len(_default_constraint) == 1:
            _default_constraint = _cls.from_generic(_default_constraint[0])
        elif _kw:
            _default_constraint = NEVER
        else:
            _default_constraint = ALWAYS

        return _cls(_default_constraint,
                    **dict((name, _cls.from_generic(value))
                           for (name, value) in _kw.items()))

    def __repr__(self):         # -nout
        args = []
        if self.default_constraint:
            args.append(repr(self.default_constraint))
        for key in self.key_constraints:
            args.append('%s=%r' % (key, self.key_constraints[key]))
        return 'DICT(%s)' % ', '.join(args)
DICT = BWDictionaryConstraint.from_dict

@BWConstraint.register('constraint_sequence', 'from_multi')
class BWSequenceConstraint(BWManyInputConstraint):
    def check_in(self, nominee, constraints):
        try:
            src = iter(nominee)
        except TypeError:           # -nodt -- edge case for unittest
            return False
        for constraint in constraints:
            for item in src:
                if item not in constraint:
                    return False
                break   # Get next item and constraint.
            else:
                # Out of items.
                return False
        else:
            for item in src:
                return False        # Too many items
            else:
                return True         # All good...

    def check_all(self, nominee):
        return self.check(nominee)

    def repr_in(self, constraint_strs): # -nout
        return 'SEQ(%s)' % ', '.join(constraint_strs)

    def __add__(self, other):
        if isinstance(other, BWSequenceConstraint):
            return type(self)(*(self.constraints + other.constraints))
        else:
            return type(self)(*(self.constraints + (other,)))

    def __radd__(self, other):
        return type(self)(*((other,) + self.constraints))
SEQ = BWSequenceConstraint.from_multi

