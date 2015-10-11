from Syntax.__exports__ import Literal, Identifier
from Syntax.Element import Element
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule
# from Semantics.Types.Bootstrap0 import Float, Int

class Constituent(ArrangementRule):
    def __init__(self):
        ArrangementRule.__init__(self, "Constituent")
        # self.stalling_identifiers = stalling_identifiers if stalling_identifiers is not None else {}

    def applies(self, element):
        return is_token(element, TOKEN.CONSTITUENT) and element.code is None

    @staticmethod
    def is_float(string:str):
        try:
            float(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_int(string:str):
        try:
            int(string)
            return True
        except ValueError:
            return False


    def apply(self, element) -> Element:
        if Constituent.is_int(element.value):
            new_element = element.parent.replace(element, Literal("INT(PLACEHOLDER)", int(element.value), element.range))
        elif Constituent.is_float(element.value):
            new_element = element.parent.replace(element, Literal("FLOAT(PLACEHOLDER)", float(element.value), element.range))
        else:
            new_element = element.parent.replace(element, Identifier(element.value, element.range))
            # if element.value in self.stalling_identifiers:
            #     return element

        return new_element.next