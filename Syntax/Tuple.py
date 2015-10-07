from .Node import Node, Element
from Syntax import Code


class Tuple(Node):
    def __init__(self, *children):
        Node.__init__(self, *children)
        # self.preform = False
        # self.defaults_to_apply_form = False
        # self.children_default_to_tuple_form = True

    def __str__(self):
        import Syntax.LispPrinter
        return Syntax.LispPrinter.lisp_printer(self)

    # @head.setter
    # def head(self, new_head):
    #     if self.first is not None:
    #         if isinstance(new_head, Element):
    #             self._head = new_head.code
    #         else:
    #             self._head = new_head
    #     if self._head is not None:
    #         assert isinstance(self._head, Code)
    #         self.range.update(self._head.range)


class PreTuple(Tuple):
    def __init__(self, *children):
        Tuple.__init__(self, *children)


