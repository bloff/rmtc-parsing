# import rmtc.Generation.SpecialForms.SpecialForms as SF
from anoky.Expansion.Macros.Quote import Quote
from anoky.Expansion.Macros.Rawmacro import RawMacro, RawSpecialForm
from anoky.Generation.SpecialForms.Comparison import Compare
from anoky.Generation.SpecialForms.Control import If, NotInIsolation
from anoky.Generation.SpecialForms.Function import Return
from anoky.Generation.SpecialForms.Import import MacroImport
from anoky.Generation.SpecialForms.SpecialForms import Attribute, Class, Global, Nonlocal
import anoky.Generation.SpecialForms.Operation as Op
# import anoky.Generation.SpecialForms.Comparison as Cmp
import anoky.Generation.SpecialForms.Assign as As
import anoky.Generation.SpecialForms.Container as Cnt
import anoky.Generation.SpecialForms.Function as Fn
import anoky.Generation.SpecialForms.Control as Ctl
import anoky.Generation.SpecialForms.Import as Imp

default_special_forms_table = {
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
