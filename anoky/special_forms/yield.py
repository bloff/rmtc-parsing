import ast

from anoky.generation.domain import ExpressionDomain, StatementDomain
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Yield(SpecialForm):

    HEADTEXT = "yield"
    #DOMIN =

    def generate(self, element:Element, GC:GenerationContext):

        assert GC.domain == StatementDomain

        acode = element.code

        if len(acode) == 1:
            return ast.Return(None)
        else:
            assert len(acode) == 2
            # TODO: return a, b, c => tuple

            with GC.let(domain=ExpressionDomain):
                expression_code = GC.generate(acode[1])

            return ast.Yield(expression_code)