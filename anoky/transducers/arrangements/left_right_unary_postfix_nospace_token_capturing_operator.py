from anoky.common.util import is_not_none
from anoky.syntax.util import identifier_in
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element
from anoky.transducers.arrangement_rule import ArrangementRule
from anoky.syntax.token import is_token
import anoky.syntax.tokens as Tokens


class LeftRightUnaryPostfixNospaceTokenCapturingOperator(ArrangementRule):
    """
    ::

       a X ⋅  ⦅X a⦆ ⋅

    when there is no whitespace between ``a`` and ``X``. ``a`` can be of the form ``BEGIN  END`` or
    ``BEGIN_MACRO  END_MACRO``, and it will be captured as a unit.
    """

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Unary Postfix No-Space Token-Capturing Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            not element.is_first() and
            is_token(element, Tokens.CONSTITUENT) and
            identifier_in(element.value, self.sym_vals) and
            is_not_none(element.prev, ".code.range.position_after.index", element, ".range.first_position.index") and
            element.prev.code.range.position_after.index == element.range.first_position.index
        )

    def apply(self, element):
        form = element.parent
        new_form_element = form.wrap(element.prev, element, Form)
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(Identifier(element.value, element.range))
        return new_form_element.next


