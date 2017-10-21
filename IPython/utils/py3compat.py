# coding: utf-8
"""Compatibility tricks for Python 3. Mainly to do with unicode."""
import functools
import re
import platform

from .encoding import DEFAULT_ENCODING


def decode(s, encoding=None):
    encoding = encoding or DEFAULT_ENCODING
    return s.decode(encoding, "replace")


def encode(u, encoding=None):
    encoding = encoding or DEFAULT_ENCODING
    return u.encode(encoding, "replace")


def cast_unicode(s, encoding=None):
    return s


def cast_bytes(s, encoding=None):
    return encode(s, encoding)


def _modify_str_or_docstring(str_change_func):
    @functools.wraps(str_change_func)
    def wrapper(func_or_str):
        if isinstance(func_or_str, (str,)):
            func = None
            doc = func_or_str
        else:
            func = func_or_str
            doc = func.__doc__

        # PYTHONOPTIMIZE=2 strips docstrings,
        # so they can disappear unexpectedly
        if doc is not None:
            doc = str_change_func(doc)

        if func:
            func.__doc__ = doc
            return func
        return doc
    return wrapper


def safe_unicode(e):
    """unicode(e) with various fallbacks. Used for exceptions, which may not be
    safe to call unicode() on.
    """
    try:
        return str(e)
    except UnicodeError:
        pass

    try:
        return repr(e)
    except UnicodeError:
        pass

    return u'Unrecoverably corrupt evalue'

# keep reference to builtin_mod because the kernel overrides that value
# to forward requests to a frontend.
def input(prompt=''):
    return builtin_mod.input(prompt)

builtin_mod_name = "builtins"
import builtins as builtin_mod


def execfile(fname, glob, loc=None, compiler=None):
    loc = loc if (loc is not None) else glob
    with open(fname, 'rb') as f:
        compiler = compiler or compile
        exec(compiler(f.read(), fname, 'exec'), glob, loc)


# Refactor print statements in doctests.
_print_statement_re = re.compile(r"\bprint (?P<expr>.*)$", re.MULTILINE)
def _print_statement_sub(match):
    expr = match.groups('expr')
    return "print(%s)" % expr


@_modify_str_or_docstring
def doctest_refactor_print(doc):
    """Refactor 'print x' statements in a doctest to print(x) style. 2to3
    unfortunately doesn't pick up on our doctests.

    Can accept a string or a function, so it can be used as a decorator."""
    return _print_statement_re.sub(_print_statement_sub, doc)


# Abstract u'abc' syntax:
@_modify_str_or_docstring
def u_format(s):
    """"{u}'abc'" --> "'abc'" (Python 3)

    Accepts a string or a function, so it can be used as a decorator."""
    return s.format(u='')


PYPY = platform.python_implementation() == "PyPy"
