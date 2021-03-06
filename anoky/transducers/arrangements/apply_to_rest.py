from anoky.syntax.form import Form
from anoky.syntax.node import Element
from anoky.syntax.preform import PreForm
from anoky.syntax.util import is_identifier
from anoky.transducers.arrangement_rule import ArrangementRule


class ApplyToRest(ArrangementRule):
    """
    ::

       name ⋅    ⦅name ⦆ ⋅
       name ⋅   ⦅name⦆ ⋅

    Used, for example, to convert ``return`` into ``return()``.
    """

    def __init__(self, names):
        ArrangementRule.__init__(self, "Apply to Rest")
        self.names = names

    def applies(self, element:Element):
        return (is_identifier(element.code) and
                element.code.name in self.names and
                (element.parent.__class__ is not Form or not element.is_first() or len(element.parent) > 2))

    def apply(self, element):
        form = element.parent
        if element.parent.__class__ is not Form or not element.is_first():
                if not element.is_last():
                    new_form = form.wrap(element.next, form.last, Form).code
                    form.remove(element)
                    new_form.prepend(element.code)
                else:
                    new_form = form.wrap(element, element, Form).code
                    head = new_form.first.code
                    new_form.remove(new_form.first)
                    new_form.prepend(head)
        elif element.parent.__class__ is Form and len(element.parent) > 2:
            form.wrap(element.next, form.last, PreForm).code

        return None




