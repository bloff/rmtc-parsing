from Syntax.__exports__ import Form
from Syntax.Element import Element
from Syntax.Util import is_identifier, identifier_in
from Transducers.Arrangements.ArrangementRule import ArrangementRule

__author__ = 'bruno'


class RightLeftUnaryPrefixNospaceOperator(ArrangementRule):
    # !e => (! e)
    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Right-Left Unary Prefix No-Space Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            (not isinstance(element.parent, Form) or not element.is_first()) and
            is_identifier(element.code) and
            identifier_in(element.code, self.sym_vals) and
            element.next is not None and
            element.next.code is not None and
            element.code.range.position_after.index == element.next.code.range.first_position.index
        )

    def apply(self, element):
        form = element.parent
        new_form_element = form.wrap(element, element.next, Form)
        return new_form_element.prev


