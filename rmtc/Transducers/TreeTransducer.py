from typing import List

import rmtc.Common.Options as Options
from rmtc.Common.StringStuff import indent_string
from rmtc.Syntax.Code import Code
from rmtc.Syntax.LispPrinter import indented_lisp_printer
from rmtc.Syntax.Node import Node


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
            if Options.PRINT_TREE_TRANSDUCER_OUTPUTS is True:
                if Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST is None or tt.name in Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST:
                    print(indent_string("After transducer: " + tt.name + "\n" +indented_lisp_printer(form), 4))