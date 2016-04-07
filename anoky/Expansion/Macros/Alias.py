from anoky.Expansion.ExpansionContext import ExpansionContext
from anoky.Expansion.Macro import Macro, IdentifierMacro
from anoky.Generation.GenerationContext import GenerationContext

from anoky.syntax.code import Code
from anoky.syntax.node import Element, Node
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier





class Alias(IdentifierMacro):

    def __init__(self, id_alias:Identifier=None, substitution:Code=None):
                 #parent_expander=None):

        #Macro.__init__(self, parent_expander=parent_expander)

        # can a code instance evaluate to False?
        #   we want to be able to alias empty-like code to identifiers
        # if id_alias and substitution != None:
        #
        #     self.configure_expand(id_alias, substitution)

        self.substitution = substitution




    def expand(self, id_element, EC:ExpansionContext):

        id_element.expand(self.substitution.copy())

        EC.expand(id_element)


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

    def expand(self, element:Element, EC:ExpansionContext):

        form = element.code

        # check we're looking at something of the right form
        assert isinstance(form, Form) and len(form) == 3

        # extract the identifier and replacement code from the form
        id_alias = form[1].code
        substitution = form[2].code

        # create an Alias instance according to the specified replacement
        alias_macro = Alias(id_alias, substitution)

        # add the new macro to the macro table
        EC.id_macro_table[id_alias.name] = alias_macro




    def generate(self, element:Element, context:GenerationContext):

        raise NotImplementedError()



