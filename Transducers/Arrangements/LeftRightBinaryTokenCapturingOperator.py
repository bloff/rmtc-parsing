from Common.Errors import ArrangementError
from Syntax.Util import is_identifier, identifier_in, is_literal
from Syntax.__exports__ import Form
from Syntax.Element import Element
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule

__author__ = 'bruno'


class LeftRightBinaryTokenCapturingOperator(ArrangementRule):
    # a . something => (. a something)
    # a .(...) => (. a (...))

    def __init__(self, token_vals):
        ArrangementRule.__init__(self, "Left-Right Binary Token-Capturing Operator")
        self.id_vals = token_vals

    def applies(self, element:Element):
        return (
            not element.is_last() and
            not element.is_first() and
            is_identifier(element) and
            identifier_in(element.code, self.id_vals)
        )

    def apply(self, element):
        form = element.parent
        next = element.next
        prev = element.prev
        if is_identifier(next) or is_literal(next):
            new_form_element = form.wrap(prev, next, Form)
        elif is_token(next, TOKEN.BEGIN_MACRO):
            new_form_element = form.wrap(prev, next.end, Form)
        else:
            raise ArrangementError(next.range.first_position, "Expected identifier, literal or begin-macro-token after '%s' token in position %s." %(element.value, element.range.first_position.nameless_str))
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(element)
        return new_form_element.next