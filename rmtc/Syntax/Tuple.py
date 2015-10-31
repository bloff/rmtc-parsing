from rmtc.Syntax.Node import Node


class Tuple(Node):
    """
    A node that usually represents the ordered arrangement of its elements into a
    single entity.
    """
    def __init__(self, *children):
        Node.__init__(self, *children)

    def __str__(self):
        return rmtc.Syntax.LispPrinter.lisp_printer(self)
