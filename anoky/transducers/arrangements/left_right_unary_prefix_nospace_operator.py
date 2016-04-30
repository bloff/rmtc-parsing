from anoky.common.errors import ArrangementError
from anoky.common.util import is_not_none
from anoky.syntax.util import  is_identifier, is_literal, is_form
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element
from anoky.syntax.token import is_token
from anoky.syntax.tokens import BEGIN_MACRO
from anoky.transducers.arrangement_rule import ArrangementRule


class LeftRightUnaryPrefixNospaceOperator(ArrangementRule):
    """
    ::

       X ⋅ b  ⦅X b⦆ ⋅
    """

    def __init__(self, token_vals):
        ArrangementRule.__init__(self, "Left-Right Unary Prefix No-Space Operator")
        self.token_vals = token_vals

    def applies(self, element:Element):
        next = element.next
        return (
            next is not None and
            (not (element.is_first() and is_form(element.parent)) or not next.is_last()) and
            is_identifier(element) and
            element.code.name in self.token_vals and
            is_not_none(element, ".range.position_after.index", next, ".range.first_position.index") and
            element.code.range.position_after.index == next.code.range.first_position.index
        )

    def apply(self, element):
        form = element.parent
        next = element.next
        new_form_element = form.wrap(element, next, Form)
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(Identifier(element.code.full_name, element.range))
        #new_form.prepend(Identifier(element.value, element.range))
        return new_form_element.next



