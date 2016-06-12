import ast

from anoky.common.errors import CodeGenerationError
from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element
from anoky.syntax.util import is_form, is_identifier


class Try(SpecialForm):

    HEADTEXT = "try"
    DOMAIN = [SDom]

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        # "Check that form is as above"
        #assert





        def gen_except_handler(except_elm):
            my_code = except_elm.code
            exception_elm = my_code[1]
            name = None
            if is_form(exception_elm, 'as'):
                with GC.let(domain=ExpressionDomain):
                    my_exception_type = GC.generate(exception_elm.code[1])
                my_exception_name_id = exception_elm.code[2]
                if not is_identifier(my_exception_name_id):
                    raise CodeGenerationError(my_exception_name_id.range, "Expected an identifier as exception name of `except` clause in `try` special-form.")
                name = my_exception_name_id.code.name
            else:
                with GC.let(domain=ExpressionDomain):
                    my_exception_type = GC.generate(exception_elm)

            body_gens = []
            for my_body_elm in my_code.iterate_from(2):
                extend_body(body_gens, GC.generate(my_body_elm))

            return ast.ExceptHandler(my_exception_type, name, body_gens)





        body_gens, handlers, or_else, finally_body = [], [], None, None
        stage = 0 # 0 = body, 1 = except, 2 = else, 3 = finally
        names = {1: "except", 2: "else", 3: "finally"}
        for body_elm in acode.iterate_from(1):
            if is_form(body_elm, 'except'):
                if stage > 1: raise CodeGenerationError(body_elm.range, "Found `except` clause after first `%s` in `try` special form." % names[stage])
                else: stage = 1
                except_handler = gen_except_handler(body_elm)
                handlers.append(except_handler)
            elif is_form(body_elm, 'else'):
                if stage > 1: raise CodeGenerationError(body_elm.range, "Found `except` clause after first `%s` in `try` special form." % names[stage])
                else: stage = 2
                or_else = [GC.generate(my_body_elm) for my_body_elm in body_elm.code.iterate_from(1)]
            elif is_form(body_elm, 'finally'):
                if stage > 2: raise CodeGenerationError(body_elm.range, "Found `except` clause after first `%s` in `try` special form." % names[stage])
                else: stage = 3
                finally_body = []
                for my_body_elm in body_elm.code.iterate_from(1):
                    extend_body(finally_body, GC.generate(my_body_elm))
            else:
                if stage > 0: raise CodeGenerationError(body_elm.range, "Found body clause after first `%s` in `try` special form." % names[stage])
                body_gen = GC.generate(body_elm)
                extend_body(body_gens, body_gen)


        return ast.Try(body_gens, handlers, or_else, finally_body)