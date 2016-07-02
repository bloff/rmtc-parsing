import ast
import importlib
import traceback
from importlib import import_module

from anoky.common.errors import CodeGenerationError, SyntaxError
from anoky.expansion.expansion_context import ExpansionContext
from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom
from anoky.generation.generation_context import GenerationContext
from anoky.macros.macro import Macro
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax.lisp_printer import succinct_lisp_printer
from anoky.syntax.node import Element
from anoky.syntax.util import is_form, is_identifier, is_seq


# todo: relative import (import ..bla)

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

            module_import.alias   :=  `as`( name, name )
            module_import.simple  :=  name

            is-identifier(name)

        def get-path(module_path):
            case composite:
                return get_path(module_path) + "." + get_name(name)
            case simple:
                return get_name(name)

        def get-name(name):
            return str(name)

        generate:
            imports_list = []
            import_statements = []

            with-each import_element:
                case simple:
                    imports_list.append
                        ast.alias
                            name = get-path(module_path)
                            asname = None
                case alias:
                    imports_list.append
                        ast.alias
                            name = get-path(module_path)
                            asname = get-name(name)
                case node:
                    to_import_module_name = get-path(module_path)
                    imported_names_from_module = []

                    with-each module_import:
                        case simple:
                            imported_names_from_module.append
                                ast.alias
                                    name = get-name(name)
                                    asname = None
                        case alias:
                            imported_names_from_module.append
                                ast.alias
                                    name = get-name(name[0])
                                    asname = get-name(name[1])

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







class MetaImport(Macro, SpecialForm):

    HEADTEXT = "meta_import"
    DOMAIN = SDom

    # (import module_names+)

    def expand(self, element:Element, EC:ExpansionContext):

        acode = element.code

        for import_element in acode[1:]:

            if is_identifier(import_element):
                to_import_name = import_element.code.full_name
                try:
                    module = importlib.import_module(to_import_name)
                    macros = module.__macros__
                    EC.macros.update(macros)
                    id_macros = module.__id_macros__
                    EC.id_macros.update(id_macros)
                    special_forms = module.__special_forms__
                    EC.special_forms.update(special_forms)
                except Exception as e:
                    traceback.print_exc()
                    raise CodeGenerationError(import_element.range,
                                              "Failed to meta-import module `%s`." % to_import_name)

            else:
                raise CodeGenerationError(import_element.range,
                                          "Special form `meta-import` expected a module pathbut found `%s`." % succinct_lisp_printer(
                                              import_element))

        return


    def generate(self, element:Element, GC:GenerationContext):

        return []
















