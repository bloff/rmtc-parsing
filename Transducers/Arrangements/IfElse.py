from Syntax.__exports__ import Form
from Syntax.Node import Element
from Syntax.Util import is_identifier
from Transducers.ArrangementRule import ArrangementRule



class InfixIfElse(ArrangementRule):
    # if set has key-value pair ('x', 'y'),
    # then convert:
    # a x b y . c => (x b a (y c)) .
    # e.g. for x = if, y = else
    # a if b else c => (if b a (else c))

    def __init__(self, set_vals):
        ArrangementRule.__init__(self, "Infix If-Else")
        self.set = set_vals

    def applies(self, y:Element):
        c = y.next if y is not None else None
        b = y.prev if y is not None else None
        x = b.prev if b is not None else None
        a = x.prev if x is not None else None
        return (
            x is not None and
            is_identifier(y.code) and
            is_identifier(x.code) and
            a is not None and
            b is not None and
            c is not None and
            (x.code.name, y.code.name) in self.set
        )

    def apply(self, y):
        form = y.parent
        c = y.next
        b = y.prev
        x = b.prev
        a = x.prev

        form.remove(a)
        form.remove(b)
        form.remove(y)
        form.remove(c)
        new_form = Form(x, b, a, Form(y, c))

        return form.replace(x, new_form).next


class IfElifElse(ArrangementRule):
    # (if a b) . [(elif a b)]* [(else b)]? => (if a b (elif a b)* (else b)?)
    def __init__(self):
        ArrangementRule.__init__(self, "If-Elif-Else")

    def applies(self, element:Element):
        return isinstance(element.code, Form) and is_identifier(element.code.head, 'if')

    def apply(self, element:Element):
        form = element.parent
        next_form_element = element.next
        while next_form_element is not None and isinstance(next_form_element.code, Form) and is_identifier(next_form_element.code.head, 'elif'):
            form.remove(next_form_element)
            element.code.append(next_form_element)
            next_form_element = element.next

        if next_form_element is not None and isinstance(next_form_element.code, Form) and is_identifier(next_form_element.code.head, 'else'):
            form.remove(next_form_element)
            element.code.append(next_form_element)

        return element.next



