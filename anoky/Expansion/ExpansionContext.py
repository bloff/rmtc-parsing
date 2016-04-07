from anoky.Common.Context import Context
from anoky.Syntax.Node import Element #, Node

class ExpansionContext(Context):

    def __init__(self, **kwargs):
        Context.__init__(self, "Macro Expansion Context")

        # JUST PASS ALL KWARGS AT ONCE
        #for arg in kwargs:
        self.set(**kwargs)


        # if "expander" in kwargs:
        #     self.set(expander = kwargs["expander"])
        #
        # # do we need a MacroTable class?
        # if "macro_table" in kwargs:
        #     self.set(macro_table = kwargs["macro_table"])



    def expand(self, element:Element):
        self.expander.expand(element, self)
        return


