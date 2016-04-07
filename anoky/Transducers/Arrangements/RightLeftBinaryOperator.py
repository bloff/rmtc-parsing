from anoky.Syntax.Form import Form
from anoky.Syntax.Node import Element
from anoky.Syntax.Util import is_identifier, identifier_in
from anoky.Transducers.ArrangementRule import ArrangementRule


class RightLeftBinaryOperator(ArrangementRule):
    """
    ::

       ⋅ ⦅X a b⦆  a ⋅ X b
    """
    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Left-Right Binary Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            is_identifier(element.code) and
            identifier_in(element.code, self.sym_vals) and
            not element.is_first() and
            not element.is_last()
        )

    def apply(self, element):
        form = element.parent
        p = element.prev
        n = element.next
        form.remove(p)
        form.remove(n)
        new_form = Form(element.code, p, n)
        new_form_element = form.replace(element, new_form)

        return new_form_element.prev