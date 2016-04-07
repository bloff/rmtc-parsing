from anoky.Syntax.Form import Form
from anoky.Syntax.Node import Element
from anoky.Syntax.Util import is_identifier, identifier_in, is_head
from anoky.transducers.arrangement_rule import ArrangementRule


class RightLeftUnaryPrefixOperator(ArrangementRule):
    """
    ::

       ⋅ ⦅X a⦆  ⋅ X a

    there can be space between ``X`` and ``a``.
    """
    def __init__(self, sym_vals):
        ArrangementRule.__init__(self, "Right-Left Unary Prefix Operator")
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        return (
            is_identifier(element.code) and
            identifier_in(element.code, self.sym_vals) and
            not is_head(element) and
            not element.is_last()
        )

    def apply(self, element):
        prev = element.prev
        form = element.parent
        form.wrap(element, element.next, Form)
        # new_form = new_form_element.code
        # new_form.remove(element)
        # new_form.head = element.code
        return prev


