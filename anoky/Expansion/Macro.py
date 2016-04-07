from anoky.Expansion.ExpansionContext import ExpansionContext
from anoky.Expansion.Expander import Expander, DefaultExpander
from anoky.Syntax.Code import Code

from anoky.Syntax.Node import Node, Element
from anoky.Syntax.Form import Form
from anoky.Syntax.Seq import Seq
from anoky.Syntax.Literal import Literal
from anoky.Syntax.Identifier import Identifier





class Macro(Expander):
    """
    Defining a macro involves instantiating this class or a subclass thereof
     and implementing its .expand method.

    """

    def __init__(self,
                 specs=None,
                 expand_func=None,
                 parent_expander:DefaultExpander=None):

        self.parent_expander = parent_expander

        # synthesize .expand method from
        #   ([parameters*], replacement_code)

        # if specs is not (None, None):
        #     params, rcode = specs
        #
        #     self.init_basic_expand(params=params, rcode=rcode)


        # allow providing an .expand function directly
        # elif expand_func:
        #     self.expand = expand_func



    def init_basic_expand(self, params, rcode):

        raise NotImplementedError()

        # def expand(self, element:Element, EC:ExpansionContext):
        #
        #
        # self.expand = expand







    def expand(self, element:Element, context:ExpansionContext):
        """


        To resume expansion downwards (to return control to the default expander,
        essentially) after applying the macro, just call
         context.expand(resume_at_this_node).
        """

        raise NotImplementedError()








###### BELOW IS TENTATIVE ######

class IdentifierMacro(Expander):


    def expand(self, id_element:Element, context:ExpansionContext):
        """
        *expand method for identifier macros does not need the current element
         as input*

        """

        raise NotImplementedError()



