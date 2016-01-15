from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Expander import Expander, DefaultExpander

from rmtc.Syntax.Node import Node, Element
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Seq import Seq
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Identifier import Identifier





class Macro(Expander):


    def expand(self, element:Element, context:ExpansionContext):

        raise NotImplementedError()

