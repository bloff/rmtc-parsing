from anoky.Syntax.Node import Node


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
    :param end_punctuation_marker: An element marking the position after the last element in the child_node to which
    punctuation applies. Usually the INDENT token of an indented code block.
    """

    def __init__(self, child_node, punctuation, skip_count, end_punctuation_marker=None):
        Node.__init__(self, child_node)
        self.punctuation = punctuation
        self.skip_count = skip_count
        self.end_punctuation_marker = end_punctuation_marker

    def __str__(self):
        from anoky.Syntax.LispPrinter import lisp_printer
        return lisp_printer(self)