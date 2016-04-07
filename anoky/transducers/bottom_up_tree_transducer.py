from anoky.syntax.node import Node
from anoky.transducers.arrangement import Arrangement
from anoky.transducers.tree_transducer import TreeTransducer


class BottomUpTreeTransducer(TreeTransducer):
    """
    A bottom-up tree transducer is defined by an arrangement (see :ref:`Arrangement`), and transforms a tree by traversing
    it from bottom to top, and applying the arrangement at each level.

    So it starts at the root of the tree, and recursively calls itself on each child. It then applies the arrangement to the root,
    which may modify it.
    """
    def __init__(self, name:str, arrangement:Arrangement):
        TreeTransducer.__init__(self, name)
        self.arrangement = arrangement

    def transduce(self, tree):
        for elm in tree:
            if isinstance(elm.code, Node):
                self.transduce(elm.code)
        self.arrangement.arrange(tree)