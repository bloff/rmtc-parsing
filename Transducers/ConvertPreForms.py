from Syntax.Punctuator import Punctuator
from Syntax.__exports__ import Node, Form, Tuple
from Syntax.PreTuple import PreTuple
from Syntax.PreForm import PreForm
from Transducers.TreeTransducer import TreeTransducer

__author__ = 'bruno'


class ConvertPreforms(TreeTransducer):
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
                    if code.prepend_head is not None:
                        new_form_element.code.prepend(code.prepend_head)
                    node.replace(e, new_form_element)
            elif isinstance(code, PreTuple):
                if len(code) == 0:
                    node.remove(e)
                elif len(code) <= 1:
                    node.replace(e, code.first)
                else:
                    code.wrap(code.first, code.last, Tuple)
                    node.replace(e, code.first)
            elif isinstance(code, Punctuator):
                last = e
                for subelm in code:
                    code.remove(subelm)
                    node.insert(last, subelm)
                    last = subelm
                node.remove(e)