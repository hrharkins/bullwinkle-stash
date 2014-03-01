'''
Metamethods
===========

>>> from bw import BWClass
>>> @BWClass()
... class ClassOnlyMethodDemo:
...     @BWClass.meta_method
...     def hidden(cls):
...         return 'Here'
...
...     @BWClass.meta_method('renamed')
...     def __meta_renamed(cls):
...         return 'Here'
...
...     @classmethod
...     def normal(cls):
...         return 'There'

>>> ClassOnlyMethodDemo.normal()
'There'
>>> ClassOnlyMethodDemo().normal()
'There'
>>> ClassOnlyMethodDemo.hidden()
'Here'
>>> ClassOnlyMethodDemo.renamed()
'Here'
>>> ClassOnlyMethodDemo().hidden()
Traceback (most recent call last):
    ...
AttributeError: 'ClassOnlyMethodDemo' object has no attribute 'hidden'

Method Modifiers
================

>>> from bw import BWClass

>>> @BWClass()
... class Base:
...     def before(self):
...         print("Base")
...         return "before"
...     def after(self):
...         print("Base")
...         return "after"
...     def preempt(self):
...         print("Base")
...         return "preempt"
...     def filter(self):
...         print("Base")
...         return "filter"
...     def around(self):
...         print("Base")
...         return "around"

>>> @BWClass(Base)
... class Sub:
...     @BWClass.before_super
...     def before(self):
...         print("Sub")
...         return 'before-override'
...     @BWClass.after_super
...     def after(self):
...         print("Sub")
...         return 'after-override'
...     @BWClass.preempt_super
...     def preempt(self):
...         print("Sub")
...         return 'preempt-override'
...     @BWClass.preempt_super(super_method='preempt')
...     def preempt_default(self):
...         print("Sub")
...         return BWClass.DEFAULT
...     @BWClass.filter_super
...     def filter(self, result):
...         print("Sub -- " + result)
...         return "<" + result + ">"
...     @BWClass.around_super
...     def around(self, superfn):
...         print("Sub -- pre")
...         result = superfn()
...         print("Sub -- post -- " + result)
...         return "<" + result + ">"

>>> sub = Sub()
>>> sub.preempt()
Sub
'preempt-override'
>>> sub.preempt_default()
Sub
Base
'preempt'
>>> sub.before()
Sub
Base
'before'
>>> sub.after()
Base
Sub
'after'
>>> sub.filter()
Base
Sub -- filter
'<filter>'
>>> sub.around()
Sub -- pre
Base
Sub -- post -- around
'<around>'

Roles
=====

>>> from bw import BWRole
>>> class WithCounter(BWRole):
...     counter = BWRole.member(0)
...
...     @BWRole.method
...     def count(other):
...         other.counter += 1

>>> @WithCounter()
... @BWClass()
... class Hello:
...     pass

>>> hello = Hello()
>>> hello.count()
>>> hello.counter
1

>>> @BWClass(BWRole)
... class WithDynamicCounter:
...     def __init__(self, counter_name='counter', inc_method='hello'):
...         self.counter_name = counter_name
...         self.inc_method = inc_method
...
...     @BWClass.after_super
...     def apply_to(self, cls):
...         counter = [0]
...         method = self.inc_method
...         name = self.counter_name
...         fn = getattr(cls, method)
...
...         def wrapper(other, *_args, **_kw):
...             result = fn(other, *_args, **_kw)
...             counter[0] += 1
...             setattr(other, name, counter[0])
...             return result
...
...         setattr(cls, method, wrapper)

>>> @WithDynamicCounter(counter_name='greetings', inc_method='hello')
... @BWClass()
... class Greeter:
...     def hello(self):
...         return "Howdy!"

>>> greeter = Greeter()
>>> greeter.hello()
'Howdy!'
>>> greeter.greetings
1

Registered Types
================

>>> @BWClass(register=True)
... class MyClass:
...     pass
>>> BWClass['MyClass'] is MyClass
True

>>> @BWClass(BWRole, register=True)
... class MyRole:
...     pass
>>> BWClass['MyRole'] is MyRole
True

>>> @BWClass('MyClass')
... class MySubclass:
...     pass
>>> isinstance(MySubclass(), MyClass)
True

'''

from bw.bwutil import debug, basestr

DELETE = type(None)
DEFAULT = type(None)

class BWMeta(type):
    def __bwtypesetup__(cls, top):
        for name in dir(cls):
            value = getattr(cls, name)
            fn = getattr(value, '__bwtypeattr__', None)
            if fn is True:
                fn = value
            if fn is not None:
                result = fn(cls, name, top)
                if result is not None:
                    setattr(cls, name, result)

