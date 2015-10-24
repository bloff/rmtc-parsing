from Syntax.__exports__ import Form, Identifier
from Syntax.Node import Element
from Syntax.Token import is_token
import Syntax.Tokens as Tokens
from Transducers.ArrangementRule import ArrangementRule


class RawComment(ArrangementRule):
    """
    Arrangement for comments without interpolated code. Does the transformation::

      BEGIN_MACRO("##")⋅  END_MACRO  ⋅

    (i.e., removes everything between ``BEGIN_MACRO`` and ``END_MACRO``).
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Raw Comment")

    def applies(self, element):
        return is_token(element, Tokens.BEGIN_MACRO, token_text="##")

    def apply(self, element) -> Element:
        parent = element.parent
        comment_form = parent.wrap(element, element.end)
        next = comment_form.next
        parent.remove(comment_form)
        return next


class Comment(ArrangementRule):
    """
    Arrangement for comments without interpolated code. Does the transformation::

      BEGIN_MACRO("#")⋅  END_MACRO  ⦅debug-values ⦆⋅

    where ```` removes all COMMENT tokens.
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Comment")

    def applies(self, element):
        return is_token(element, Tokens.BEGIN_MACRO, token_text="#")

    def apply(self, element) -> Element:
        assert is_token(element.next, Tokens.COMMENT)
        if element.next.next is element.end:
            parent = element.parent
            next_element = element.end.next
            parent.remove(element.next)
            parent.remove(element)
            parent.remove(element.end)
            return next_element
        else:
            parent = element.parent
            """:type : Node"""
            new_form_element = parent.wrap(element, element.end, Form)
            new_form = new_form_element.code
            new_form.prepend(Identifier("debug-values", element.range))
            # str BEGIN_MACRO('#') seq of STRING tokens, interspersed with Identifiers and BEGIN_MACRO / END_MACRO pairs END_MACRO

            new_form.remove(element) # remove BEGIN_MACRO('#')
            new_form.remove(element.end)  # remove END_MACRO

            elm = new_form[1] # first element
            while elm is not None:
                if is_token(elm, Tokens.BEGIN_MACRO):
                    elm = elm.end.next
                elif is_token(elm, Tokens.COMMENT):
                    nxt = elm.next
                    new_form.remove(elm)
                    elm = nxt
                else:
                    elm = elm.next

            return new_form_element.next
