from anoky.syntax.node import Node, ElementOperation


class Form(Node):
    """
    A node whose first element is singled out (and called *head*). It usually
    represents the application of the first element (presumably a function, a
    macro, etc) to the remaining elements.
    """
    def __init__(self, *children, new_element=ElementOperation.make_new):
        Node.__init__(self, *children, new_element=new_element)

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
        import anoky.syntax.lisp_printer as LispPrinter
        return LispPrinter.lisp_printer(self)


    def copy(self):
        return Form(*[i.code.copy() for i in self])
