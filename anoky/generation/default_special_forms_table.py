# import rmtc.Generation.SpecialForms.SpecialForms as SF
from anoky.expansion.Macros.quote import Quote
from anoky.expansion.Macros.rawmacro import RawMacro, RawSpecialForm
from anoky.generation.special_forms.comparison import Compare
from anoky.generation.special_forms.control import If, NotInIsolation
from anoky.generation.special_forms.function import Return
from anoky.generation.special_forms.import_ import MacroImport
from anoky.generation.special_forms.special_forms import Attribute, Class, Global, Nonlocal
import anoky.generation.special_forms.operation as Op
# import anoky.generation.special_forms.Comparison as Cmp
import anoky.generation.special_forms.assign as As
import anoky.generation.special_forms.containers as Cnt
import anoky.generation.special_forms.function as Fn
import anoky.generation.special_forms.control as Ctl
import anoky.generation.special_forms.import_ as Imp

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
