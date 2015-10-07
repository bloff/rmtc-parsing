from Streams.StreamRange import StreamRange
from .Code import *


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

class NodeIterator(object):
    def __init__(self, first_element:Element):
        self.current = first_element
        self.next = first_element.next if first_element is not None else None
        self.i = -1

    def __next__(self) -> Element:
        if self.current is None:
            raise StopIteration()

        ret = self.current
        self.current = self.next
        if self.next is not None:
            self.next = self.next.next

        self.i += 1

        return ret

    def __iter__(self):
        return self

class Node (Code):

    # Given a list of elements and/or Code instances, or a sequence of elements and/or Code instances as arguments
    # creates a node whose elements have the given code instances, and the code instances of the given elements;
    # e.g., Node(1, 2, elm) has elements: Element.make(1), Element.make(2), Element.make(elm.value)
    def __init__(self, *children):
        super(Node, self).__init__()
        if len(children) == 1 and isinstance(children[0], list):
            children = children[0]

        # first element of node
        self.first = None
        # last element of node
        self.last = None

        self.range = StreamRange()

        if len(children) > 0:
            assert isinstance(children[0], Code) or isinstance(children[0], Element)
            current = self.first = Element.make(children[0], self)
            self.range.update(current.code.range)
            for child in children[1:]:
                assert isinstance(child, Code) or isinstance(child, Element)
                current.next = Element.make(child, self)
                current.next.prev = current
                current = current.next
                self.range.update(current.code.range)
            self.last = current

    def erase(self):
        for node in self:
            node.parent = node.next = node.prev = None
        self.first = self.last = None

    def prepend(self, child):
        assert isinstance(child, Code) or isinstance(child, Element)
        element = Element.make(child, self)
        self.range.update(element.code.range)
        if self.first is None:
            self.first = self.last = element
        else:
            self.first.prev = element
            element.next = self.first
            self.first = element

    def append(self, child):
        assert isinstance(child, Code) or isinstance(child, Element)
        element = Element.make(child, self)
        self.range.update(element.code.range)
        if self.first is None:
            self.first = self.last = element
        else:
            self.last.next = element
            element.prev = self.last
            self.last = element

    def insert(self, after_this:Element, child):
        assert isinstance(after_this, Element) or (after_this is None and self.first is None)
        assert isinstance(child, Code) or isinstance(child, Element)
        if after_this is None and self.first is None:
            self.append(child)
        else:
            assert after_this.parent is self
            element = Element.make(child, self)
            self.range.update(element.code.range)
            element.next = after_this.next
            element.prev = after_this
            if after_this.next is not None:
                after_this.next.prev = element
            else: self.last = element
            after_this.next = element

    def remove(self, element):
        assert isinstance(element, Element)
        assert element.parent is self

        if element.prev is None: self.first = element.next
        else: element.prev.next = element.next
         # if node is the tail
        if element.next is None: self.last = element.prev
        else: element.next.prev = element.prev
        element.parent = element.next = element.prev = None

    def replace(self, element, new_child):
        assert isinstance(element, Element)
        assert element.parent is self
        assert isinstance(new_child, Code) or isinstance(new_child, Element)
        new_element = Element.make(new_child, self)
        self.range.update(new_element.code.range)
        new_element.next = element.next
        new_element.prev = element.prev
        # if c is the head
        if element.prev is None: self.first = new_element
        else: element.prev.next = new_element
         # if c is the tail
        if element.next is None: self.last = new_element
        else: element.next.prev = new_element
        element.parent = element.next = element.prev = None
        return new_element

    # def expand(self, element, code):
    #     assert isinstance(element, Element)
    #     assert element.parent is self
    #     assert isinstance(code, Code)
    #     new_element = Element.make(code, self)
    #     new_element.next = element.next
    #     new_element.prev = element.prev
    #     assert element.expansion is None
    #     element.expansion = new_element

    # # replaces node in self with the elements of form
    # # so (a b c).replace_explode(b, (d e)) = (a d e c)
    # def replace_explode(self, element, node_or_list):
    #     assert isinstance(node_or_list, Node) or isinstance(node_or_list, list)
    #     assert isinstance(element, Element)
    #     element_to_insert_after = element
    #     if isinstance(node_or_list, Node):
    #         element_to_add = node_or_list.first
    #         while element_to_add is not None:
    #             self.insert(element_to_insert_after, element_to_add)
    #             element_to_insert_after = element_to_insert_after.next
    #             element_to_add = element_to_add.next
    #     else:
    #         assert isinstance(node_or_list, list)
    #         for i in range(len(node_or_list)):
    #             self.insert(element_to_insert_after, node_or_list[i])
    #             element_to_insert_after = element_to_insert_after.next
    #     self.remove(element)

    # replaces node in self with the elements of given Node
    # Destroys the given Node in the process
    # so (a b c).replace_explode(b, (d e)) = (a d e c), and the (d e) node becomes ()
    def replace_explode_modify(self, element, node):
        assert isinstance(node, Node)
        assert isinstance(element, Element)
        assert element.parent is self

        if node.first is None:
            self.remove(element)
            return

        after_element = element.next

        element_to_add = node.first
        while element_to_add is not None:
            element_to_add.parent = self
            element_to_add = element_to_add.next

        element.next = node.first
        node.first.prev = element

        node.last.next = after_element
        if after_element is None: self.last = node
        else: after_element.prev = node.last
        node.first = None
        node.last = None

        self.remove(element)



    # # expands node in self with the elements of form
    # # so (a b c).replace_explode(b, (d e)) = (a b-expanded-to(d e) c)
    # def expand_explode(self, element, node_or_list):
    #     assert isinstance(node_or_list, Node) or isinstance(node_or_list, list)
    #     if isinstance(node_or_list, list):
    #         node_or_list = Node(node_or_list)
    #     new_element = Element(node_or_list, self)
    #     new_element.next = element.next
    #     new_element.prev = element.prev
    #     assert element.expansion is None
    #     element.expansion = new_element

    # ( ... first_node ... last_node ...)
    # =>
    # ( ... (first_node ... last_node) ...)
    def wrap(self, first_element, last_element, node_class_constructor = None, *node_class_constructor_args, **node_class_constructor_kwargs):

        new_node = Node() if node_class_constructor is None else node_class_constructor(*node_class_constructor_args, **node_class_constructor_kwargs)
        new_element = Element(new_node, self)
        new_element.prev = first_element.prev
        new_element.next = last_element.next
        new_node.first = first_element
        new_node.last = last_element
        # if c is the head
        if first_element.prev is None: self.first = new_element
        else: first_element.prev.next = new_element
         # if c is the tail
        if last_element.next is None: self.last = new_element
        else: last_element.next.prev = new_element

        new_node.last.next = new_node.first.prev = None

        for e in new_node:
            e.parent = new_node
            new_node.range.update(e.code.range if e.code is not None else e.range)

        return new_element

    # # ( ... (a b c) ... ) where parameter node = (a b c)
    # # =>
    # # ( ... a b c ...)
    # def unwrap(self, node):
    #     if not isinstance(node, Form):
    #         return
    #
    #     if node.is_head(): self.first = node.head
    #     else: node.prev.next = node.head
    #     if node.is_tail(): self.last = node.tail
    #     else: node.next.prev = node.tail
    #
    #     node.head.prev = node.prev
    #     node.tail.next = node.next
    #
    #     for e in node:
    #         e.par = self


    def __len__(self):
        count = 0
        for _ in self:
            count += 1
        return count

    def __getitem__(self, key):
        c = len(self)
        if c == 0 and key == 0:
            return None

        if isinstance(key, slice):
            raise NotImplementedError()
            # if key.step != None:
            #     return [self[i] for i in range(key.start, min(key.stop, len(self)))] # FIXME
            # else:
            #     ret = []
            #     i = key.start
            #     element = self[i]
            #     while element is not None and i < key.stop:
            #         ret.append(element)
            #         element = element.next
            #         i -= 1
            #     return ret

        if not isinstance(key, int) or key >= c or key < -c:
            raise IndexError()
        if key >= 0:
            for c in self:
                if key == 0: return c
                key -= 1
        else:
            return self[c + key]


    def __setitem__(self, key, value):
        c = len(self)
        if not isinstance(key, int) or key >= c or key < -c:
            raise IndexError()
        if key >= 0:
            for c in self:
                if key == 0:
                    self.replace(c, value)
                key -= 1
        else:
            self[c + key] = value

    def __delitem__(self, key):
        c = len(self)
        if not isinstance(key, int) or key >= c or key < -c:
            raise IndexError()
        if key >= 0:
            for c in self:
                if key == 0:
                    self.remove(c)
                key -= 1
        else:
            del self[c + key]

    def __iter__(self):
        return NodeIterator(self.first)

    def iterate_from(self, start:int):
        return NodeIterator(self[start] if len(self) > start else None)

    def __str__(self):
        children = [str(element.code) if element.code is not None else str(element) for element in self]
        return "Node(%s)" % ", ".join(children)

    # def __contains__(self, item):
    #     if isinstance(item, Symbol):
    #         for c in self:
    #             if isinstance(c, Symbol) and c.val == item.name:
    #                 return True
    #     elif isinstance(item, Literal):
    #         for c in self:
    #             if isinstance(c, Literal) and c.val == item.val:
    #                 return True
    #
    #     # todo: isinstance(type, Form) ?
    #     else:
    #         return False