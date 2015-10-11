from Syntax.__exports__ import Form
from Syntax.Element import Element
from Syntax.Util import is_identifier
from Transducers.Arrangements.ArrangementRule import ArrangementRule

# converts
# ... return ...
# to
# ... (return (...))
# and
# ... return
# to
# ... return()
# ! NO-BREAK e => (! e)
# e +. e => +(e e).



class ApplyToRest(ArrangementRule):

    def __init__(self, names):
        ArrangementRule.__init__(self, "Apply to Rest")
        self.names = names

    def applies(self, element:Element):
        return (is_identifier(element.code) and
                element.code.name in self.names and
                (not isinstance(element.parent, Form) or not element.is_first()))

    def apply(self, element):
        form = element.parent
        if not element.is_last():
            new_form = form.wrap(element.next, form.last, Form).code
            form.remove(element)
            new_form.prepend(element.code)
        else:
            new_form = form.wrap(element, element, Form).code
            head = new_form.first.code
            new_form.remove(new_form.first)
            new_form.prepend(head)
        return None




