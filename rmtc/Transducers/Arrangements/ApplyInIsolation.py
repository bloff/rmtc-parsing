from rmtc.Syntax.Form import Form
from rmtc.Syntax.Node import Element
from rmtc.Syntax.PreForm import PreForm
from rmtc.Syntax.Util import is_identifier
from rmtc.Transducers.ArrangementRule import ArrangementRule


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
                not element.is_first())

    def apply(self, element):
        form = element.parent
        new_form = form.wrap(element, element, Form).code
        head = new_form.first.code
        new_form.remove(new_form.first)
        new_form.prepend(head)
        return None



