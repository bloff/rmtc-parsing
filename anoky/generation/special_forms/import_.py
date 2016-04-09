import ast

from importlib import import_module

from anoky.common.errors import CodeGenerationError, SyntaxError
from anoky.expansion.expansion_context import ExpansionContext
from anoky.expansion.macro import Macro, IdentifierMacro
from anoky.generation.generation_context import GenerationContext

from anoky.generation.special_forms.special_forms import SpecialForm
from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.lisp_printer import succinct_lisp_printer

from anoky.syntax.node import Element
from anoky.syntax.util import is_form, is_identifier, is_seq


def _get_module_path(element:Element) -> str:
    if not _is_module_path(element):
            raise CodeGenerationError(element.range, "Expected a module path (`a.b.c`) , but found `%s`." % succinct_lisp_printer(element))
    elif is_identifier(element):
        return element.code.full_name # TODO: name mangling?
    elif is_form(element, '.'):
        return _get_module_path(element.code[1]) + "." + _get_module_path(element.code[2])


def _is_module_path(element:Element) -> bool:
    return is_identifier(element) or \
               is_form(element, ".") and \
               len(element.code) == 3 and \
               _is_module_path(element.code[1]) and \
               is_identifier(element.code[2])

def _get_name(element:Element):
    if not is_identifier(element):
        raise SyntaxError(element.range, "Expected a module name , but found `%s`." % succinct_lisp_printer(element))
    return element.code.full_name

class Import(Macro, SpecialForm):
    """
    # One day this will be the code of this special form:

    def-special import:
        syntax:
            `import`( import_element* )

            import_element.alias  :=  `as`( module_path, name )
            import_element.simple :=  module_path
            import_element.node   :=  module_path( module_import* )
            import_element.node   :=  (module_path, module_import*)

            module_path.composite :=  module_path.name
            module_path.simple    :=  name

            module_import.alias  :=  `as`( name, name )
            module_import.simple :=  name

            is_identifier(name)

        def get_path(module_path):
            case composite:
                return get(module_path) + "." + get(name)
            case simple:
                return get(name)

        def get_name(name):
            return str(name)

        generate:
            import_list = []
            import_statements = []

            with-each import_element:
                case simple:
                    imports_list.append
                        ast.alias
                            name = get_path(module_path)
                            asname = None
                case alias:
                    imports_list.append
                        ast.alias
                            name = get_path(module_path)
                            asname = get_name(name)
                case node:
                    to_import_module_name = get_path(module_path)
                    imported_names_from_module = []

                    with-each module_import:
                        case simple:
                            imported_names_from_module.append
                                ast.alias
                                    name = get_name(name)
                                    asname = None
                        case alias:
                            imported_names_from_module.append
                                ast.alias
                                    name = get_name(name[0])
                                    asname = get_name(name[1])

            if len(imports_list) > 0:
                import_statements.append(ast.Import(imports_list))

            return import_statements

    """

    HEADTEXT = "import"
    DOMAIN = SDom

    # (import module_names+)

    def expand(self, element:Element, EC:ExpansionContext):

        return


    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        imports_list = []
        import_statements = []

        with GC.let(domain=ExDom):

            for import_element in acode[1:]:

                if _is_module_path(import_element):
                    to_import_name = _get_module_path(import_element)
                    imports_list.append(ast.alias(name=to_import_name, asname=None))

                elif is_form(import_element.code, "as"):
                    to_import_name = _get_module_path(import_element.code[1])
                    to_import_asname = _get_name(import_element.code[2])

                    imports_list.append(ast.alias(name=to_import_name,
                                                  asname=to_import_asname))
                elif is_form(import_element.code) or is_seq(import_element.code):
                    to_import_module_name = _get_module_path(import_element.code[0])
                    imported_names_from_module = []

                    for to_import_item_element in import_element.code[1:]:

                        if is_identifier(to_import_item_element):
                            to_import_name = _get_name(to_import_item_element)
                            imported_names_from_module.append(ast.alias(name=to_import_name, asname=None))

                        elif is_form(to_import_item_element.code, "as"):
                            to_import_name = _get_name(to_import_item_element.code[1])
                            to_import_asname = _get_name(to_import_item_element.code[2])
                            imported_names_from_module.append(ast.alias(name=to_import_name,
                                                          asname=to_import_asname))
                    import_statements.append(ast.ImportFrom(to_import_module_name, imported_names_from_module, 0))
                else:
                    raise CodeGenerationError(import_element.range, "Special form `import` expected an import specifier but found `%s`."
                                                                    "For example:"
                                                                    "```"
                                                                    "import"
                                                                    "   a.b.c"
                                                                    "   x.y.z as name"
                                                                    "   u.v.w( var1, var2 as v )"
                                                                    "```" % succinct_lisp_printer(import_element))

        if len(imports_list) > 0:
            import_statements.append(ast.Import(imports_list))
        return import_statements




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

        module_name = _get_import_name(acode1[1])

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

        print(EC.macro_table)

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
                                            names=[ast.alias("import_module", None)],
                                            level=0)

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

        value_code = ast.Subscript(value=ast.Attribute(value=ast.Name(id=module_name,
                                                                      ctx=ast.Load()),
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

        return [import_import_code, assign_imported_module_code, assign_macro_code]






class IdMacroImport(Macro, SpecialForm):

    def expand(self, element:Element, EC:ExpansionContext):

        raise NotImplementedError()

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()












######################
## STORING COMPILED INSTANCES



macrostore_init_code = [
    # import anoky.module as __anoky__
    ast.Import([ast.alias(name="anoky.Module", asname="__aky__")]),
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
    #import anoky.AnokyImporter as __akyimp__
    ast.Import([ast.alias(name="anoky.AnokyImporter", asname="__akyimp__")])

]














