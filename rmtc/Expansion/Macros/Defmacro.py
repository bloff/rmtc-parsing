import ast

from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Macro import Macro
from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Syntax.Node import Element


class DefMacro(Macro, SpecialForm):

    HEADTEXT = "defmacro"

    def expand(self, element:Element, context:ExpansionContext):

        raise NotImplementedError()



    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()






class DefIdMacro(Macro, SpecialForm):

    HEADTEXT = "defidmacro"

    def expand(self, element:Element, context:ExpansionContext):




        raise NotImplementedError()



    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()

