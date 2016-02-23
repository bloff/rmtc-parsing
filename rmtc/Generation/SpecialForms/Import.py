import ast

import importlib

from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Macro import Macro, IdentifierMacro
from rmtc.Generation.GenerationContext import GenerationContext

from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier

from rmtc.Syntax.Node import Element




class Import(Macro, SpecialForm):

    HEADTEXT = "import"
    DOMAIN = SDom

    def expand(self, element:Element, EC:ExpansionContext):

        #raise NotImplementedError()

        acode = element.code

        imports_list = []

        for to_import_element in acode[1:]:

            if isinstance(to_import_element.code, Identifier):

                to_import_name = to_import_element.code.full_name

                imports_list.append(to_import_name)

            else:

                assert isinstance(to_import_element.code, Form) \
                    and isinstance(to_import_element.code[0].code, Identifier) \
                    and to_import_element.code[0].code.full_name == "as"

                # assert 1 and 2 are also code

                to_import_name = to_import_element.code[1].code.full_name
                to_import_asname = to_import_element.code[2].code.full_name

                imports_list.append((to_import_name, to_import_asname))

        for to_import_name in imports_list:

            if isinstance(to_import_name, str):

                raise NotImplementedError()

            else:

                # assert isinstance(to_import_name, tuple)

                raise NotImplementedError()


# (import module_names+)
# where each module_name is either a name (an Identifier) or
#    (as name newname)

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        imports_list = []

        with GC.let(domain=ExDom):

            for to_import_element in acode[1:]:

                if isinstance(to_import_element.code, Identifier):

                    to_import_name = to_import_element.code.full_name

                    imports_list.append(ast.alias(name=to_import_name,
                                                  asname=None))

                else:

                    assert isinstance(to_import_element.code, Form) \
                        and isinstance(to_import_element.code[0].code, Identifier) \
                        and to_import_element.code[0].code.full_name == "as"

                    # assert 1 and 2 are also code

                    to_import_name = to_import_element.code[1].code.full_name
                    to_import_asname = to_import_element.code[2].code.full_name

                    imports_list.append(ast.alias(name=to_import_name,
                                                  asname=to_import_asname))



        return




class ImportFrom(Macro, SpecialForm):

    HEADTEXT = "from"
    DOMAIN = SDom

    # (from module_name import names+)
    # where each name is either an identifier or
    #   (as name newname)


    def expand(self, element:Element, EC:ExpansionContext):

        acode = element.code

        module_name = acode[1].code.full_name

        #assert acode[2].code.full_name == "import"

        imports_list = []

        for to_import_element in acode [3:]:

            if isinstance(to_import_element.code, Identifier):

                to_import_name = to_import_element.code.full_name

                imports_list.append(to_import_name)

            else:

                assert isinstance(to_import_element.code, Form) \
                    and isinstance(to_import_element.code[0].code, Identifier) \
                    and to_import_element.code[0].code.full_name == "as"

                # assert 1 and 2 are also code

                to_import_name = to_import_element.code[1].code.full_name
                to_import_asname = to_import_element.code[2].code.full_name

                imports_list.append((to_import_name, to_import_asname))





    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code







        # return








class MacroImport(Macro, SpecialForm):

    HEADTEXT = "macroimport"


    def expand(self, element:Element, EC:ExpansionContext):

        acode = element.code

        module_name = acode[1].code.full_name

        macro_names = []

        for macro_name_element in acode[2:]:

            macro_names.append(macro_name_element.code.full_name)


        mod = importlib.import_module(module_name)
        modmacros = mod.__macros__

        #check for __macros__

        try:
            __macros__
        except NameError:
            __macros__ = {}

        for macro_name in macro_names:

            __macros__[macro_name] = modmacros[macro_name]


        return




    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()




class IdMacroImport(Macro, SpecialForm):

    def expand(self, element:Element, EC:ExpansionContext):

        raise NotImplementedError()

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()







def check_for_pyc(name):
    """


    """



    return






















