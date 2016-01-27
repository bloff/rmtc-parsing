import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.Generator import Generator
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element


##=====================
def ctx_from_domain(GC:GenerationContext):
    if GC.domain == 'l':
        return ast.Store()
    elif GC.domain == 'd':
        return ast.Del()
    else:
        return ast.Load()
##=====================



class SpecialForm(Generator):

    pass





class BooleanBinaryOp(SpecialForm):

# #([and, or] expr0 expr1 additional_exprs+)

    HEADTEXT = ["and", "or"]

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code
        #assert isinstance(acode, Form)

        if acode[0].code.name == "and":
            op = ast.And()
        else:
            assert acode[0].code.name == "or"
            op = ast.Or()

        juncts_code = []
        with GC.let(domain='e'):
            for e in acode[1:]:
                juncts_code.append(GC.generate(e))

        return ast.BoolOp(op, juncts_code)




class Subscript(SpecialForm):

# #(@[] base_object id_or_seq)  ??
#

    HEADTEXT = "@[]"

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain='e'):
            base_object_code = GC.generate(acode[1])

        if isinstance(acode[2].code, Literal):

            if GC.domain == 'l':
                return ast.Subscript(base_object_code, ast.Index(GC.generate(acode[2])), ast.Store())

            # if GC.domain == 'd'
            # else

        #elif slice

        #else extslice




# https://greentreesnakes.readthedocs.org/en/latest/nodes.html#function-and-class-definitions


class Lambda(SpecialForm):

# #(lambda (arg,*) expression)

    HEADTEXT = "lambda"

    def generate(self, element:Element, GC:GenerationContext):

        assert GC.domain == 'e'

        acode = element.code
        #assert len(acode) == 3

        with GC.let(domain='e'):
            expression_code = GC.generate(acode[2])


        # INCOMPLETE:
        # vararg, kwarg, defaults, kw_defaults
        #
        # - This whole arg section might be way off-track
        # - since anything could be an argument, we might need to check
        #   when generating any expression if we actually need to return an ast.arg object
        #   ..or, could we convert everything (e.g. ast.Name, ast.BoolOp, anything)
        #   to an ast.arg after it's been generated

        args_codes = []
        with GC.domain == 'a':
            for a in acode[1]:
                # args_code should be a list of ast.arg objects!
                args_codes.append(GC.generate(a))




        arguments_code = ast.arguments(args_codes, )


        return ast.Lambda(arguments_code, expression_code)





class If(SpecialForm):

# #(if condition body_element+ (elif condition body_element+)* (else body_element+)?)))

    HEADTEXT = "if"

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        # "Check that form is as above"
        #assert

        with GC.let(domain='e'):
            condition_code = GC.generate(acode[1])


        # "make sure we have only 1 body_element in each of the bodies"
        #if GC.domain == 'e':


        body_code = []
        if GC.domain == 'e':
            body_code.append(GC.generate(acode[2]))
        else:
            #assert GC.domain == 's'
            nxtelm = acode[3]
            for nxtelm in acode.iterate_from(3):
                #if nxtelm.code ...
                    break


            while (not isinstance(nxtelm.code, Form)) or nxtelm.code[0].code.name not in ['elif','else']:
                # (nxtelm.code[0].code.name in ['elif', 'else'] if isinstance(nxtelm.code, Form) else True)
                body_code.append(GC.generate(nxtelm.code))
                nxtelm = nxtelm.next


        #else_code =

        if GC.domain == 'e':

            return #ast.IfExp(condition_code, body_code, else_code)

        else:

            #assert GC.domain == StatementDomain
            #assert GC.domain == StatementDomain()
            #assert isinstance(GC.domain, StatementDomain)
            assert GC.domain == 's'

            #return ast.If(condition_code, body_code, else_code)







class Attribute(SpecialForm):

# #(. base_object attribute_name)

    HEADTEXT = "."

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain='e'):
            base_object_code = GC.generate(acode[1])

        att_name = acode[2].code.name

        if GC.domain == 'l':
            return ast.Attribute(base_object_code, att_name, ast.Store())

        elif GC.domain == 'd':
            return ast.Attribute(base_object_code, att_name, ast.Del())

        else:
            return ast.Attribute(base_object_code, att_name, ast.Load())




class Return(SpecialForm):

# #(return expression?)

    HEADTEXT = "return"

    def generate(self, element:Element, GC:GenerationContext):

        assert GC.domain == 's'

        acode = element.code

        if len(acode) == 1:
            return ast.Return(None)

        else:
            assert len(acode) == 2

            with GC.let(domain='e'):
                expression_code = GC.generate(acode[1])

            return ast.Return(expression_code)



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
            with GC.let(domain='e'):
                exception_obj_code = GC.generate(acode[1])

            return ast.Raise(exception_obj_code)

        else:
            assert len(acode) == 1
            return ast.Raise(None)



class Pass(SpecialForm):

# #(pass)

    HEADTEXT = "pass"

    def generate(self):
        return ast.Pass()











default_special_forms_table = {
    "and" : BooleanBinaryOp(),
    "or" : BooleanBinaryOp(),
    "@[]" : Subscript(),
    "if" : If(),
    "." : Attribute(),
    "raise" : Raise(),
    "pass" : Pass()
}

default_special_forms_table["or"] = default_special_forms_table["and"]


# "+" :







