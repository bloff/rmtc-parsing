from rmtc.Common.Errors import TokenizingError
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Punctuator import Punctuator
from rmtc.Syntax.Node import Node
from rmtc.Syntax.Seq import Seq
from rmtc.Syntax.PreSeq import PreSeq
from rmtc.Syntax.PreForm import PreForm
from rmtc.Transducers.TreeTransducer import TreeTransducer

class ConvertPreforms(TreeTransducer):
    """
    Transverses the tree in a bottom-up fashion. For each PreForm or PreTuple, converts it into a Form or Tuple if more than
    one child is present, and otherwise replaces the PreForm/PreTuple with its single child.
    """
    def __init__(self):
        TreeTransducer.__init__(self, "Convert Preforms")

    def transduce(self, node):
        for e in node:
            code = e.code
            if isinstance(code, Node):
                self.transduce(code)
            if isinstance(code, PreForm):
                if len(code) == 0:
                    node.remove(e)
                elif len(code) <= 1:
                    node.replace(e, code.first)
                else:
                    new_form_element = code.wrap(code.first, code.last, Form)
                    node.replace(e, new_form_element)
            elif isinstance(code, PreSeq):
                if len(code) == 0:
                    node.remove(e)
                elif len(code) <= 1:
                    node.replace(e, code.first)
                else:
                    code.wrap(code.first, code.last, Seq)
                    node.replace(e, code.first)
            elif isinstance(code, Punctuator):
                raise TokenizingError("Unexpected unprocessed punctuator.")
                # last = e
                # for subelm in code:
                #     code.remove(subelm)
                #     node.insert(last, subelm)
                #     last = subelm
                # node.remove(e)