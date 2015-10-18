from Syntax.Tuple import Tuple



class PreTuple(Tuple):
    """
    A node that represents a ``Tuple`` if it has two or more elements, and otherwise
    the single element within it.
    """
    def __init__(self, *children):
        Tuple.__init__(self, *children)