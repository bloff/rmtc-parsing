import ast

from anoky.generation.domain import ExpressionDomain, StatementDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import expr_wrap
from anoky.special_forms import SpecialForm
from anoky.syntax.node import Element


class Compare(SpecialForm):


    HEADTEXT = "compare"
    DOMAIN = [StatementDomain, ExpressionDomain]
    OPERAND_DICT = {"==": ast.Eq,
                    "!=": ast.NotEq,
                    "<=": ast.LtE,
                    ">=": ast.GtE,
                    "<": ast.Lt,
                    ">": ast.Gt}

    def generate(self, element:Element, GC:GenerationContext):

        self.precheck(element, GC)

        acode = element.code

        operands_seq = acode.last.code

        first_operand = operands_seq[0]

        with GC.let(domain = ExpressionDomain):
            first_operand_gen = GC.generate(first_operand)

            ops = [self.OPERAND_DICT[e.code.name]() for e in acode[1:-1]]
            comparators = [GC.generate(operand) for operand in operands_seq.iterate_from(1)]

        return expr_wrap(
            ast.Compare(
                left = first_operand_gen,
                ops = ops,
                comparators = comparators
            ), GC)








# cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn







# Since Comparisons aren't just binary the following classes might
#  not be a good idea
#
# class EqComparison(Comparison):
#
#     HEADTEXT = "=="
#     OP = ast.Eq
#
#
# class NotEqComparison(Comparison):
#
#     HEADTEXT = "!="
#     OP = ast.NotEq
#
#
# class LessComparison(Comparison):
#
#     HEADTEXT = "<"
#     OP = ast.Lt








