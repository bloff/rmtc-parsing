from anoky.common.errors import CodeGenerationError
from anoky.expansion.expander import Expander
from anoky.expansion.expansion_context import ExpansionContext
from anoky.generation.generation_context import GenerationContext
from anoky.generation.generator import Generator

#from anoky.special_forms.AugAssign import *

from anoky.syntax.node import Element


class SpecialForm(Expander, Generator):

    HEADTEXT = None
    LENGTH = None
    DOMAIN = None

    def expand(self, element: Element, EC: ExpansionContext):
        for item in element.code:
            EC.expand(item)

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()

    def precheck(self, element:Element, GC:GenerationContext):
        acode = element.code
        # assert isinstance(acode[0], Identifier) ?
        if self.LENGTH:
            if isinstance(self.LENGTH, int):
                # if a number
                if self.LENGTH != len(acode):
                    raise CodeGenerationError(element.range, "Special form `%s` expected %d arguments, got %d."%(self.HEADTEXT, self.LENGTH, len(acode)))
            else:
                # if range or list
                if len(acode) not in self.LENGTH:
                    valid_numbers = ", ".join(self.LENGTH[:-1]) + " or " + self.LENGTH[-1]
                    raise CodeGenerationError(element.range, "Special form `%s` expected %d arguments, got %d."%(self.HEADTEXT, valid_numbers, len(acode)))
        if self.DOMAIN:
            if isinstance(self.DOMAIN, str):
                if self.DOMAIN != GC.domain:
                    raise CodeGenerationError(element.range, "Special form `%s` appeared in domain '%s', but can only appear in domain '%s'."%(self.HEADTEXT, GC.domain, self.DOMAIN))
            else:
                # if list or set
                if GC.domain not in self.DOMAIN:
                    valid_domains = "'"+ "', '".join(self.LENGTH[:-1]) + " or '" + self.LENGTH[-1] + "'"
                    raise CodeGenerationError(element.range, "Special form `%s` appeared in domain '%s', but can only appear in domains ."%(self.HEADTEXT, GC.domain, valid_domains))









