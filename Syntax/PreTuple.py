from Syntax.Tuple import Tuple

__author__ = 'bruno'


class PreTuple(Tuple):
    def __init__(self, *children):
        Tuple.__init__(self, *children)