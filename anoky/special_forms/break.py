import ast

from anoky.generation.domain import StatementDomain as SDom
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Break(SpecialForm):

    HEADTEXT = "break"
    LENGTH = 1
    DOMAIN = SDom

    # (break)

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        return ast.Break()