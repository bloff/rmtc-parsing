from anoky.syntax.identifier import Identifier
from anoky.syntax.preseq import PreSeq
from anoky.syntax.form import Form
from anoky.syntax.preform import PreForm
from anoky.syntax.node import Element
from anoky.syntax.util import is_identifier
from anoky.syntax.token import is_token
import anoky.syntax.tokens as Tokens
from anoky.transducers.arrangement_rule import ArrangementRule


class MultipleAssignment(ArrangementRule):
    # TODO:
    #
    """
        ... := ⋅ ...: INDENT ... -> \(= ⟅...,⟆ ⟅...: INDENT ...⟆ \) ⋅

        ... := ⋅ ... INDENT ... -> \(= ⟅...,⟆ ⟅..., ARGBREAK, ...⟆ \) ⋅

        ... := ⋅ ... -> \(= ⟅...,⟆ ⟅...,⟆ \) ⋅

        ... := ⋅ -> \(= ⟅...,⟆\)⋅

    ``⟅,⟆`` denote PreTuples and ``⟅⟆`` denote PreForms.

    """

    def __init__(self):
        ArrangementRule.__init__(self, "Multiple Assignment")

    def applies(self, element:Element):
        return (is_identifier(element, ':=') or is_identifier(element, '=')) and \
               not element.is_first() and \
               ( isinstance(element.parent, PreForm) or isinstance(element.parent, PreSeq) )


    def apply(self, element):
        form = element.parent

        if is_identifier(element, '=') and \
                not ( form.first.next is element or
                      is_token(form.first.next, Tokens.PUNCTUATION, ',')):
                return


        form.wrap(form.first, element.prev, PreSeq)
        if element.next is not None:
            first_indent = element.next
            while first_indent is not None and not is_token(first_indent, Tokens.INDENT):
                first_indent = first_indent.next
            if first_indent is not None:
                if is_token(first_indent.prev, Tokens.PUNCTUATION, ':'):
                    form.wrap(element.next, form.last, PreForm)
                else:
                    form.replace(first_indent, Tokens.ARGBREAK())
                    form.wrap(element.next, form.last, PreSeq)
        form.remove(element)
        if isinstance(form, PreForm):
            form.prepend(Identifier("="))
        else:
            new_form = form.wrap(form.first, form.last, Form).code
            new_form.prepend(element)
        return None



