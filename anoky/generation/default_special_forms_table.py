
def default_special_forms_table():
    from anoky.fallback import fallback_import
    Op = fallback_import("anoky.special_forms.operation")
    As = fallback_import("anoky.special_forms.assign")
    Cnt = fallback_import("anoky.special_forms.containers")
    Fn = fallback_import("anoky.special_forms.function")
    Ctl = fallback_import("anoky.special_forms.control")
    Imp = fallback_import("anoky.special_forms.specialform_import")

    Quote = fallback_import("anoky.macros.quote", "Quote")
    (RawMacro, RawSpecialForm) = fallback_import("anoky.macros.rawmacro", "RawMacro", "RawSpecialForm")
    Compare = fallback_import("anoky.special_forms.comparison", "Compare")
    (If, NotInIsolation) = fallback_import("anoky.special_forms.control", "If", "NotInIsolation")
    Return = fallback_import("anoky.special_forms.function", "Return")
    (Attribute, Class, Global, Nonlocal) = fallback_import("anoky.special_forms.special_forms", "Attribute", "Class", "Global", "Nonlocal")


    return {
        "=": As.Assign(),
        ".": Attribute(),

        # "+" : Op.UnaryAddOp(),
        # "-" : Op.UnarySubOp(),
        "not": Op.NotOp(),
        "~": Op.InvertOp(),

        "+": Op.AddOp(),
        "-": Op.SubOp(),
        "*": Op.MultOp(),
        "/": Op.DivOp(),
        "//": Op.FloorDivOp(),
        "%": Op.ModOp(),
        "**": Op.PowOp(),
        "<<": Op.LShiftOp(),
        ">>": Op.RShiftOp(),
        "|": Op.BitOrOp(),
        "^": Op.BitXorOp(),
        "&": Op.BitAndOp(),
        "@": Op.MatMultOp(),

        "and": Op.AndOp(),
        "or": Op.OrOp(),

        "+=": As.AddAssign(),
        "-=": As.SubtractAssign(),
        "*=": As.MultiplyAssign(),
        "/=": As.DivideAssign(),
        "//=": As.IntDivideAssign(),
        "%=": As.ModuloAssign(),
        "**=": As.PowAssign(),
        "<<=": As.BitLShiftAssign(),
        ">>=": As.BitRShiftAssign(),
        "|=": As.BitOrAssign(),
        "^=": As.BitXorAssign(),
        "&=": As.BitAndAssign(),
        "@=": As.MatMultAssign(),

        "compare": Compare(),

        "[]": Cnt.List(),
        "{}": Cnt.BraceContainer(),
        # "{}" : Ct.Dict(), #or set?
        "@[]": Cnt.Subscript(),

        "if": If(),
        "else": NotInIsolation(),

        "while": Ctl.While(),
        "for": Ctl.For(),

        "raise": Ctl.Raise(),
        "try": Ctl.Try(),
        "assert": Ctl.Assert(),
        "pass": Ctl.Pass(),


        "return": Return(),

        "with": Ctl.With(),

        "def": Fn.Def(),

        "global": Global(),
        "nonlocal": Nonlocal(),

        "class": Class(),

        "import": Imp.Import(),
        "importmacro": Imp.MacroImport(),
        "quote": Quote(),
        "rawmacro": RawMacro(),
        "rawspecial": RawSpecialForm()

    }

# container = Cnt.Container()

# default_special_forms_table["{}"] = container
# default_special_forms_table["[]"] = container
