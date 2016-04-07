from anoky.syntax.node import Element



class ArrangementRule(object):
    """
    An arrangement rule is a conditional transformation of an :ref:`Element` within a :ref:`Node`.
    """
    def __init__(self, name:str):
        self.name = name

    def applies(self, element:Element) -> bool:
        """
        This method should return ``True`` iff the rule should be applied at the position of the given :ref:`Element`.
        """
        raise NotImplementedError()

    def apply(self, element:Element) -> Element:
        """
        Assuming that ``self.applies(element) is True``, this method transforms the given element, and/or its parent
        node. It should return the next element to be read (usually the element immediately to the left or to the right
        of the elements involved in the transformation).
        """
        raise NotImplementedError()



