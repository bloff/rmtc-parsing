from typing import Union

from rmtc.Streams.StreamRange import StreamRange
from rmtc.Syntax.Code import Code


class Element(object):
    """
    An element of a Node.

    :param code_or_element:
      If ``code_or_element`` is not an ``Element``, then code_or_element is the code attribute of the new element.
      If ``code_or_element`` is an ``Element``, then ``code_or_element``'s ``code`` attribute is the code attribute of the new element.
    :param parent: The ``Node`` containing this element.
    :param kwargs: Any number of attributes that should be associated with this element.
    """
    def __init__(self, code_or_element, parent=None, **kwargs):
        assert parent is None or isinstance(parent, Node)
        self.__dict__.update(kwargs)

        self.parent = parent
        """The ``Node`` containing this element."""
        self.prev = None
        """The ``Element`` that precedes this element, or ``None`` if this is the first element."""
        self.next = None
        """The ``Element`` that follows this element, or ``None`` if this is the last element."""
        self.code = None
        """The ``Code`` associated with this element. May be ``None``."""



        if code_or_element is None or isinstance(code_or_element, Code):
            self.code = code_or_element
        else:
            assert isinstance(code_or_element, Element)
            self.code = code_or_element.code

    @staticmethod
    def _make_new_element(code_or_element, parent=None):
        if isinstance(code_or_element, Code):
            return Element(code_or_element, parent)
        else:
            assert isinstance(code_or_element, Element)
            if code_or_element.parent is None:
                code_or_element.parent = parent
                return code_or_element
            else:
                return Element(code_or_element, parent)


    def __getattr__(self, item):
        return self.__dict__.get(item, None)

    def __setattr__(self, key, item):
        self.__dict__[key] = item

    def update(self, other, **kwargs):
        self.__dict__.update(other, **kwargs)

    def wipe(self):
        parent, prev, next, code = self.parent, self.prev, self.next, self.code
        self.__dict__.clear()
        self.parent, self.prev, self.next, self.code = parent, prev, next, code

    def expand(self, code:Code):
        self.wipe()
        self.code = code

    def detach(self):
        parent, prev, next, code = self.parent, self.prev, self.next, self.code
        detached_element = Element(None)
        detached_element.__dict__ = self.__dict__
        detached_element.parent, detached_element.prev, detached_element.next, detached_element.code = None, None, None, None
        self.__dict__ = dict()
        self.parent, self.prev, self.next, self.code = parent, prev, next, None
        return detached_element


    def is_last(self):
        """
        Whether this element is the last of its Node. Returns ``False`` if parent is ``None``.
        """
        return self.parent is not None and self.parent.last is self

    def is_first(self):
        """
        Whether this element is the first of its Node. Returns ``False`` if parent is ``None``.
        """
        return self.parent is not None and self.parent.first is self

    @property
    def number(self) -> int:
        """
        The position of this element in its parent ``Node``.
        """
        node = self
        i = 0
        while not node.is_first():
            i += 1
            node = node.prev
        return i

    @property
    def range(self) -> StreamRange:
        """
        The range attribute (of ``StreamRange`` type) of this element's associated ``Code`` instance.
        """
        assert self.code is not None
        return self.code.range

    def __str__(self):
        if self.code is not None:
            return "Element(%s)" % str(self.code)
        else:
            return "Element()"


