from rmtc.Syntax.Form import Form
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Util import is_identifier, is_form
from rmtc.Transducers.ArrangementRule import ArrangementRule


class InfixIfElse(ArrangementRule):
    """
    Applies the transformation::

      a X b Y ⋅ c  ⦅X b a ⦅Y c⦆⦆ ⋅

    E.g. for X = if, Y = else::

      a if b else ⋅ c  ⦅if b a ⦅else c⦆⦆ ⋅
    """

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


class FormWithDirectives(ArrangementRule):
    # (if a b) . [(elif a b)]* [(else b)]? => (if a b (elif a b)* (else b)?)
    """
    Applies the transformation::

      ⦅head ⦆ ⋅ ⦅valid_continuation ⦆*  ⦅head  ⦅valid_continuation ⦆*⦆⋅

    (e.g. with head = `if` and valid_continuation one of `elif` or `else`, then it
        places the elifs and else forms inside the preceeding if form)
    """

    def __init__(self, head_name:str, following_names:set):
        ArrangementRule.__init__(self, head_name + '-'.join(following_names))
        self.head_name = head_name
        self.following_names = following_names

    def applies(self, element:Element):
        return isinstance(element.code, Form) and is_identifier(element.code.head, self.head_name)

    def apply(self, element:Element):
        form = element.parent
        next_form_element = element.next
        while next_form_element is not None:
            interesting_form = any( is_form(next_form_element, form_head) for form_head in self.following_names)
            if not interesting_form: break
            form.remove(next_form_element)
            element.code.append(next_form_element)
            next_form_element = element.next


        return element.next



