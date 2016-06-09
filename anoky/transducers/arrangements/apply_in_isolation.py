from anoky.syntax.form import Form
from anoky.syntax.node import Element
from anoky.syntax.preform import PreForm
from anoky.syntax.util import is_identifier
from anoky.transducers.arrangement_rule import ArrangementRule


def is_forced_head(element):
    if not element.is_first(): return False
    parent = element.parent
    if isinstance(parent, PreForm):
        return len(element.parent) > 1
    elif isinstance(parent, Form):
        return True
    else:
        return False


class ApplyInIsolation(ArrangementRule):
    """
    ::

       name ⋅    ⦅name ⦆ ⋅
       name ⋅   ⦅name⦆ ⋅

    Used, for example, to convert ``return`` into ``return()``.
    """

    def __init__(self, names):
        ArrangementRule.__init__(self, "Apply in Isolation")
        self.names = names

    def applies(self, element:Element):
        return (is_identifier(element.code) and
                element.code.name in self.names and
                not is_forced_head(element))

    def apply(self, element):
        form = element.parent
        new_form = form.wrap(element, element, Form).code
        head = new_form.first.code
        new_form.remove(new_form.first)
        new_form.prepend(head)
        return None




