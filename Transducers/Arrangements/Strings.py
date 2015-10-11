from Syntax.__exports__ import Form, Identifier, Literal
from Syntax.Element import Element
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule
# from Semantics.Types.Bootstrap0 import String

class Strings(ArrangementRule):
    def __init__(self):
        ArrangementRule.__init__(self, "Strings")

    def applies(self, element):
        return is_token(element, TOKEN.BEGIN_MACRO, token_text="“")

    def apply(self, element) -> Element:
        assert is_token(element.next, TOKEN.STRING)
        if element.next.next is element.end:
            parent = element.parent
            string_token = element.next
            parent.remove(element)
            parent.remove(element.end)
            string_token.code = Literal("STRING(PLACEHOLDER)", string_token.value, string_token.range)
            return string_token.next
        else:
            new_form_element = element.parent.wrap(element, element.end, Form)
            new_form = new_form_element.code
            new_form.prepend(Identifier("str", element.range))
            # str BEGIN_MACRO('“') seq of STRING tokens, interspersed with Identifiers and BEGIN_MACRO / END_MACRO pairs END_MACRO

            new_form.remove(element) # remove BEGIN_MACRO('“')
            new_form.remove(element.end)  # remove END_MACRO

            elm = new_form[1] # first element
            while elm is not None:
                if is_token(elm, TOKEN.STRING):
                    elm.code = Literal(String, elm.value, elm.range)
                if is_token(elm, TOKEN.BEGIN_MACRO):
                    elm = elm.end.next
                else:
                    elm = elm.next



            return new_form_element.next
