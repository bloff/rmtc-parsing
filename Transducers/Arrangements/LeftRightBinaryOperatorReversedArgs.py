from Syntax.Util import identifier_in
from Syntax.__exports__ import is_identifier, Form
from Syntax.Node import Element
from Transducers.Arrangements.ArrangementRule import ArrangementRule

__author__ = 'bruno'


class LeftRightBinaryOperatorReversedArgs(ArrangementRule):
    # a for. b => (for b a).

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Binary Operator Reversed Args")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            is_identifier(element.code) and
            identifier_in(element.code, self.sym_vals) and
            not element.is_first() and
            not element.is_last()
        )


    def apply(self, element:Element):
        form = element.parent
        p = element.prev
        n = element.next
        form.remove(p)
        form.remove(n)
        new_form = Form(element, n, p)
        return form.replace(element, new_form).next