from anoky.common.context import Context
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element #, Node

class ExpansionContext(Context):

    def __init__(self, **kwargs):
        Context.__init__(self, "Macro Expansion Context")

        self.set(gensym_count = 0)
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


    def gensym(self):
        self.set(gensym_count = self.gensym_count + 1)

        return Identifier("GENSYM_" + str(self.gensym_count))

