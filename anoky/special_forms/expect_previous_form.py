import ast

from anoky.common.errors import CodeGenerationError
from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import expr_wrap
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element
from anoky.syntax.util import is_form, identifier_in


class ExpectPreviousForm(SpecialForm):

    DOMAIN = [SDom, ExpressionDomain]

    def __init__(self, expected_names:set):
        self.expected_names = expected_names

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)
        head_name = element.code[0].code.name

        if not is_form(element.prev) or not identifier_in(element.prev.code[0], self.expected_names):
            raise CodeGenerationError(element.code[0].range, "`%s` form must appear after %s." % (head_name, self.expected_names))

        if GC.domain == ExpressionDomain:
            return expr_wrap(ast.NameConstant(None), GC)
        else:
            return []