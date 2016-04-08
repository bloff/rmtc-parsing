from rmtc.Syntax.PreSeq import PreSeq
from rmtc.Syntax.Form import Form
from rmtc.Syntax.PreForm import PreForm
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Util import is_identifier
from rmtc.Syntax.Token import is_token
import rmtc.Syntax.Tokens as Tokens
from rmtc.Transducers.ArrangementRule import ArrangementRule


class MultipleAssignment(ArrangementRule):
    """
    ::

         := ⋅  INDENT   ⦅:= ⟅⟆ ⟅ ARGBREAK ⟆⦆ ⋅

         := ⋅   ⦅:= ⟅⟆ ⟅⟆⦆ ⋅

         := ⋅     ⦅:= ⟅⟆⦆ ⋅

    ``⟅⟆`` denote PreTuples.

    """

    def __init__(self, arrows):
        ArrangementRule.__init__(self, "Multiple Assignment")
        self.symbols = arrows

    def applies(self, element:Element):
        return is_identifier(element.code) and \
               element.code.name in self.symbols and \
               not element.is_first() and \
               ( isinstance(element.parent, PreForm) or isinstance(element.parent, PreSeq) )


    def apply(self, element):
        form = element.parent
        form.wrap(form.first, element.prev, PreSeq)
        if element.next is not None:
            first_indent = element.next
            while first_indent is not None and not is_token(first_indent, Tokens.INDENT):
                first_indent = first_indent.next
            if first_indent is not None:
                form.replace(first_indent, Tokens.ARGBREAK())
            form.wrap(element.next, form.last, PreSeq)
        form.remove(element)
        if isinstance(form, PreForm):
            form.prepend(element)
        else:
            new_form = form.wrap(form.first, form.last, Form).code
            new_form.prepend(element)
        return None



