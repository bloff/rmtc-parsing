from anoky.Syntax.Seq import Seq



class PreSeq(Seq):
    """
    A node that represents a ``Tuple`` if it has two or more elements, and otherwise
    the single element within it.
    """
    def __init__(self, *children):
        Seq.__init__(self, *children)