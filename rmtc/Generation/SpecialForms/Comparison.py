import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Syntax.Node import Element


class Comparison(SpecialForm):

#
# class Compare(left, ops, comparators)
# "left is the first value in the comparison,
#  ops the list of operators, and comparators
#  the list of values after the first."

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        left_element = acode[1]

        #with



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








