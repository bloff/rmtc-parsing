from anoky.Syntax.Form import Form
from anoky.Syntax.Identifier import Identifier
from anoky.Syntax.Node import Element
from anoky.Syntax.Util import is_identifier
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




