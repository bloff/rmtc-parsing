
def default_special_forms_table():
    from anoky.fallback import fallback_import
    operators = fallback_import("anoky.special_forms.operators")
    assign = fallback_import("anoky.special_forms.assign")
    containers = fallback_import("anoky.special_forms.containers")

    Def = fallback_import("anoky.special_forms.def", "Def")
    Try = fallback_import("anoky.special_forms.try", "Try")
    Raise = fallback_import("anoky.special_forms.raise", "Raise")
    Assert = fallback_import("anoky.special_forms.assert", "Assert")
    Pass = fallback_import("anoky.special_forms.pass", "Pass")
    Return = fallback_import("anoky.special_forms.return", "Return")
    Yield = fallback_import("anoky.special_forms.yield", "Yield")
    Break = fallback_import("anoky.special_forms.break", "Break")
    Continue = fallback_import("anoky.special_forms.continue", "Continue")



    While = fallback_import("anoky.special_forms.while", "While")
    With = fallback_import("anoky.special_forms.with", "With")
    For = fallback_import("anoky.special_forms.for", "For")

    NotInIsolation = fallback_import("anoky.special_forms.not_in_isolation", "NotInIsolation")

    # ExpectPreviousForm = fallback_import("anoky.special_forms.expect_previous_form", "ExpectPreviousForm")


    Import = fallback_import("anoky.special_forms.import", "Import")
    ImportMacro = fallback_import("anoky.special_forms.import", "ImportMacro")


    Quote = fallback_import("anoky.special_forms.quote", "Quote")
    (RawMacro, RawSpecialForm) = fallback_import("anoky.macros.rawmacro", "RawMacro", "RawSpecialForm")
    Compare = fallback_import("anoky.special_forms.comparison", "Compare")
    If = fallback_import("anoky.special_forms.if", "If")

    Attribute = fallback_import("anoky.special_forms.attribute", "Attribute")
    Class = fallback_import("anoky.special_forms.class", "Class")
    (Global, Nonlocal) = fallback_import("anoky.special_forms.scope_statement", "Global", "Nonlocal")


    return {
        "=": assign.Assign(),
        ".": Attribute(),

        # "+" : Op.UnaryAddOp(),
        # "-" : Op.UnarySubOp(),
        "not": operators.NotOp(),

        "~": operators.InvertOp(),

        "+": operators.AddOp(),
        "-": operators.SubOp(),
        "*": operators.MultOp(),
        "/": operators.DivOp(),
        "//": operators.FloorDivOp(),
        "%": operators.ModOp(),
        "**": operators.PowOp(),
        "<<": operators.LShiftOp(),
        ">>": operators.RShiftOp(),
        "|": operators.BitOrOp(),
        "^": operators.BitXorOp(),
        "&": operators.BitAndOp(),
        "@": operators.MatMultOp(),

        "and": operators.AndOp(),
        "or": operators.OrOp(),

        "+=": assign.AddAssign(),
        "-=": assign.SubtractAssign(),
        "*=": assign.MultiplyAssign(),
        "/=": assign.DivideAssign(),
        "//=": assign.IntDivideAssign(),
        "%=": assign.ModuloAssign(),
        "**=": assign.PowAssign(),
        "<<=": assign.BitLShiftAssign(),
        ">>=": assign.BitRShiftAssign(),
        "|=": assign.BitOrAssign(),
        "^=": assign.BitXorAssign(),
        "&=": assign.BitAndAssign(),
        "@=": assign.MatMultAssign(),

        "compare": Compare(),

        "[]": containers.List(),
        "{}": containers.BraceContainer(),
        # "{}" : Ct.Dict(), #or set?
        "@[]": containers.Subscript(),

        "if": If(),
        "else": NotInIsolation(),
        "elif": NotInIsolation(),

        "while": While(),
        "for": For(),

        "raise": Raise(),
        "try": Try(),
        "assert": Assert(),
        "pass": Pass(),


        "return": Return(),
        "yield": Yield(),
        "break": Break(),
        "continue": Continue(),

        "with": With(),

        "def": Def(),

        "global": Global(),
        "nonlocal": Nonlocal(),

        "class": Class(),

        "import": Import(),
        "import_macro": ImportMacro(),
        "quote": Quote(),
        "rawmacro": RawMacro(),
        "rawspecial": RawSpecialForm()

    }

# container = Cnt.Container()

# default_special_forms_table["{}"] = container
# default_special_forms_table["[]"] = container
