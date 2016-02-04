import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom

from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element




# list, tuple?, dict
# comprehensions
# subscription
#
# del












class Subscript(SpecialForm):

# #(@[] base_object id_or_seq)  ??
#

    HEADTEXT = "@[]"

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain=ExDom):
            base_object_code = GC.generate(acode[1])

        if isinstance(acode[2].code, Literal):

            if GC.domain == LVDom:
                return ast.Subscript(base_object_code, ast.Index(GC.generate(acode[2])), ast.Store())

            # if GC.domain == DelDom
            # else

        #elif slice

        #else extslice






class Delete(SpecialForm):

    HEADTEXT = "del"
    DOMAIN = SDom

    # (del (seq, to, delete))

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()