from rmtc.Expansion.ExpansionContext import ExpansionContext

from rmtc.Syntax.Node import Node, Element
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Seq import Seq
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Identifier import Identifier





class Expander(object):


    def expand(self, element:Element, context:ExpansionContext):
        raise NotImplementedError()





class DefaultExpander(Expander):


    # split macro application and recursive expansion
    #   into two functions?


    def expand(self, element:Element, context:ExpansionContext):

        code = element.code

        # check if any macros apply
        # ..or only do this for Forms?

        # continue expanding downwards
        if isinstance(code, Form):

            head = code.first

            pass


        if isinstance(code, Seq):
            # expand all elements in the seq

            pass


        if isinstance(code, Literal):

            pass


        if isinstance(code, Identifier):

            pass






