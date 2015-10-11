from .Node import Node


class Form(Node):
    def __init__(self, *children):
        Node.__init__(self, *children)
        # self.preform = False
        # self.defaults_to_apply_form = False
        # self.children_default_to_tuple_form = True

    @property
    def head(self):
        return self.first

    @head.setter
    def head(self, new_head):
        raise NotImplementedError()

    @staticmethod
    def copy(code):
        return Form([child for child in code.iterate_from(0)])

    def __str__(self):
        import Syntax.LispPrinter
        return Syntax.LispPrinter.lisp_printer(self)


