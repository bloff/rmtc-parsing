
import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom

from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Node import Element




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
from rmtc.Syntax.Util import is_form


class If(SpecialForm):

# #(if condition body_element+ (elif condition body_element+)* (else body_element+)?)))

    HEADTEXT = "if"
    DOMAIN = SDom

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        # "Check that form is as above"
        #assert

        with GC.let(domain=ExDom):
            condition_code = GC.generate(acode[1])


        # "make sure we have only 1 body_element in each of the bodies"
        #if GC.domain == ExDom:


        body_code = []
        if GC.domain == ExDom:
            body_code.append(GC.generate(acode[2]))
        else:
            #assert GC.domain == SDom
            nxtelm = acode[3]
            for nxtelm in acode.iterate_from(3):
                #if nxtelm.code ...
                    break


            while (not isinstance(nxtelm.code, Form)) \
                            or nxtelm.code[0].code.full_name not in ['elif','else']:
                # (nxtelm.code[0].code.full_name in ['elif', 'else'] if isinstance(nxtelm.code, Form) else True)
                body_code.append(GC.generate(nxtelm.code))
                nxtelm = nxtelm.next


        #else_code =

        if GC.domain == ExDom:

            return #ast.IfExp(condition_code, body_code, else_code)

        else:

            #assert GC.domain == StatementDomain
            #assert GC.domain == StatementDomain()
            #assert isinstance(GC.domain, StatementDomain)
            assert GC.domain == SDom

            #return ast.If(condition_code, body_code, else_code)




class While(SpecialForm):

    HEADTEXT = "while"
    DOMAIN = SDom

    # (while testexpr body_statement+ (else ...)?)

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()

        # acode = element.code
        #
        # testexpr_element = acode[1]
        #
        # with GC.let(domain=ExDom):
        #
        #     testexpr_code = GC.generate(testexpr_element)
        #
        #
        #
        # body_items




class For(SpecialForm):

    HEADTEXT = "for"
    DOMAIN = SDom

    # (for (ids, iterable) statement+ (else ...)? )

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()

        #acode = element.code





        #return ast.For(target=
        #               iter=
        #               body=
        #               orelse=
        #               )




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

            return ast.Raise(exception_obj_code)

        else:
            assert len(acode) == 1
            return ast.Raise(None)


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

















