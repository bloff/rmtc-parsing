import ast

from importlib import import_module

from rmtc.Common.Errors import CodeGenerationError
from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Macro import Macro, IdentifierMacro
from rmtc.Generation.GenerationContext import GenerationContext

from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.LispPrinter import succinct_lisp_printer

from rmtc.Syntax.Node import Element
from rmtc.Syntax.Util import is_form, is_identifier


def get_import_name(element:Element) -> str:
    if is_identifier(element):
        return element.code.full_name # TODO: name mangling?
    elif is_form(element, '.'):
        return ".".join(get_import_name(e) for e in element.code.iterate_from(1))
    else:
        raise CodeGenerationError(element.range, "Expected a module path (`a.b.c`) , but found `%s`." % succinct_lisp_printer(element))

class Import(Macro, SpecialForm):

    HEADTEXT = "import"
    DOMAIN = SDom

    # (import module_names+)

    def expand(self, element:Element, EC:ExpansionContext):

        return

        # acode = element.code
        #
        #
        # imports_list = []
        #
        # for to_import_element in acode[1:]:
        #
        #     if isinstance(to_import_element.code, Identifier):
        #
        #         to_import_name = to_import_element.code.full_name
        #
        #         imports_list.append(to_import_name)
        #
        #     else:
        #
        #         assert isinstance(to_import_element.code, Form) \
        #             and isinstance(to_import_element.code[0].code, Identifier) \
        #             and to_import_element.code[0].code.full_name == "as"
        #
        #         # assert 1 and 2 are also code
        #
        #         to_import_name = to_import_element.code[1].code.full_name
        #         to_import_asname = to_import_element.code[2].code.full_name
        #
        #         imports_list.append((to_import_name, to_import_asname))
        #
        # for to_import_name in imports_list:
        #
        #     if isinstance(to_import_name, str):
        #
        #         raise NotImplementedError()
        #
        #     else:
        #
        #         # assert isinstance(to_import_name, tuple)
        #
        #         raise NotImplementedError()


# (import module_names+)
# where each module_name is either a name (an Identifier) or
#    (as name newname)

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        imports_list = []

        with GC.let(domain=ExDom):

            for to_import_element in acode[1:]:

                if isinstance(to_import_element.code, Identifier) or is_form(to_import_element.code, "."):

                    to_import_name = get_import_name(to_import_element)

                    imports_list.append(ast.alias(name=to_import_name,
                                                  asname=None))
                elif is_form(to_import_element.code, "as"):
                    # (as module_name as_name)

                    # assert isinstance(to_import_element.code, Form) \
                    #     and isinstance(to_import_element.code[0].code, Identifier) \
                    #     and to_import_element.code[0].code.full_name == "as"

                    to_import_name = get_import_name(to_import_element.code[1])
                    to_import_asname = to_import_element.code[2].code.full_name

                    imports_list.append(ast.alias(name=to_import_name,
                                                  asname=to_import_asname))
                else:
                    raise CodeGenerationError(to_import_element.range, "Special form `import` expected a module path (`a.b.c`) or an import alias `(as a.b.c name)`, but found `%s`." % succinct_lisp_printer(to_import_element))

        return ast.Import(imports_list)




# class ImportFrom(Macro, SpecialForm):
#
#     HEADTEXT = "from"
#     DOMAIN = SDom
#
#     # (from module_name import names+)
#     # where each name is either an identifier or
#     #   (as name newname)
#
#
#     def expand(self, element:Element, EC:ExpansionContext):
#
#         acode = element.code
#
#         module_name = acode[1].code.full_name
#
#         #assert acode[2].code.full_name == "import"
#
#         imports_list = []
#
#         for to_import_element in acode [3:]:
#
#             if isinstance(to_import_element.code, Identifier):
#
#                 to_import_name = to_import_element.code.full_name
#
#                 imports_list.append(to_import_name)
#
#             else:
#
#                 assert isinstance(to_import_element.code, Form) \
#                     and isinstance(to_import_element.code[0].code, Identifier) \
#                     and to_import_element.code[0].code.full_name == "as"
#
#                 # assert 1 and 2 are also code
#
#                 to_import_name = to_import_element.code[1].code.full_name
#                 to_import_asname = to_import_element.code[2].code.full_name
#
#                 imports_list.append((to_import_name, to_import_asname))
#
#
#
#
#
#     def generate(self, element:Element, GC:GenerationContext):
#
#         acode = element.code
#
#
#
#
#
#
#
#         # return








class MacroImport(Macro, SpecialForm):

    HEADTEXT = "importmacro"

