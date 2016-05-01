import ast

from anoky.generation.domain import StatementDomain as SDom
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Pass(SpecialForm):

    HEADTEXT = "pass"
    LENGTH = 1
    DOMAIN = SDom

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        return ast.Pass()