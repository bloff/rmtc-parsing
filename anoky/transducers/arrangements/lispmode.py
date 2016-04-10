import anoky.transducers.arrangements.util as Util
from anoky.syntax import tokens as Tokens
from anoky.syntax.form import Form
from anoky.syntax.node import Element
from anoky.syntax.preseq import PreSeq
from anoky.syntax.token import is_token
from anoky.transducers.arrangement_rule import ArrangementRule


class LispMode(ArrangementRule):
    """
    Applies the transformation::

      BEGIN_MACRO("(") ⋅ (BEGIN  END)* END_MACRO  ⟨⟅*⟆⟩ ⋅

    which removes BEGIN and END tokens, wraps what's left in a PreTuple, and that in a Punctuator. The list of punctuation
    tokens given to the punctuator is the appending of all lists of punctuation tokens in each ``BEGIN  END`` pair.
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Lisp Mode")

    def applies(self, element):
        return Util.is_opening_delimiter(element, '#(')

    def apply(self, element) -> Element:
        node_type = PreSeq if element.node_type is "seq" else Form
        new_node_element = element.parent.wrap(element, element.end, node_type)
        new_node = new_node_element.code

        new_node.remove(element) # remove BEGIN_MACRO('#(')
        new_node.remove(element.end)  # remove END_MACRO(')')

        return new_node_element.next
