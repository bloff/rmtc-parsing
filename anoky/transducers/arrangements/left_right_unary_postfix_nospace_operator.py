from anoky.syntax.form import Form
from anoky.syntax.node import Element
from anoky.syntax.util import is_identifier, identifier_in
from anoky.transducers.arrangement_rule import ArrangementRule


class LeftRightUnaryPostfixNospaceOperator(ArrangementRule):
    """
    ::

       a X ⋅  ⦅«⋅X» a⦆ ⋅
    """

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Unary Postfix No-Space Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            not element.is_first() and
            is_identifier(element.code) and
            identifier_in(element.code, self.sym_vals) and
            element.prev is not None and
            element.prev.code is not None and
            element.prev.code.range.position_after.index == element.code.range.first_position.index
        )

    def apply(self, element):
        form = element.parent
        new_form_element = form.wrap(element.prev, element, Form)
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(element)
        return new_form_element.next


