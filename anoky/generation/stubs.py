import ast

from anoky.expansion.expansion_context import ExpansionContext
from anoky.macros.macro import Macro
from anoky.special_forms.special_form import SpecialForm

macrostore_init_code = [
    # import anoky.module as __anoky__
    ast.Import([ast.alias(name="anoky.module", asname="__aky__")]),
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
    #import anoky.importer as __akyimp__
    ast.Import([ast.alias(name="anoky.importer", asname="__akyimp__")])

]