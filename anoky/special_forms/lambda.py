import ast

from anoky.generation.domain import ExpressionDomain as ExDom
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


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