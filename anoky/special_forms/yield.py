import ast

from anoky.generation.domain import ExpressionDomain, StatementDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import expr_wrap
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Yield(SpecialForm):

    HEADTEXT = "yield"
    DOMAIN = [StatementDomain, ExpressionDomain]

    def generate(self, element:Element, GC:GenerationContext):
        self.precheck(element, GC)

        acode = element.code

        if len(acode) == 1:
            return ast.Return(None)
        else:
            assert len(acode) == 2
            # TODO: return a, b, c => tuple

            with GC.let(domain=ExpressionDomain):
                expression_code = GC.generate(acode[1])

            return expr_wrap(ast.Yield(expression_code), GC)