from Common import Options
from Common.StringStuff import indent_string
from Syntax.LispPrinter import indented_lisp_printer
from Syntax.Node import Node


class TreeTransducer(object):
    def __init__(self, name:str):
        self.name = name

    def transduce(self, tree):
        raise NotImplementedError()



def apply_transducer_chain(transducer_chain, form):
    """
    :type transducer_chain: list(TopDownTreeTransducer)
    :type form: Code
    """
    for tt in transducer_chain:
        if isinstance(form, Node) and len(form) > 0:
            tt.transduce(form)
            if Options.PRINT_TREE_TRANSDUCER_OUTPUTS is True:
                if Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST is None or tt.name in Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST:
                    print(indent_string("After transducer: " + tt.name + "\n" +indented_lisp_printer(form), 4))