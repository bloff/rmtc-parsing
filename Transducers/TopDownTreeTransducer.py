from Syntax.__exports__ import Node
from Transducers.Arrangements import Arrangement
from Transducers.TreeTransducer import TreeTransducer

class TopDownTreeTransducer(TreeTransducer):
    def __init__(self, name:str, arrangement:Arrangement):
        TreeTransducer.__init__(self, name)
        self.arrangement = arrangement

    def transduce(self, tree):
        self.arrangement.arrange(tree)
        for elm in tree:
            if isinstance(elm.code, Node):
                self.transduce(elm.code)