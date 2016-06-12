import ast

from anoky.common.errors import CodeGenerationError
from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax.lisp_printer import succinct_lisp_printer
from anoky.syntax.node import Element




# if / elif / else
# while (/ else)
# for / in
# break
# continue
# try / except / finally
# with
#
# raise
# assert
# pass
from anoky.syntax.util import is_form


class If(SpecialForm):

    HEADTEXT = "if"
    DOMAIN = [SDom, ExDom]

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        # "Check that form is as above"
        #assert


        if GC.domain == ExDom:
            astIf = ast.IfExp
            if len(acode) > 3 and not (is_form(acode[3], 'elif') or is_form(acode[3], 'else')):
                raise CodeGenerationError(acode.range, "If expression must only have a single sub-expression (for now).")
        else:
            astIf = ast.If



        def gen_elif_elses(elif_else_elm):
            my_code = elif_else_elm.code
            if is_form(elif_else_elm, 'elif'):
                with GC.let(domain=ExDom):
                    my_condition_gen = GC.generate(my_code[1])

                my_body_gens = []
                for body_elm in my_code.iterate_from(2):
                    extend_body(my_body_gens, GC.generate(body_elm))

                if elif_else_elm.next is None:
                    return [astIf(my_condition_gen, my_body_gens, [])]
                else:
                    else_code = gen_elif_elses(elif_else_elm.next)
                    return [astIf(my_condition_gen, my_body_gens, else_code)]
            elif is_form(elif_else_elm, 'else'):
                my_body_gens = []
                for body_elm in my_code.iterate_from(1):
                    extend_body(my_body_gens, GC.generate(body_elm))
                return my_body_gens
            else:
                raise CodeGenerationError(elif_else_elm.range,
                                          "Unexpected element `%s` after first `elif` or `else` form within `if` form." % (
                                          succinct_lisp_printer(elif_else_elm)))

        with GC.let(domain=ExDom):
            condition_gen = GC.generate(acode[1])
        body_gens = []
        else_code = []

        for body_elm in acode.iterate_from(2):
            if is_form(body_elm, 'elif') or is_form(body_elm, 'else'):
                else_code = gen_elif_elses(body_elm)
                break
            else:
                body_gen = GC.generate(body_elm)
                extend_body(body_gens, body_gen)

        if len(body_gens) == 0: body_gens.append(ast.Pass())


        if GC.domain == ExDom:
            return ast.IfExp(condition_gen, body_gens[0], else_code[0] if len(else_code) > 0 else ast.NameConstant(None))
        else:
            return ast.If(condition_gen, body_gens, else_code)





