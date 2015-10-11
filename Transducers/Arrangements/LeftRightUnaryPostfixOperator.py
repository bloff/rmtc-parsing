from Syntax.__exports__ import Form
from Syntax.Element import Element
from Syntax.Util import is_identifier, identifier_in
from Transducers.Arrangements.ArrangementRule import ArrangementRule

__author__ = 'bruno'


class LeftRightUnaryPostfixOperator(ArrangementRule):
    # e++ => (++ e)

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Unary Postfix Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            not element.is_first() and
            is_identifier(element.code) and
            identifier_in(element.code, self.sym_vals) and
            element.prev is not None
        )

    def apply(self, element):
        form = element.parent
        new_form_element = form.wrap(element.prev, element, Form)
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(element)
        return new_form_element.next


