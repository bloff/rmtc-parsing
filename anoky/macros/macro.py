from anoky.expansion.expander import Expander
from anoky.expansion.expansion_context import ExpansionContext
from anoky.syntax.node import Element


class Macro(Expander):
    """
    Defining a macro involves instantiating this class or a subclass thereof
     and implementing its .expand method.

    """

    def __init__(self,
                 specs=None,
                 expand_func=None,
                 parent_expander=None):

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



