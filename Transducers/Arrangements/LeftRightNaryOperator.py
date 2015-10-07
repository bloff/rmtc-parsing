from Syntax.__exports__ import Element, Form
from Syntax.Util import is_identifier, identifier_in
from Transducers.Arrangements.ArrangementRule import ArrangementRule

__author__ = 'bruno'


class LeftRightNaryOperator(ArrangementRule):

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right N-Ary Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        #  p [ + ] n
        return (is_identifier(element.code) and
                identifier_in(element.code, self.sym_vals) and
                not element.is_first() and
                not element.is_last())

    def apply(self, element):
        # p + n
        # + p n
        # (+ p n)
        form = element.parent
        head = element.code
        p = element.prev
        n = element.next
        form.remove(p) # + n
        form.remove(n) # +
        new_form = Form(head, p, n) # +      (+ p n)
        new_form_element = form.replace(element, new_form) # (+ p n)

        while True: # while we find + e
            e1 = new_form_element.next
            if e1 is None: break
            e2 = e1.next
            if e2 is None: break
            if is_identifier(e1.code, head.name): # if e1 is the same symbol as e, then it is the same operator
                form.remove(e1)
                form.remove(e2)
                new_form.append(e2) # so we add the next element as an operand
            else: break

        return new_form_element.next