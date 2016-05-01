from anoky.common.errors import CodeGenerationError
from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class NotInIsolation(SpecialForm):

    DOMAIN = [SDom, ExpressionDomain]


    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)
        head_name = element.code[0].code.name

        raise CodeGenerationError(element.code[0].range, "`%s` form cannot appear in isolation." % head_name)