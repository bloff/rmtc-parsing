from .Node import Node


class Tuple(Node):
    def __init__(self, *children):
        Node.__init__(self, *children)

    def __str__(self):
        import Syntax.LispPrinter
        return Syntax.LispPrinter.lisp_printer(self)
