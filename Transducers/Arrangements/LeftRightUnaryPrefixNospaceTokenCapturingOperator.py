from Common.Errors import ArrangementError
from Common.Util import is_not_none
from Syntax.Util import is_identifier, is_literal, identifier_in
from Syntax.__exports__ import Form
from Syntax.Element import Element
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule

__author__ = 'bruno'


class LeftRightUnaryPrefixNospaceTokenCapturingOperator(ArrangementRule):
    # $something => ($ something)
    # $(...) => ($ (...))

    def __init__(self, token_vals):
        ArrangementRule.__init__(self, "Left-Right Unary Prefix No-Space Token-Capturing Operator")
        self.sym_vals = token_vals

    def applies(self, element:Element):
        def _is_identifier_or_literal_immediately_after(next, element):
            return ((is_identifier(next) or is_literal(next)) and
                is_not_none(next, ".code.range.first_position.index") and
                element.code.range.position_after.index == next.code.range.first_position.index)

        def _is_begin_macro_token_immediately_after(next, element):
            return (is_token(next, TOKEN.BEGIN_MACRO) and
                is_not_none(next, ".range.first_position.index") and
                element.code.range.position_after.index == next.range.first_position.index)

        next = element.next
        return (
            next is not None and
            (not element.is_first() or not next.is_last()) and
            is_identifier(element) and
            identifier_in(element.code, self.sym_vals) and
            is_not_none(element, ".code.range.position_after.index") and
            (_is_identifier_or_literal_immediately_after(next, element) or
             _is_begin_macro_token_immediately_after(next, element))
        )

    def apply(self, element):
        form = element.parent
        next = element.next
        if is_identifier(next) or is_literal(next):
            new_form_element = form.wrap(element, next, Form)
        elif is_token(next, TOKEN.BEGIN_MACRO):
            new_form_element = form.wrap(element, next.end, Form)
        else:
            raise ArrangementError(next.range.first_position, "Expected identifier, literal or begin-macro-token after '%s' identifier in position %s." %(element.value, element.range.first_position.nameless_str))
        new_form = new_form_element.code
        new_form.remove(element)
        new_form.prepend(element)
        return new_form_element.next



