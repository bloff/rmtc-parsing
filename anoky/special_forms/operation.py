import ast

from anoky.generation.domain import ExpressionDomain as ExDom
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import expr_wrap
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax.node import Element



# unary op
# binary op
# boolean op


class UnaryOp(SpecialForm):

    LENGTH = 2

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        operand_element = acode[1]

        with GC.let(domain=ExDom):
            operand_code = GC.generate(operand_element)

        return expr_wrap(ast.UnaryOp(self.OP(), operand_code), GC)


class UnaryAddOp(UnaryOp):

    HEADTEXT = "+"
    OP = ast.UAdd


class UnarySubOp(UnaryOp):

    HEADTEXT = "-"
    OP = ast.USub


class NotOp(UnaryOp):

    HEADTEXT = "not"
    OP = ast.Not


class InvertOp(UnaryOp):

    HEADTEXT = "~"
    OP = ast.Invert






class BinaryOp(SpecialForm):

    LENGTH = 3

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        left_element, right_element = acode[1], acode[2]

        with GC.let(domain=ExDom):
            left_code = GC.generate(left_element)
            right_code = GC.generate(right_element)

        return expr_wrap(ast.BinOp(left_code, self.OP(), right_code), GC)


class AddOp(BinaryOp):

    HEADTEXT = "+"
    OP = ast.Add


class SubOp(BinaryOp):

    HEADTEXT = "-"
    OP = ast.Sub


class MultOp(BinaryOp):

    HEADTEXT = "*"
    OP = ast.Mult


class DivOp(BinaryOp):

    HEADTEXT = "/"
    OP = ast.Div


class FloorDivOp(BinaryOp):

    HEADTEXT = "//"
    OP = ast.FloorDiv


class ModOp(BinaryOp):

    HEADTEXT = "%"
    OP = ast.Mod


class PowOp(BinaryOp):

    HEADTEXT = "**"
    OP = ast.Pow


class LShiftOp(BinaryOp):

    HEADTEXT = "<<"
    OP = ast.LShift


class RShiftOp(BinaryOp):

    HEADTEXT = ">>"
    OP = ast.RShift


class BitOrOp(BinaryOp):

    HEADTEXT = "|"
    OP = ast.BitOr


class BitXorOp(BinaryOp):

    HEADTEXT = "^"
    OP = ast.BitXor


class BitAndOp(BinaryOp):

    HEADTEXT = "&"
    OP = ast.BitAnd


class MatMultOp(BinaryOp):

    HEADTEXT = "@"
    OP = ast.MatMult







class BooleanBinaryOp(SpecialForm):

# #([and, or] expr0 expr1 additional_exprs+)



    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code
        #assert isinstance(acode, Form)

        # if acode[0].code.full_name == "and":
        #     op = ast.And()
        # else:
        #     assert acode[0].code.full_name == "or"
        #     op = ast.Or()

        juncts_code = []

        with GC.let(domain=ExDom):
            for e in acode[1:]:
                juncts_code.append(GC.generate(e))

        return expr_wrap(ast.BoolOp(self.OP(), juncts_code), GC)

        # code = ast.BoolOp(self.OP(), juncts_code)

        # if GC.domain == SDom:
        #     return ast.Expr(code)
        # return code



class AndOp(BooleanBinaryOp):

    HEADTEXT = "and"
    OP = ast.And


class OrOp(BooleanBinaryOp):

    HEADTEXT = "or"
    OP = ast.Or






