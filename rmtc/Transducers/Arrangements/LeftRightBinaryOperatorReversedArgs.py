from rmtc.Syntax.Form import Form
from rmtc.Syntax.Util import is_identifier, identifier_in
from rmtc.Syntax.Node import Element
from rmtc.Transducers.ArrangementRule import ArrangementRule


class LeftRightBinaryOperatorReversedArgs(ArrangementRule):
    """
    ::

       a X ⋅ b  ⦅X b a⦆ ⋅
    """

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