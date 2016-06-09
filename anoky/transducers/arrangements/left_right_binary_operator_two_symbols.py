from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element
from anoky.syntax.util import is_identifier
from anoky.transducers.arrangement_rule import ArrangementRule


class LeftRightBinaryOperatorTwoSymbols(ArrangementRule):
    """
    ::

       a X Y ⋅ b  ⦅X-Y a b⦆ ⋅

    E.g. for X = is, Y = not::

       a is not ⋅ b  ⦅is-not a b⦆ ⋅

    """

    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Binary Operator - Two Symbols")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        next = element.next
        return (
            is_identifier(element.code) and
            next is not None and
            is_identifier(next.code) and
            (element.code.name, next.code.name) in self.sym_vals and # FIXME
            not element.is_first() and
            not next.is_last()
        )

    def apply(self, element):
        form = element.parent
        p = element.prev
        n = element.next
        nn = n.next
        form.remove(p)
        form.remove(n)
        form.remove(nn)
        head = Identifier(element.code.name + n.code.name)
        head.range.update(element.code.range)
        head.range.update(n.code.range)
        new_form = Form(head, p, nn)
        new_form_element = form.replace(element, new_form)

        return new_form_element.next




