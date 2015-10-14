from Syntax.Node import Node


class Punctuator(Node):
    """
    A node that should contain a single element, usually itself a node,
    whose punctuation is yet unprocessed.

    :param child_node: The unprocessed child node.
    :param punctuation: A list of elements of the child node that are punctuation which should be processed.
    :param skip_count: The arrangement of punctuation of the child node should ignore these many elements; so,
       for instance, in lyc, the parsing of :literal:``head(a b, c d)`` creates a form with children ``head a b , c d``,
       and the ``,`` punctuation should group together ``a`` and ``b``, but not ``head``. So skip_count is 1.
       Also in lyc, the parsing of :literal:``head[a b, c d]`` creates a form with the children ``@[] head a b , c d``,
       and the ``,`` punctuation should not group together ``@[]`` or ``head``. So skip_count is 2.
    :param last_element: The last element to which punctuation applies. Usually the element immediately prior to indentation.
    """
    def __init__(self, child_node, punctuation, skip_count, last_element=None):
        Node.__init__(self, child_node)
        self.punctuation = punctuation
        self.skip_count = skip_count
        self.last_element = last_element

    def __str__(self):
        import Syntax.LispPrinter
        return Syntax.LispPrinter.lisp_printer(self)