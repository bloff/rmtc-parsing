import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.Generator import Generator
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom

#from rmtc.Generation.SpecialForms.AugAssign import *


from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element


##=====================
from rmtc.Syntax.Seq import Seq


def ctx_from_domain(GC:GenerationContext):
    if GC.domain == LVDom:
        return ast.Store()
    elif GC.domain == DelDom:
        return ast.Del()
    else:
        return ast.Load()

def expr_wrap(code, GC:GenerationContext):
    if GC.domain == SDom:
        return ast.Expr(code)
    return code

##=====================




class SpecialForm(Generator):

    HEADTEXT = None
    LENGTH = None
    DOMAIN = None

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()

    def precheck(self, element:Element, GC:GenerationContext):
        acode = element.code
        # assert isinstance(acode[0], Identifier) ?
        if self.HEADTEXT:
            assert self.HEADTEXT == acode[0].code.full_name
        if self.LENGTH:
            if isinstance(self.LENGTH, int):
                # if a number
                assert self.LENGTH == len(acode)
            else:
                # if range or list
                assert len(acode) in self.LENGTH
        if self.DOMAIN:
            if isinstance(self.DOMAIN, int):
                assert self.DOMAIN == GC.domain
            else:
                # if list or set
                assert GC.domain in self.DOMAIN


    @staticmethod
    def expr_wrap(code, GC:GenerationContext):
        if GC.domain == SDom:
            return ast.Expr(code)
        return code


##=================================
#
# import
#
# global
# nonlocal
#
# class
#
# attribute
#





class Attribute(SpecialForm):

# #(. base_object attribute_name)

    HEADTEXT = "."
    LENGTH = 3

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain=ExDom):
            base_object_code = GC.generate(acode[1])

        att_name = acode[2].code.full_name

        if GC.domain == LVDom:
            return ast.Attribute(base_object_code, att_name, ast.Store())

        elif GC.domain == DelDom:
            return ast.Attribute(base_object_code, att_name, ast.Del())

        else:
            return ast.Attribute(base_object_code, att_name, ast.Load())














