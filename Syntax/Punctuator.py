from Syntax.Node import Node


class Punctuator(Node):
    def __init__(self, node, punctuation, skip_count, last_element=None):
        Node.__init__(self, node)
        self.punctuation = punctuation
        self.skip_count = skip_count
        self.last_element = last_element

    def __str__(self):
        import Syntax.LispPrinter
        return Syntax.LispPrinter.lisp_printer(self)