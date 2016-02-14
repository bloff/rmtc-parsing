from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Expander import Expander, DefaultExpander

from rmtc.Syntax.Node import Node, Element
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Seq import Seq
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Identifier import Identifier





class Macro(Expander):
    """
    Defining a macro involves instantiating this class or a subclass thereof
     and implementing its .expand method.

    """

    def __init__(self, parent_expander:DefaultExpander=None):
        self.parent_expander = parent_expander


    def expand(self, element:Element, context:ExpansionContext):
        """


        To resume expansion downwards (to return control to the default expander,
        essentially) after applying the macro, just call
         context.expander.expand(resume_at_this_node).
        """

        raise NotImplementedError()








###### BELOW IS TENTATIVE ######

class IdentifierMacro(Expander):


    def expand(self, context:ExpansionContext):
        """
        *expand method for identifier macros does not need the current element
         as input*

        """

        raise NotImplementedError()



