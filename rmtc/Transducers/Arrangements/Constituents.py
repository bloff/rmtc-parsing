from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Token import is_token
import rmtc.Syntax.Tokens as Tokens
from rmtc.Transducers.ArrangementRule import ArrangementRule

# from Semantics.Types.Bootstrap0 import Float, Int

class Constituent(ArrangementRule):
    """
    Replaces CONSTITUENT tokens with Identifiers or (int or float) Literals.
    """
    def __init__(self, int_literal_type = "INT (PLACEHOLDER TYPE)", float_literal_type = "FLOAT (PLACEHOLDER TYPE)"):
        ArrangementRule.__init__(self, "Constituent")
        self.int_literal_type = int_literal_type
        self.float_literal_type = float_literal_type

    def applies(self, element):
        return is_token(element, Tokens.CONSTITUENT) and element.code is None

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
            new_element = element.parent.replace(element, Literal(self.int_literal_type, int(element.value), element.range))
        elif Constituent.is_float(element.value):
            new_element = element.parent.replace(element, Literal(self.float_literal_type, float(element.value), element.range))
        else:
            new_element = element.parent.replace(element, Identifier(element.value, element.range))
            # if element.value in self.stalling_identifiers:
            #     return element

        return new_element.next