from Streams.StreamRange import StreamRange
from Syntax.Code import Code
from Syntax.Node import Node

__author__ = 'bruno'


class Element(object):

    @staticmethod
    def make(code_or_element, parent=None):
        if isinstance(code_or_element, Code):
            return Element(code_or_element, parent)
        else:
            assert isinstance(code_or_element, Element)
            if code_or_element.parent is None:
                code_or_element.parent = parent
                return code_or_element
            else:
                return Element(code_or_element, parent)

    # If value_or_element is not an Element, then value_or_element is the value of the new element
    # If value_or_element is an Element, then value_or_element's value is the value of the new element
    def __init__(self, code_or_element, parent=None):
        assert parent is None or isinstance(parent, Node)
        self.parent = parent
        """:type : Node"""
        self.prev = None
        """:type : Element"""
        self.next = None
        """:type : Element"""
        self.code = None
        """:type : Code"""
        self.expansion = None
        """:type : Element"""

        if code_or_element is None or isinstance(code_or_element, Code):
            self.code = code_or_element
        else:
            assert isinstance(code_or_element, Element)
            self.code = code_or_element.code

    def is_last(self):
        return self.next is None

    def is_first(self):
        return self.prev is None

    @property
    def number(self) -> int:
        node = self
        i = 0
        while not node.is_first():
            i += 1
            node = node.prev
        return i

    @property
    def range(self) -> StreamRange:
        assert self.code is not None
        return self.code.range

    def __str__(self):
        if self.code is not None:
            return "Element(%s)" % str(self.code)
        else:
            return "Element()"