from rmtc.Syntax.Node import Node


class Form(Node):
    """
    A node whose first element is singled out (and called *head*). It usually
    represents the application of the first element (presumably a function, a
    macro, etc) to the remaining elements.
    """
    def __init__(self, *children):
        Node.__init__(self, *children)

    @property
    def head(self):
        """
        The first element of the form.
        """
        return self.first

    @head.setter
    def head(self, new_head):
        raise NotImplementedError()

    def __str__(self):
        import rmtc.Syntax.LispPrinter as LispPrinter
        return LispPrinter.lisp_printer(self)


    def copy(self):
        return Form(*[i.code.copy() for i in self])