# importmacro module.macro
# (importmacro (. module macro))
#
# importmacro module macros+
#
# from module importmacro macro1, macro2
# (from module importmacro (macro1, macro2))


    def expand(self, element:Element, EC:ExpansionContext):

        acode = element.code

        acode1 = acode[1].code

        module_name = get_import_name(acode1[1])

        macro_name = acode1[2].code.full_name


        #if isinstance(acode1[2].code, Identifier):
        #    macro_name = acode1[2].code.full_name

        # else:
        #     assert isinstance(acode1[2].code, Form) \
        #         and acode1[2].code[0].code.full_name == "as"

        # macro_names = []
        # for macro_name_element in acode[2:]:
        #     macro_names.append(macro_name_element.code.full_name)


        mod = import_module(module_name)

        modmacros = mod.__macros__

        # check for local __macros__?

        # for macro_name in macro_names:
        #     __macros__[macro_name] = modmacros[macro_name]

        #__macros__[macro_name] = modmacros[macro_name]

        EC.macro_table[macro_name] = modmacros[macro_name]

        return




    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        acode1 = acode[1].code

        module_name = acode1[1].code.full_name
        macro_name = acode1[2].code.full_name


        # generate code to import module
        # i.e. for
        #   from importlib import import_module
        #   modulename = import_module("modulename")

        import_import_code = ast.ImportFrom(module="importlib",
                                            names=[ast.alias("import_module")])

        module_import_code = ast.Call(func=ast.Name(id="import_module",
                                                    ctx=ast.Load()),
                                      args=[ast.Str(module_name)],
                                      keywords=[])

        assign_imported_module_code = ast.Assign(targets=[ast.Name(id=module_name,
                                                                   ctx=ast.Store())],
                                        value=module_import_code)


        # generate code assigning module.__macros__ to local variable?
        # i.e. for
        #   modmacros = mod.__macros__
        #
        # assign_modmacs_code = ast.Assign(targets=[ast.Name(id="modmacs",
        #                                                    ctx=ast.Store())],
        #                                  value=ast.Attribute( .. ))


        # generate code for
        #   __macros__[name] = module.__macros__[name]
        #                     (modmacros[name]?)

        target_code = ast.Subscript(value=ast.Name(id="__macros__", ctx=ast.Load()),
                                    slice=ast.Index(ast.Str(macro_name)),
                                    ctx=ast.Store())

        value_code = ast.Subscript(value=ast.Attribute(value=ast.Name(id=module_name),
                                                       attr="__macros__",
                                                       ctx=ast.Load()),
                                   slice=ast.Index(ast.Str(macro_name)),
                                   ctx=ast.Load())

        assign_macro_code = ast.Assign(targets=[target_code],
                                       value=value_code)


        # we want:
        #   import_import_code,
        #   assign_imported_module_code, and
        #   assign_macro_code

        # return as tuple?

        return






class IdMacroImport(Macro, SpecialForm):

    def expand(self, element:Element, EC:ExpansionContext):

        raise NotImplementedError()

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()












######################
## STORING COMPILED INSTANCES



macrostore_init_code = [
    # import rmtc.module as __anoky__
    ast.Import([ast.alias(name="rmtc.Module", asname="__aky__")]),
    # __macros__ = {}  (and for id macros and special forms)
    ast.Assign(targets=[ast.Name(id="__macros__", ctx=ast.Store())],
               value=ast.Dict([], [])),
    ast.Assign(targets=[ast.Name(id="__id_macros__", ctx=ast.Store())],
               value=ast.Dict([], [])),
    ast.Assign(targets=[ast.Name(id="__special_forms__", ctx=ast.Store())],
               value=ast.Dict([], []))
]



def generate_macro_store_code(mac_name, mac:Macro):

    # __macros__[mac_name]
    store_as_code = ast.Subscript(value=ast.Name(id="__macros__", ctx=ast.Load()),
                                  slice=ast.Index(ast.Str(mac_name)),
                                  ctx=ast.Store())

    # ~~RHS~~
    #macro_gen_code =

    raise NotImplementedError()

def generate_idmacro_store_code(idmac_name, idmac:Macro):

    store_as_code = ast.Subscript(value=ast.Name(id="__id_macros__", ctx=ast.Load()),
                                  slice=ast.Index(ast.Str(idmac_name)),
                                  ctx=ast.Store())

    #idmacro_gen_code =

def generate_specform_store_code(specform_name, specform:SpecialForm):

    raise NotImplementedError()





def generate_macro_store_codes_from_EC(EC:ExpansionContext):

    macro_store_codes = []

    ECmt = EC.macro_table

    for mac in ECmt:

        mac_store_code = generate_macro_store_code(mac, ECmt[mac])

        macro_store_codes.append(mac_store_code)


    return macro_store_codes




akyimport_init_code = [
    #import rmtc.AnokyImporter as __akyimp__
    ast.Import([ast.alias(name="rmtc.AnokyImporter", asname="__akyimp__")])

]