class BWMetaFactory(object):
    metatype = BWMeta

    def __init__(self, *_bases, **_config):
        self.bases = _bases
        self.init(**_config)

    def init(self, register=None):
        self.register = register

    def __call__(self, cls):
        bases = self.filter_subbases(cls.__bases__ + type(self)[self.bases])
        clsdict = dict(cls.__dict__)
        clsdict.pop('__dict__', None)
        meta = self.make_meta(cls.__name__, bases, clsdict)
        newcls = meta(cls.__name__, bases, clsdict)
        self.prepare_class(newcls)
        if self.register:
            type(self).register(newcls)
        return newcls

    def filter_subbases(self, bases):
        filtered = []
        for base in bases:
            if not any(base is not check and issubclass(check, base)
                       for check in bases):
                filtered.append(base)
        return tuple(filtered)

    def make_meta(self, clsname, clsbases, clsdict):
        if not clsbases:
            clsbases = (object,)        # -no-py3-dt, -no-py3-ut
        metatype = self.get_metatype()
        metabases = [metatype]
        metabases.extend(type(base) for base in clsbases)

        filtered = self.filter_subbases(metabases)

        return type('<%s>' % clsname, filtered, {})

    def get_metatype(self):
        return self.metatype

    def prepare_class(self, newcls):
        newcls.__bwtypesetup__(newcls)

    @classmethod
    def typeattr_fn(cls, attrfn=None, fn=None):
        if attrfn is None:
            return lambda f: cls.typeattr_fn(f, fn)
        if fn is None:
            attrfn.__bwtypeattr__ = True
            return attrfn
        else:
            fn.__bwtypeattr__ = attrfn
            return fn

    @classmethod
    def meta_method(cls, fn, metaname=None):
        if isinstance(fn, basestr):
            return lambda f: cls.meta_method(f, fn)

        @staticmethod
        @cls.typeattr_fn
        def metamethod_init(incls, name, top, metaname=metaname, fn=fn):
            if metaname is None:
                metaname = name
            fn.__name__ = metaname
            setattr(type(incls), metaname, fn)
            delattr(incls, name)

        return metamethod_init

class BWMetaFactoryMeta(type):
    def __getitem__(factory, query):
        if type(query) is tuple:
            return tuple(factory[base] if isinstance(base, basestr) else base
                         for base in query)
        else:
            return factory.__dict__.get(':bw:' + query)

    def register(factory, cls):
        setattr(factory, ':bw:' + cls.__name__, cls)

BWMetaFactory = BWMetaFactoryMeta(
        BWMetaFactory.__name__,
        BWMetaFactory.__bases__,
        dict(BWMetaFactory.__dict__))

class BWClassMeta(BWMeta):
    pass

def decorator(wrapper):
    def consumer(fn=None, **_kw):
        if fn is None:
            return lambda f: consumer(f, **_kw)
        else:
            return wrapper(fn, **_kw)
    consumer.__name__ = '*' + wrapper.__name__
    return consumer

@decorator
def method_modifier(modificiation_fn):
    @decorator
    def modifier_wrapper(modifier_fn, super_method=None):
        @BWMetaFactory.typeattr_fn
        def binder(targetcls, name, topcls, super_method=super_method):
            if super_method is None:
                super_method = name
            superfn = getattr(super(topcls, targetcls), super_method, None)
            wrapper = modificiation_fn(targetcls, modifier_fn, superfn)
            return wrapper
        return staticmethod(binder)
    return staticmethod(modifier_wrapper)

class BWClass(BWMetaFactory):
    metatype = BWClassMeta
    DEFAULT = DEFAULT

    @method_modifier
    def after_super(cls, after_fn, superfn):
        def wrapper(_self, *_args, **_kw):
            result = superfn(_self, *_args, **_kw)
            after_fn(_self, *_args, **_kw)
            return result
        return wrapper

    @method_modifier
    def before_super(cls, before_fn, superfn):
        def wrapper(_self, *_args, **_kw):
            before_fn(_self, *_args, **_kw)
            return superfn(_self, *_args, **_kw)
        return wrapper

    @method_modifier
    def preempt_super(cls, before_fn, superfn):
        def wrapper(_self, *_args, **_kw):
            result = before_fn(_self, *_args, **_kw)
            if result is DEFAULT:
                return superfn(_self, *_args, **_kw)
            else:
                return result
        return wrapper

    @method_modifier
    def filter_super(cls, filter_fn, superfn):
        def wrapper(_self, *_args, **_kw):
            result = superfn(_self, *_args, **_kw)
            return filter_fn(_self, result, *_args, **_kw)
        return wrapper

    @method_modifier
    def around_super(cls, around_fn, superfn):
        def wrapper(_self, *_args, **_kw):
            def super_caller(*_a, **_kw):
                return superfn(_self, *_a, **_kw)
            return around_fn(_self, super_caller, *_args, **_kw)
        return wrapper

    method_modifier = staticmethod(method_modifier)

@BWClass()
class BWRole(object):
    def __call__(self, cls):
        self.apply_to(cls)
        return cls

    def apply_to(self, cls):
        for base in reversed(type(self).__mro__):
            for name in base.__dict__:
                value = base.__dict__[name]
                fn = getattr(value, '__bwroleinit__', None)
                if fn is True:
                    fn = value
                if fn is not None:
                    fn(cls, base, name)

    @classmethod
    def roleinit_fn(cls, fn):
        fn.__bwroleinit__ = True
        return fn

    @classmethod
    def member(cls, value):
        @cls.roleinit_fn
        def member_setup(target, base, name, value=value):
            setattr(target, name, value)
        return member_setup

    @classmethod
    def method(cls, fn):
        @cls.roleinit_fn
        def method_setup(target, base, name, fn=fn):
            setattr(target, name, fn)
        return method_setup

