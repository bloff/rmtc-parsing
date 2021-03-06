import ast

from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element
from anoky.syntax.util import is_form


class While(SpecialForm):

    HEADTEXT = "while"
    DOMAIN = SDom

    # (while testexpr body_statement+ (else ...)?)

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        testexpr_element = acode[1]

        with GC.let(domain=ExpressionDomain):

            testexpr_code = GC.generate(testexpr_element)

        if is_form(element.next, "else"):
            raise NotImplementedError()

        body_codes = []
        for e in acode[2:]:
            extend_body(body_codes, GC.generate(e))

        return ast.While(test=testexpr_code,
                         body=body_codes,
                         orelse=[])