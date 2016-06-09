"""
A pretty-printing dump function for the ast module.  The code was copied from
the ast.dump function and modified slightly to pretty-print.

Alex Leone (acleone ~AT~ gmail.com), 2010-01-30

From http://alexleone.blogspot.co.uk/2010/01/python-ast-pretty-printer.html
"""

from ast import *

def dump(node, annotate_fields=True, include_attributes=False, indent='  '):
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, level=0):
        if isinstance(node, AST):
            fields = [(a, _format(b, level)) for a, b in iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, _format(getattr(node, a), level))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                           if annotate_fields else
                           (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                         for x in node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(node)

    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)

def parseprint(code, filename="<string>", mode="exec", **kwargs):
    """Parse some code from a string and pretty-print it."""
    node = parse(code, mode=mode)   # An ode to the code
    print(dump(node, **kwargs))

# Short name: pdp = parse, dump, print
pdp = parseprint


pyast = parse("""a = 1
print(a)

def f():
    print(a)

f()""")

pyast2 = Module(body=[
    Assign(targets=[
        Name(id='a', ctx=Store()),
      ], value=Num(n=1)),
    Expr(value=Call(func=Name(id='print', ctx=Load()), args=[
        Name(id='a', ctx=Load()),
      ], keywords=[])),
    FunctionDef(name='f', args=arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
        Expr(value=Call(func=Name(id='print', ctx=Load()), args=[
            Name(id='a', ctx=Load()),
          ], keywords=[])),
      ], decorator_list=[], returns=None),
    Expr(value=Call(func=Name(id='f', ctx=Load()), args=[], keywords=[])),
  ])

fix_missing_locations(pyast2)

pyast3 = Module(body=[
    Import(names=[
        alias(name='anoky.importer', asname='__akyimp__'),
      ]),
    Import(names=[
        alias(name='anoky.module', asname='__aky__'),
      ]),
    Assign(targets=[
        Name(id='__macros__', ctx=Store()),
      ], value=Dict(keys=[], values=[])),
    Assign(targets=[
        Name(id='__id_macros__', ctx=Store()),
      ], value=Dict(keys=[], values=[])),
    Assign(targets=[
        Name(id='__special_forms__', ctx=Store()),
      ], value=Dict(keys=[], values=[])),
    Assign(targets=[
        Name(id='a', ctx=Store()),
      ], value=Num(n=1)),
    Expr(value=Call(func=Name(id='print', ctx=Load()), args=[
        Name(id='a', ctx=Load()),
      ], keywords=[])),
    FunctionDef(name='f', args=arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
        Expr(value=Call(func=Name(id='print', ctx=Load()), args=[
            Name(id='a', ctx=Load()),
          ], keywords=[])),
      ], decorator_list=[], returns=None),
    Expr(value=Call(func=Name(id='f', ctx=Load()), args=[], keywords=[])),
  ])

fix_missing_locations(pyast3)


exec(compile(pyast, "<ast1>", mode="exec"))
exec(compile(pyast2, "<ast1>", mode="exec"))
exec(compile(pyast3, "<ast1>", mode="exec"))

pass