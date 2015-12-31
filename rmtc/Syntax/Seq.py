from rmtc.Syntax.Node import Node


class Seq(Node):
    """
    A node that usually represents the ordered arrangement of its elements into a
    single entity.
    """
    def __init__(self, *children):
        Node.__init__(self, *children)

    def __str__(self):
        from rmtc.Syntax.LispPrinter import lisp_printer
        return lisp_printer(self)
