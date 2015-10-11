from Syntax.Element import Element

__author__ = 'bruno'


class ArrangementRule(object):
    def __init__(self, name:str):
        self.name = name

    def applies(self, element:Element):
        raise NotImplementedError()

    def apply(self, element:Element) -> Element:
        raise NotImplementedError()



