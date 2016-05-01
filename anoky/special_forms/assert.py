import ast

from anoky.generation.domain import ExpressionDomain as ExDom
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Assert(SpecialForm):

    HEADTEXT = "assert"

    # (assert test)
    # (assert test msg)

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        test_element = acode[1]

        with GC.let(domain=ExDom):

            test_code = GC.generate(test_element)

            msg_code = None
            if len(acode) > 2:
                msg_element = acode[2]
                msg_code = GC.generate(msg_element)


        return ast.Assert(test=test_code, msg=msg_code)