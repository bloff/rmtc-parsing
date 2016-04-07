from anoky.syntax.node import Node, ElementOperation


class Seq(Node):
    """
    A node that usually represents the ordered arrangement of its elements into a
    single entity.
    """
    def __init__(self, *children, new_element=ElementOperation.make_new):
        Node.__init__(self, *children, new_element=new_element)

    def __str__(self):
        from anoky.syntax.lisp_printer import lisp_printer
        return lisp_printer(self)

    def copy(self):
        return Seq(*[i.code.copy() for i in self])