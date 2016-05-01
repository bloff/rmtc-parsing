import ast

from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Return(SpecialForm):

# #(return expression?)

    HEADTEXT = "return"

    def generate(self, element:Element, GC:GenerationContext):

        assert GC.domain == SDom

        acode = element.code

        if len(acode) == 1:
            return ast.Return(None)
        else:
            assert len(acode) == 2
            # TODO: return a, b, c => tuple

            with GC.let(domain=ExpressionDomain):
                expression_code = GC.generate(acode[1])

            return ast.Return(expression_code)