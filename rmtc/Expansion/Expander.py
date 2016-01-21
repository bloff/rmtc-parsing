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
    """
    Default macro expander.


    """

    # split macro application and recursive expansion
    #   into two functions?


    def expand(self, element:Element, context:ExpansionContext):

        code = element.code


        # expand downwards by cases

        if isinstance(code, Form):

            head = code.first
            headcode = head.code

            # check if any macros apply

            if isinstance(headcode, Identifier) and headcode.name in context.macro_table:

                context.macro_table[headcode.name].expand(element, context)

            # otherwise expand recursively
            else:

                for item in code:
                    context.expand(item)


        if isinstance(code, Seq):
            # expand all elements in the seq

            for item in code:
                context.expand(item)


        if isinstance(code, Literal):

            pass


        if isinstance(code, Identifier):

            # IDENTIFIER MACROS
            if code.name in context.id_macro_table:

                idmac = context.id_macro_table[code.name]

                element.parent.replace(element, idmac.expand(element, context))







def expand_macros(code:Node):
    default_expander = DefaultExpander()
    c = ExpansionContext(default_expander=default_expander)
    for item in code:
        c.expand(item)