class NodeIterator(object):
    """
    An iterator over the elements of a node. After iterating over some element,
    it is OK to change the node up to (and including) that element, but
    changing the node after that element might result in unexpected behavior
    (the iterator's behavior becomes undefined).
    """
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
    """
    A doubly-linked list.
    """

    # Given a list of elements and/or Code instances, or a sequence of elements and/or Code instances as arguments
    # creates a node whose elements have the given code instances, and the code instances of the given elements;
    # e.g., Node(1, 2, elm) has elements: Element.make(1), Element.make(2), Element.make(elm.value)
    def __init__(self, *children):
        super(Node, self).__init__()
        if len(children) == 1 and isinstance(children[0], list):
            children = children[0]

        self.first = None
        """The first Element of the doubly-linked list."""
        self.last = None
        """The last Element of the doubly-linked list."""

        self.range = StreamRange()

        if len(children) > 0:
            assert isinstance(children[0], Code) or isinstance(children[0], Element)
            current = self.first = Element._make_new_element(children[0], self)
            self.range.update(current.code.range)
            for child in children[1:]:
                assert isinstance(child, Code) or isinstance(child, Element)
                current.next = Element._make_new_element(child, self)
                current.next.prev = current
                current = current.next
                self.range.update(current.code.range)
            self.last = current

    def erase(self):
        """
        Empties the entire list.
        """
        for node in self:
            node.parent = node.next = node.prev = None
        self.first = self.last = None

    def prepend(self, child:Union[Code,Element]):
        """
        Adds an element to the beginning of this node.

        :param child: A Code or an Element to be inserted. If ``child`` is an Element whose ``parent`` field is ``None``,
          the element will be changed to have this node as its parent.

        :type child: Code or Element

        """
        assert isinstance(child, Code) or isinstance(child, Element)
        element = Element._make_new_element(child, self)
        self.range.update(element.range)
        if self.first is None:
            self.first = self.last = element
        else:
            self.first.prev = element
            element.next = self.first
            self.first = element

    def append(self, child):
        """
        Adds an element to the end of this node.

        :param child: A Code or an Element to be inserted. If ``child`` is an Element whose ``parent`` field is ``None``,
          the element will be changed to have this node as its parent.

        :type child: Code or Element

        """
        assert isinstance(child, Code) or isinstance(child, Element)
        element = Element._make_new_element(child, self)
        self.range.update(element.range)
        if self.first is None:
            self.first = self.last = element
        else:
            self.last.next = element
            element.prev = self.last
            self.last = element

    def insert(self, after_this:Element, child):
        """
        Inserts a new element after a given element of this node.

        :param after_this: An Element (whose ``parent`` must be this node) after which
           the new element is to be inserted.

        :type after_this: Element

        :param child: A Code or an Element to be inserted. If ``child`` is an Element whose ``parent`` field is ``None``,
          the element will be changed to have this node as its parent.

        :type child: Code or Element

        """
        assert isinstance(after_this, Element) or (after_this is None and self.first is None)
        assert isinstance(child, Code) or isinstance(child, Element)
        if after_this is None and self.first is None:
            self.append(child)
        else:
            assert after_this.parent is self
            element = Element._make_new_element(child, self)
            self.range.update(element.range)
            element.next = after_this.next
            element.prev = after_this
            if after_this.next is not None:
                after_this.next.prev = element
            else: self.last = element
            after_this.next = element

    def remove(self, element):
        """
        Inserts a new element after a given element of this node.

        :param element: An Element (whose ``parent`` must be this node) after which
           the new element is to be inserted.

        :type element: Element

        """
        assert isinstance(element, Element)
        assert element.parent is self

        if element.prev is None: self.first = element.next
        else: element.prev.next = element.next
         # if node is the tail
        if element.next is None: self.last = element.prev
        else: element.next.prev = element.prev
        element.parent = element.next = element.prev = None

    def replace(self, element, new_child):
        """
        Replacesa given element of this node with a new element.

        :param element: The element (whose ``parent`` must be this node)
            to be replaced.

        :type element: Element

        :param new_child: A Code or an Element to be inserted. If ``child`` is an Element whose ``parent`` field is ``None``,
          the element will be changed to have this node as its parent.

        :type new_child: Code or Element

        """
        assert isinstance(element, Element)
        assert element.parent is self
        assert isinstance(new_child, Code) or isinstance(new_child, Element)
        new_element = Element._make_new_element(new_child, self)
        self.range.update(new_element.range)
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

    # replaces node in self with the elements of given Node
    # Destroys the given Node in the process
    # so (a b c).replace_explode(b, (d e)) = (a d e c), and the (d e) node becomes ()
    def replace_explode_modify(self, element, node):
        """
        Replaces a given element of this node with the sequence of elements given by another node.

        **This operation removes the elements from the given node, and makes this node their parent.**

        :param element: The element (whose ``parent`` must be this node)
            to be replaced.

        :type element: Element

        :param node: A ``Node`` whose elements will replace the given element.

        :type node: Node

        """
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


    # ( ... first_node ... last_node ...)
    # =>
    # ( ... (first_node ... last_node) ...)
    def wrap(self, first_element, last_element, node_class_constructor = None, *node_class_constructor_args, **node_class_constructor_kwargs):
        """
        Replaces the sequence of elements of this node between first_element and end_punctuation_marker with a new node,
        containing that very same sequence.

        :param first_element: The first element (whose ``parent`` must be this node)
            in the sequence to be wrapped.

        :type first_element: Element

        :param last_element: The first element (whose ``parent`` must be this node)
            in the sequence to be wrapped.

        :type last_element: Element

        :param node_class_constructor: A subtype of ``Node`` which will be used to construct the new node.

        :type node_class_constructor: type

        :param node_class_constructor_args: Arguments to pass to the constructor of the new node.

        :param node_class_constructor_kwargs: Keyword arguments to pass to the constructor of the new node.

        """
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
            # start, stop, step = slice.start, slice.stop, slice.step
            # if step is not None:
            #     raise NotImplementedError()

            ii = key.indices(c)
            return [self[i] for i in range(*ii)]

            # raise NotImplementedError()

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
        """
        Returns an iterator that goes through all elements from the ``start`` position to the end of the node.
        """
        return NodeIterator(self[start] if len(self) > start else None)

    def __str__(self):
        children = [str(element.code) if element.code is not None else str(element) for element in self]
        return "Node(%s)" % ", ".join(children)

