from anoky.Common.Record import Record
from anoky.Expansion.ExpansionContext import ExpansionContext

from anoky.Syntax.Node import Node, Element
from anoky.Syntax.Form import Form
from anoky.Syntax.Seq import Seq
from anoky.Syntax.Literal import Literal
from anoky.Syntax.Identifier import Identifier







class Expander(object):


    def expand(self, element:Element, context:ExpansionContext):
        raise NotImplementedError()





class DefaultExpander(Expander):
    """
    Default macro expander.


    """


    def expand_unit(self, unit:Node, **kwargs):

        from anoky.Expansion.Macros.Alias import DefAlias
        from anoky.Expansion.Macros.Quote import Quote
        from anoky.Expansion.Macros.Rawmacro import RawMacro, RawSpecialForm
        from anoky.Generation.SpecialForms.Import import MacroImport

        assert(isinstance(unit, Node))
        context_root_bindings = Record(
            default_expander = self,
            expander = self,
            macro_table = {"quote":Quote(),
                           "rawmacro":RawMacro(),
                           "rawspecial":RawSpecialForm(),
                           "importmacro":MacroImport()},
                          #"import" etc.
                          #"defalias":DefAlias()},
            id_macro_table = {}
        )
        context_root_bindings.update(kwargs)
        EC = ExpansionContext(**context_root_bindings.__dict__)
        #unit.cg_context = EC
        for element in unit:
            EC.expand(element)

        return EC











    # split macro application and recursive expansion
    #   into two functions?


    def expand(self, element:Element, EC:ExpansionContext):

        code = element.code


        # expand downwards by cases

        if isinstance(code, Form):

            head = code.first
            headcode = head.code

            # check if any macros apply

            if isinstance(headcode, Identifier) \
                    and headcode.full_name in EC.macro_table:

                EC.macro_table[headcode.full_name].expand(element, EC)

            # otherwise expand recursively
            else:

                for item in code:
                    EC.expand(item)


        elif isinstance(code, Seq):
            # expand all elements in the seq

            for item in code:

                EC.expand(item)


        elif isinstance(code, Literal):

            pass


        elif isinstance(code, Identifier):

            # IDENTIFIER MACROS
            if code.full_name in EC.id_macro_table:

                idmac = EC.id_macro_table[code.full_name]

                idmac.expand(element, EC)

#                element.parent.replace(element, idmac.expand(element, context))







def expand_macros(code:Node):
    default_expander = DefaultExpander()
    c = ExpansionContext(default_expander=default_expander)
    for item in code:
        c.expand(item)