

def default_macro_table():
    from anoky.expansion.Macros.quote import Quote
    from anoky.expansion.Macros.rawmacro import RawMacro, RawSpecialForm
    from anoky.generation.special_forms.specialform_import import MacroImport
    return {
        "quote": Quote(),
         "import_macro": MacroImport()
    }


def default_id_macro_table():
    return {}