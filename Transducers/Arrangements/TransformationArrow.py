from Syntax.__exports__ import Form
from Syntax.PreForm import PreForm
from Syntax.Node import Element
from Syntax.Util import is_identifier
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule

# CONVERTS:
#     ... special_head ... INDENT ...
# INTO
#     special_head((...) (...) ...)
# AND:
#     ... special_head ...
# INTO
#     special_head((...) (...))
# AND:
#     ... special_head
# INTO
#     special_head((...))



class TransformationArrow(ArrangementRule):

    def __init__(self, arrows):
        ArrangementRule.__init__(self, "Transformation Arrow")
        self.arrows = arrows

    def applies(self, element:Element):
        return is_identifier(element.code) and element.code.name in self.arrows and not element.is_first()

    def apply(self, element):
        form = element.parent
        form.wrap(form.first, element.prev, PreForm)
        if element.next is not None:
            first_indent = element.next
            while first_indent is not None and not is_token(first_indent, TOKEN.INDENT):
                first_indent = first_indent.next
            if first_indent is not None:
                new_form = form.wrap(element.next, first_indent, PreForm).code
                new_form.remove(first_indent)
            else:
                form.wrap(element.next, form.last, PreForm)
        form.remove(element)
        if isinstance(form, PreForm):
            form.prepend(element)
        else:
            new_form = form.wrap(form.first, form.last, Form).code
            new_form.replace(new_form.first, element)
        return None



