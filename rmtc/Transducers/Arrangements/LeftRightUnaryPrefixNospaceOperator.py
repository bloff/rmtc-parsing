from rmtc.Common.Errors import ArrangementError
from rmtc.Common.Util import is_not_none
from rmtc.Syntax.Util import  is_identifier, is_literal
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Token import is_token
from rmtc.Syntax.Tokens import BEGIN_MACRO
from rmtc.Transducers.ArrangementRule import ArrangementRule


class LeftRightUnaryPrefixNospaceOperator(ArrangementRule):
    """
    ::

       X ⋅ b  ⦅X b⦆ ⋅
    """

    def __init__(self, token_vals):
        ArrangementRule.__init__(self, "Left-Right Unary Prefix No-Space Token-Capturing Operator")
        self.token_vals = token_vals

    def applies(self, element:Element):
        next = element.next
        return (
            not element.is_last() and
            is_identifier(element) and
            element.code.name in self.token_vals and
            is_not_none(element, ".range.position_after.index", next, ".range.first_position.index") and
            element.code.range.position_after.index == next.code.range.first_position.index and
            not isinstance(element.parent, Form)
        )

    def apply(self, element):
        form = element.parent
        next = element.next
        if is_identifier(next) or is_literal(next):
            new_form_element = form.wrap(element, next, Form)
        elif is_token(next, BEGIN_MACRO):
            new_form_element = form.wrap(element, next.end, Form)
        else:
            raise ArrangementError(next.range.first_position, "Expected identifier, literal or begin-macro-token after '%s' identifier in position %s." %(element.value, element.range.first_position.nameless_str))
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(Identifier(element.code.full_name, element.range))
        #new_form.prepend(Identifier(element.value, element.range))
        return new_form_element.next



