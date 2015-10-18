from Syntax.__exports__ import Form, Identifier
from Syntax.Node import Element
from Syntax.Util import is_identifier
from Transducers.ArrangementRule import ArrangementRule

# a not in b => (not-in a b)
# TODO: replace with
# a not in b => (not (in a b))
class LeftRightBinaryOperatorTwoSymbols(ArrangementRule):

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Binary Operator - Two Symbols")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        prev = element.prev
        return (
            is_identifier(element.code) and
            prev is not None and
            is_identifier(prev.code) and
            (prev.code.name, element.code.name) in self.sym_vals and # FIXME
            not prev.is_first() and
            not element.is_last()
        )

    def apply(self, element):
        form = element.parent
        p = element.prev
        pp = p.prev
        n = element.next
        form.remove(p)
        form.remove(pp)
        form.remove(n)
        head = Identifier(p.code.name + "-" + element.code.name)
        head.range.update(p.code.range)
        head.range.update(element.code.range)
        new_form = Form(head, pp, n)
        new_form_element = form.replace(element, new_form)

        return new_form_element.next




