from Syntax.Element import Element

__author__ = 'bruno'


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