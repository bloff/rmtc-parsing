import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.Generator import Generator
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom

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

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()





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




class Subscript(SpecialForm):

# #(@[] base_object id_or_seq)  ??
#

    HEADTEXT = "@[]"

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain='e'):
            base_object_code = GC.generate(acode[1])

        if isinstance(acode[2].code, Literal):

            if GC.domain == LVDom:
                return ast.Subscript(base_object_code, ast.Index(GC.generate(acode[2])), ast.Store())

            # if GC.domain == DelDom
            # else

        #elif slice

        #else extslice





class Assign(SpecialForm):

# #(= target expr)
#
# #(= targets+ expr)
# #(= (targets,+) expr)

    HEADTEXT = "="

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        targets = acode[1]


        if not isinstance(targets, Seq):
            # targets is only one target

            with GC.set(domain=LVDom):
                target_code = GC.generate(targets)


        with GC.set(domain=ExDom):
            expr_code = GC.generate(acode.last)


        return ast.Assign(targets=[target_code], value=expr_code)




class AugAssign(SpecialForm):

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()


class AddAssign(AugAssign):

    HEADTEXT = "+="

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()


class SubtractAssign(AugAssign):

    HEADTEXT = "-="

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()

# class MultiplyAssign
# class DivideAssign
# class IntDivideAssign
# class ModuloAssign
# class MatMultAssign
# class BitOrAssign
# class BitXorAssign
# class BitAndAssign
# class BitLShiftAssign
# class BitRShiftAssign








class Def(SpecialForm):

# #(def (fname argform*) body_statement+)
# where each argform is one of
#   arg
#   (type, arg)
#   (= arg initializer)
#   (type, (= arg initializer))
#
#   (* arg)
#   (** arg)

    HEADTEXT = "def"

    def generate(self, element:Element, GC:GenerationContext):


        acode = element.code

        func_specs = acode[1]

        assert isinstance(func_specs[0], Identifier)

        function_name = func_specs[0].code.full_name

        arguments = self.generate_arguments(*func_specs[1:], GC=GC)



    def generate_arguments(self, *params, GC:GenerationContext):


        argslist = []
        kwonlyargslist = []
        vararg = None
        kwarg = None
        defaults = []
        kw_defaults = []

        for param_element in params:

            param_code = param_element.code

            if isinstance(param_code, Identifier):
                # arg

                arg_object = ast.arg(arg=param_code.code.full_name, annotation=None)

                if self.vararg is not None or self.kwarg is not None:
                    # argument is keyword-only

                    kwonlyargslist.append(arg_object)

                else:

                    argslist.append(arg_object)




            elif isinstance(param_code, Form):

                #assert isinstance(param_code[0].code, Identifier) and
                if param_code[0].code.full_name == '=':
                    # (= arg initializer)

                    assert len(param_code) == 3

                    with GC.set(domain=ExDom):
                        initializer_code = GC.generate(param_code[2])

                    assert isinstance(param_code[1].code, Identifier)



                elif param_code[0].code.full_name == '*':
                    # (* arg)

                    #assert isinstance(param_code[1].code, Identifier)

                    starg = ast.arg(arg=param_code[1].code.full_name, annotation=None)

                    assert self.vararg is None

                    self.vararg = starg



                elif param_code[0].code.full_name == '**':
                    # (** arg)

                    #assert isinstance(param_code[1].code, Identifier)

                    dblstarg = ast.arg(arg=param_code[1].code.full_name, annotation=None)

                    assert self.kwarg is None

                    self.kwarg = dblstarg






            else:
                # (type, arg)
                # (type, (= arg initializer))
                # (type, (* arg))
                # (type, (** arg))

                #assert isinstance(param_code, Seq)

                annotation_element = param_code[0]

                # if isinstance(annotation_code, Identifier):
                #     annotation = ast.Name(id=annotation_code.full_name, ctx=ast.Load())
                #
                # elif isinstance(annotation_code, Literal):
                #     annotation =

                with GC.set(domain=ExDom):
                    annotation_code = GC.generate(annotation_element)

                # and now the arg itself..






        return ast.arguments(argslist, vararg, kwonlyargslist, kwarg, defaults, kw_defaults)











class Lambda(SpecialForm):

# #(lambda (arg,*) expression)

    HEADTEXT = "lambda"

    def generate(self, element:Element, GC:GenerationContext):

        assert GC.domain == ExDom

        acode = element.code
        #assert len(acode) == 3

        with GC.let(domain=ExDom):
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




class Return(SpecialForm):

# #(return expression?)

    HEADTEXT = "return"

    def generate(self, element:Element, GC:GenerationContext):

        assert GC.domain == SDom

        acode = element.code

        if len(acode) == 1:
            return ast.Return(None)

        else:
            assert len(acode) == 2

            with GC.let(domain=ExDom):
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
            with GC.let(domain=ExDom):
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







