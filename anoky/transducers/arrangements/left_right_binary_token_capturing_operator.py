from anoky.common.errors import ArrangementError
from anoky.Syntax.Util import is_identifier, identifier_in, is_literal, is_form
from anoky.Syntax.Form import Form
from anoky.Syntax.Node import Element
from anoky.Syntax.Token import is_token
import anoky.Syntax.Tokens as Tokens
from anoky.transducers.arrangement_rule import ArrangementRule


class LeftRightBinaryTokenCapturingOperator(ArrangementRule):
    """
    ::

       a X ⋅ b  ⦅X a b⦆ ⋅

    ``b`` can be of the form ``BEGIN  END`` or ``BEGIN_MACRO  END_MACRO``, and it will be captured as a unit.
    """

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
        next = element.next # this is 'b'
        prev = element.prev # this is 'a'
        if is_identifier(next) or is_literal(next) or is_form(next):
            new_form_element = form.wrap(prev, next, Form)
        elif is_token(next, Tokens.BEGIN_MACRO):
            # a . BEGIN_MACRO something END_MACRO dont want => (. a BEGIN_MACRO) something END_MACRO
            # actually want
            # a . BEGIN_MACRO something END_MACRO => (. a BEGIN_MACRO something END_MACRO)
            new_form_element = form.wrap(prev, next.end, Form)
        else:
            raise ArrangementError(element.range.position_after, "Expected identifier, literal, form or begin-macro-token after '%s' in position %s." %(element.code.name, element.range.first_position.nameless_str))
        new_form = new_form_element.code
        # at this point new_form = ⦅a X b⦆
        new_form.remove(element)
        # at this point new_form = ⦅a b⦆
        new_form.prepend(element)
        # at this point new_form = ⦅X a b⦆
        return new_form_element.next # return the next position to be read