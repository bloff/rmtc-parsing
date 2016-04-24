

def default_macro_table():
    from anoky.special_forms.quote import Quote
    from anoky.special_forms.specialform_import import MacroImport
    return {
        "quote": Quote(),
         "import_macro": MacroImport()
    }


def default_id_macro_table():
    return {}