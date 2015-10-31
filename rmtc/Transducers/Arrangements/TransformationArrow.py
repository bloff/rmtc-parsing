from rmtc.Syntax.PreTuple import PreTuple
from rmtc.Syntax.Form import Form
from rmtc.Syntax.PreForm import PreForm
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Util import is_identifier
from rmtc.Syntax.Token import is_token
import rmtc.Syntax.Tokens as Tokens
from rmtc.Transducers.ArrangementRule import ArrangementRule


class TransformationArrow(ArrangementRule):
    # FIXME: indents have disappeared by now
    """
    ::

          ⋅  INDENT   ⦅ ⟅⟆ ⟅⟆ ⦆ ⋅

          ⋅   ⦅ ⟅⟆ ⟅⟆⦆ ⋅

          ⋅     ⦅ ⟅⟆⦆ ⋅

    ``⟅⟆`` denote PreTuples.

    """

    def __init__(self, arrows):
        ArrangementRule.__init__(self, "Transformation Arrow")
        self.arrows = arrows

    def applies(self, element:Element):
        return is_identifier(element.code) and element.code.name in self.arrows and not element.is_first()

    def apply(self, element):
        form = element.parent
        form.wrap(form.first, element.prev, PreTuple)
        if element.next is not None:
            first_indent = element.next
            while first_indent is not None and not is_token(first_indent, Tokens.INDENT):
                first_indent = first_indent.next
            if first_indent is not None:
                new_form = form.wrap(element.next, first_indent, PreTuple).code
                new_form.remove(first_indent)
            else:
                form.wrap(element.next, form.last, PreTuple)
        form.remove(element)
        if isinstance(form, PreForm):
            form.prepend(element)
        else:
            new_form = form.wrap(form.first, form.last, Form).code
            new_form.replace(new_form.first, element)
        return None


