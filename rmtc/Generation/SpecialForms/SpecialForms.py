import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.Generator import Generator
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom

#from rmtc.Generation.SpecialForms.AugAssign import *


from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element


##=====================
from rmtc.Syntax.Seq import Seq


def ctx_from_domain(GC:GenerationContext):
    if GC.domain == LVDom:
        return ast.Store()
    elif GC.domain == DelDom:
        return ast.Del()
    else:
        return ast.Load()
##=====================



class SpecialForm(Generator):

    HEADTEXT = None
    LENGTH = None

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()

    def precheck(self, element:Element, GC:GenerationContext):
        acode = element.code
        # assert isinstance(acode[0], Identifier) ?
        if self.HEADTEXT:
            assert self.HEADTEXT == acode[0].code.full_name
        if self.LENGTH:
            if isinstance(self.LENGTH, int):
                # if a number
                assert self.LENGTH == len(acode)
            else:
                # if range or list
                assert len(acode) in self.LENGTH





class BooleanBinaryOp(SpecialForm):

# #([and, or] expr0 expr1 additional_exprs+)

    HEADTEXT = ["and", "or"]

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code
        #assert isinstance(acode, Form)

        if acode[0].code.full_name == "and":
            op = ast.And()
        else:
            assert acode[0].code.full_name == "or"
            op = ast.Or()

        juncts_code = []
        with GC.let(domain='e'):
            for e in acode[1:]:
                juncts_code.append(GC.generate(e))

        return ast.BoolOp(op, juncts_code)








class Assign(SpecialForm):

# #(= target expr)
#
# #(= targets+ expr)
# #(= (targets,+) expr)

    HEADTEXT = "="
    LENGTH = 3

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        targets_element = acode[1]
        value_element = acode.last


        # if not isinstance(targets, Seq):
        #     # targets is only one target
        #
        #     with GC.let(domain=LVDom):
        #         target_code = GC.generate(targets)

        with GC.let(domain=LVDom):
            targets_code = GC.generate(targets_element)

        with GC.let(domain=ExDom):
            value_code = GC.generate(value_element)


        return ast.Assign(targets=[targets_code], value=value_code)










class If(SpecialForm):

# #(if condition body_element+ (elif condition body_element+)* (else body_element+)?)))

    HEADTEXT = "if"

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


            while (not isinstance(nxtelm.code, Form)) or nxtelm.code[0].code.full_name not in ['elif','else']:
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







class Attribute(SpecialForm):

# #(. base_object attribute_name)

    HEADTEXT = "."
    LENGTH = 3

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain=ExDom):
            base_object_code = GC.generate(acode[1])

        att_name = acode[2].code.full_name

        if GC.domain == LVDom:
            return ast.Attribute(base_object_code, att_name, ast.Store())

        elif GC.domain == DelDom:
            return ast.Attribute(base_object_code, att_name, ast.Del())

        else:
            return ast.Attribute(base_object_code, att_name, ast.Load())








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



# class Pass(SpecialForm):
#
# # #(pass)
#
#     HEADTEXT = "pass"
#
#     def generate(self):
#         return ast.Pass()









