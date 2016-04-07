from anoky.Syntax.Form import Form



class PreForm(Form):
    """
    A node that represents a ``Form`` if it has two or more elements, and otherwise
    the single element within it.
    """
    def __init__(self, *children):
        Form.__init__(self, *children)