import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Node import Element

from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom


# def
# lambda
# call?
# return



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

                    with GC.let(domain=ExDom):
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

                with GC.let(domain=ExDom):
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
        #with GC.let(domain=ArgDom):
            # for a in acode[1]:
            #     # args_code should be a list of ast.arg objects!
            #     args_codes.append(GC.generate(a))




        arguments_code = ast.arguments(args_codes, )


        return ast.Lambda(arguments_code, expression_code)







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