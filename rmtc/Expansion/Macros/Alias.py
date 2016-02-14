from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Macro import Macro

from rmtc.Syntax.Code import Code
from rmtc.Syntax.Node import Element, Node
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier





class Alias(Macro):

    def __init__(self, id_alias:Identifier=None, substitution:Code=None):

        # can a code instance evaluate to False?
        #   we want to be able to alias empty-like code to identifiers
        # if id_alias and substitution != None:
        #
        #     self.configure_expand(id_alias, substitution)

        self.substitution = substitution




    def expand(self, element, context):

        element.expand(self.substitution.copy())

        context.expand(element)


    # def configure_expand(self, id_alias:Identifier, substitution:Code):
    #
    #
    #     def alias_expand(self, element:Element, context:ExpansionContext):
    #
    #         element.expand(substitution)
    #
    #         # do we want to continue macro-expanding with
    #         #   the freshly substituted code?
    #         context.expander.expand(element, context)
    #
    #
    #     self.expand = alias_expand








class DefAlias(Macro):

    # (defalias name form)

    def expand(self, element:Element, context:ExpansionContext):

        form = element.code

        # check we're looking at something of the right form
        assert isinstance(form, Form) and len(form) == 3

        # extract the identifier and replacement code from the form
        id_alias = form[1].code
        substitution = form[2].code

        # create an Alias instance according to the specified replacement
        alias_macro = Alias(id_alias, substitution)

        # add the new macro to the macro table
        context.id_macro_table[id_alias.name] = alias_macro




