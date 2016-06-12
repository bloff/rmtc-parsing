import ast

from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element
from anoky.syntax.util import is_form


class For(SpecialForm):

    HEADTEXT = "for"
    DOMAIN = SDom

    # (for (ids, iterable) statement+ (else ...)? )

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        target_iter_element = acode[1]
        target_element = target_iter_element.code[0]
        iter_element = target_iter_element.code[1]

        with GC.let(domain=ExpressionDomain):

            target_code = GC.generate(target_element)
            iter_code = GC.generate(iter_element)

        if is_form(acode.last, "else"):
            raise NotImplementedError()

        body_codes = []
        for e in acode[2:]:
            extend_body(body_codes, GC.generate(e))


        return ast.For(target=target_code,
                      iter=iter_code,
                      body=body_codes,
                      orelse=[],
                      )