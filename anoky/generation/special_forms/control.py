
import ast

from anoky.common.errors import CodeGenerationError
from anoky.generation.generation_context import GenerationContext
from anoky.generation.special_forms.special_forms import SpecialForm
from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom

from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
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
from anoky.syntax.util import is_form, is_identifier


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

                my_body_gens = [GC.generate(body_elm) for body_elm in my_code.iterate_from(2)]

                if elif_else_elm.next is None:
                    return [astIf(my_condition_gen, my_body_gens, [])]
                else:
                    else_code = gen_elif_elses(elif_else_elm.next)
                    return [astIf(my_condition_gen, my_body_gens, else_code)]
            elif is_form(elif_else_elm, 'else'):
                return [GC.generate(body_elm) for body_elm in my_code.iterate_from(1)]
            else:
                raise CodeGenerationError(elif_else_elm.range, "Unexpected element `%s` after first `elif` or `else` form within `if` form." % (succinct_lisp_printer(elif_else_elm)))




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
                body_gens.append(body_gen)

        if len(body_gens) == 0: body_gens.append(ast.Pass())

        if GC.domain == ExDom:
            return ast.IfExp(condition_gen, body_gens[0], else_code[0] if len(else_code) > 0 else ast.NameConstant(None))
        else:
            return ast.If(condition_gen, body_gens, else_code)




class While(SpecialForm):

    HEADTEXT = "while"
    DOMAIN = SDom

    # (while testexpr body_statement+ (else ...)?)

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        testexpr_element = acode[1]

        with GC.let(domain=ExDom):

            testexpr_code = GC.generate(testexpr_element)

        if is_form(acode.last, "else"):
            raise NotImplementedError()

        body_codes = [GC.generate(e) for e in acode[2:]]

        return ast.While(test=testexpr_code,
                         body=body_codes,
                         orelse=[])




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

        with GC.let(domain=ExDom):

            target_code = GC.generate(target_element)
            iter_code = GC.generate(iter_element)

        if is_form(acode.last, "else"):
            raise NotImplementedError()

        body_codes = [GC.generate(e) for e in acode[2:]]


        return ast.For(target=target_code,
                      iter=iter_code,
                      body=body_codes,
                      orelse=[],
                      )




class Break(SpecialForm):

    HEADTEXT = "break"
    LENGTH = 1
    DOMAIN = SDom

    # (break)

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        return ast.Break()


class Continue(SpecialForm):

    HEADTEXT = "continue"
    LENGTH = 1
    DOMAIN = SDom

    # (continue)

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        return ast.Continue()





class Raise(SpecialForm):

# #(raise exception?)
#
# not implemented yet:
# "raise ex_obj from cause"?  ==>  ast.Raise(ex_obj, cause)

    HEADTEXT = "raise"

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code
        #assert isinstance(acode, Form)

        if len(acode) > 1:
            with GC.let(domain=ExDom):
                exception_obj_code = GC.generate(acode[1])

            return ast.Raise(exception_obj_code, None) # Fix none to allow raise x from y syntax

        else:
            assert len(acode) == 1
            return ast.Raise()


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



class Pass(SpecialForm):

    HEADTEXT = "pass"
    LENGTH = 1
    DOMAIN = SDom

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        return ast.Pass()





class With(SpecialForm):

    HEADTEXT = "with"
    DOMAIN = SDom

    # (with ((f) (as x y)) body+

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        context_element = acode[1]
        context_element_code = context_element.code
        assert len(context_element_code) > 0

        with_items = []

        with GC.let(domain=ExDom):

            for ctxel in context_element_code:


                if is_form(ctxel.code, "as"):

                    ctxelcode = ctxel.code

                    assert len(ctxel) == 3
                    ctx_expr = GC.generate(ctxelcode[1])

                    opt_var = GC.generate(ctxelcode[2])

                    with_items.append(ast.withitem(context_expr=ctx_expr,
                                                   optional_vars=opt_var))

                else:

                    ctx_expr = GC.generate(ctxel)

                    with_items.append(ast.withitem(context_expr=ctx_expr,
                                                   optional_vars=None))

            body_items = []

            with GC.let(domain=SDom):

                for bodyel in acode[2:]:

                    body_items.append(GC.generate(bodyel))


        return ast.With(items=with_items,
                        body=body_items)





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
                with GC.let(domain=ExDom):
                    my_exception_type = GC.generate(exception_elm.code[1])
                my_exception_name_id = exception_elm.code[2]
                if not is_identifier(my_exception_name_id):
                    raise CodeGenerationError(my_exception_name_id.range, "Expected an identifier as exception name of `except` clause in `try` special-form.")
                name = my_exception_name_id.code.name
            else:
                with GC.let(domain=ExDom):
                    my_exception_type = GC.generate(exception_elm)

            body_gens = [GC.generate(my_body_elm) for my_body_elm in my_code.iterate_from(2)]

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
                finally_body = [GC.generate(my_body_elm) for my_body_elm in body_elm.code.iterate_from(1)]
            else:
                if stage > 0: raise CodeGenerationError(body_elm.range, "Found body clause after first `%s` in `try` special form." % names[stage])
                body_gen = GC.generate(body_elm)
                body_gens.append(body_gen)


        return ast.Try(body_gens, handlers, or_else, finally_body)



class NotInIsolation(SpecialForm):

    DOMAIN = [SDom, ExDom]


    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)
        head_name = element.code[0].code.name

        raise CodeGenerationError(element.code[0].range, "`%s` form cannot appear in isolation." % head_name)
