from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Expander import Expander, DefaultExpander

from rmtc.Syntax.Node import Node, Element
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Seq import Seq
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Identifier import Identifier





class Macro(Expander):
    """
    When implementing a Macro, any further macro expansion down the tree must be explicitly specified..

    """

    def __init__(self, parent_expander:DefaultExpander=None):
        self.parent_expander = parent_expander


    def expand(self, element:Element, context:ExpansionContext):

        raise NotImplementedError()



    def default_expand(self, element:Element, context:ExpansionContext):
        """
        When writing a custom expand method for a macro instance,
        this default_expand method can be called at the end of the
        custom expand if the macro expansion process should continue
        down the tree after the macro is applied.

        If the Macro instance was called from another Expander instance
         (another macro or a DefaultExpander), this will essentially
         "return control" to that. Otherwise, this uses the .expand
         method defined in the DefaultExpander class.

        :param element:
        :param context:
        :return:
        """

        if self.parent_expander:
            return self.parent_expander.expand(element, context)
        else:
            return DefaultExpander.expand(self, element, context)