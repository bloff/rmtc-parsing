from anoky.syntax.node import Node
from anoky.transducers.arrangement import Arrangement
from anoky.transducers.tree_transducer import TreeTransducer

class TopDownTreeTransducer(TreeTransducer):
    """
    A top-down tree transducer is defined by an arrangement (see :ref:`Arrangement`), and transforms a tree by traversing
    it from top to bottom, and applying the arrangement at each level.

    So it starts at the root of the tree, and applies the arrangement, which could modify the root; it then goes through each
    child of the (modified) root node, and recursively calls itself on that child.
    """
    def __init__(self, name:str, arrangement:Arrangement):
        TreeTransducer.__init__(self, name)
        self.arrangement = arrangement

    def transduce(self, tree):
        self.arrangement.arrange(tree)
        for elm in tree:
            if isinstance(elm.code, Node):
                self.transduce(elm.code)

    def get_rule(self, name):
        return self.arrangement.get_rule(name)

    def insert_rule(self, after_rule_with_name, rule):
        return self.arrangement.insert_rule(after_rule_with_name, rule)

    def insert_rule_before(self, after_rule_with_name, rule):
        return self.arrangement.insert_rule_before(after_rule_with_name, rule)