from Syntax.Form import Form

__author__ = 'bruno'


class PreForm(Form):
    """
    A node that represents a ``Form`` if it has two or more elements, and otherwise
    the single element within it.
    """
    def __init__(self, *children):
        Form.__init__(self, *children)
        self.prepend_head = None