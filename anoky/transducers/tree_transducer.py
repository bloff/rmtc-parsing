from typing import List

from anoky.common.globals import G
from anoky.common.string_stuff import indent_string
from anoky.syntax.code import Code
from anoky.syntax.lisp_printer import indented_lisp_printer
from anoky.syntax.node import Node


class TreeTransducer(object):
    """
    A tree transducer defines some transformation on trees, represented by nested nodes (see :ref:`Node`).
    """
    def __init__(self, name:str):
        self.name = name

    def transduce(self, tree:Node):
        """
        Modifies the given tree according to some transformation.
        """

        raise NotImplementedError()



def apply_transducer_chain(transducer_chain:List[TreeTransducer], form:Code):
    """
    Applies each tree transducer in a given list, in turn.
    """
    for tt in transducer_chain:
        if isinstance(form, Node) and len(form) > 0:
            tt.transduce(form)
            if G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS is True:
                if G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST is None or tt.name in G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST:
                    print(indent_string("After transducer: " + tt.name + "\n" +indented_lisp_printer(form), 4))