from anoky.Syntax.Form import Form
from anoky.Syntax.Identifier import Identifier
from anoky.Syntax.Node import Element
from anoky.Syntax.Seq import Seq
from anoky.Syntax.Util import is_identifier, identifier_in, is_form
from anoky.transducers.arrangement_rule import ArrangementRule


class LeftRightNaryOperatorMultipleHeads(ArrangementRule):
    """
    ::

       a X1 ⋅ b1 X2 b2 X3 ... Xn bn  ⦅head_symbol (X1, X2, ..., Xn) (a, b1, b2, ... ,bn⦆ ⋅
    """
    def __init__(self, head_symbol_name, sym_vals):
        ArrangementRule.__init__(self, "Left-Right N-Ary Multi-Operator")
        self.head_symbol_name = head_symbol_name
        self.sym_vals = sym_vals

    def applies(self, element:Element):
        #  p [ + ] n
        return (is_identifier(element.code) and
                identifier_in(element.code, self.sym_vals) and
                not element.is_first() and
                not element.is_last() and
                not is_form(element.parent, self.head_symbol_name))

    def apply(self, element):
        # p < n
        form = element.parent
        ops = [element]
        p = element.prev
        n = element.next
        args = [p, n]
        form.remove(p) # < n
        form.remove(n) # <
        new_form = Form(Identifier(self.head_symbol_name))
        new_form_element = form.replace(element, new_form) # (head_symbol)

        while True: # while we find + e
            e1 = new_form_element.next
            if e1 is None: break
            e2 = e1.next
            if e2 is None: break
            if is_identifier(e1.code) and e1.code.name in self.sym_vals: # if e1 is the same symbol as e, then it is the same operator
                form.remove(e1)
                form.remove(e2)
                ops.append(e1)
                args.append(e2)
            else: break

        for op in ops:
            new_form.append(op)

        new_form.append(Seq(*args))

        return new_form_element.next