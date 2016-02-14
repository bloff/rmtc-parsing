import ast


from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Syntax.Node import Element

from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom






class Assign(SpecialForm):

# #(= target expr)
#
# #(= targets+ expr)
# #(= (targets,+) expr)

    HEADTEXT = "="
    LENGTH = 3
    DOMAIN = SDom

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















class AugAssign(SpecialForm):

# #(OP target expression)

    #OP = None

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        assert len(acode) == 3
        # target_element = acode[1]
        # augvalue_element = acode[2]

        with GC.let(domain=LVDom):
            # "target can be Name, Subscript or Attribute,
            #  but not a Tuple or List (unlike the targets of Assign)."

            target_code = GC.generate(acode[1])

        with GC.let(domain=ExDom):
            augvalue_code = GC.generate(acode[2])


        return ast.AugAssign(target_code, type(self).OP(), augvalue_code)





class AddAssign(AugAssign):

    HEADTEXT = "+="
    OP = ast.Add


class SubtractAssign(AugAssign):

    HEADTEXT = "-="
    OP = ast.Sub


class MultiplyAssign(AugAssign):

    HEADTEXT = "*="
    OP = ast.Mult


class DivideAssign(AugAssign):

    HEADTEXT = "/="
    OP = ast.Div


class IntDivideAssign(AugAssign):

    HEADTEXT = "//="
    OP = ast.FloorDiv


class ModuloAssign(AugAssign):

    HEADTEXT = "%="
    OP = ast.Mod


class PowAssign(AugAssign):

    HEADTEXT = "**="
    OP = ast.Pow


class MatMultAssign(AugAssign):

    HEADTEXT = "@="
    OP = ast.MatMult


class BitOrAssign(AugAssign):

    HEADTEXT = "|="
    OP = ast.BitOr


class BitXorAssign(AugAssign):

    HEADTEXT = "^="
    OP = ast.BitXor


class BitAndAssign(AugAssign):

    HEADTEXT = "&="
    OP = ast.BitAnd


class BitLShiftAssign(AugAssign):

    HEADTEXT = "<<="
    OP = ast.LShift


class BitRShiftAssign(AugAssign):

    HEADTEXT = ">>="
    OP = ast.RShift

