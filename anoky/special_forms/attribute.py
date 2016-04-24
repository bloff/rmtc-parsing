import ast

from anoky.generation.domain import ExpressionDomain as ExDom, LValueDomain, DeletionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import expr_wrap
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


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
            return expr_wrap(ast.Attribute(base_object_code, att_name, ast.Load()), GC)