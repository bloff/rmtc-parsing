from Common.Util import is_not_none
from Syntax.Util import identifier_in
from Syntax.__exports__ import Form, Identifier
from Syntax.Node import Element
from Transducers.ArrangementRule import ArrangementRule
from Syntax.Token import is_token, TOKEN



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
            is_token(element, TOKEN.CONSTITUENT) and
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


