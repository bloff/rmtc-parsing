
#import rmtc.Generation.SpecialForms.SpecialForms as SF
from rmtc.Generation.SpecialForms.SpecialForms import Attribute, Class, Global, Nonlocal
import rmtc.Generation.SpecialForms.Operation as Op
#import rmtc.Generation.SpecialForms.Comparison as Cmp
import rmtc.Generation.SpecialForms.Assign as As
import rmtc.Generation.SpecialForms.Container as Cnt
import rmtc.Generation.SpecialForms.Function as Fn
import rmtc.Generation.SpecialForms.Control as Ctl



default_special_forms_table = {
    "=" : As.Assign(),
    "." : Attribute(),

    # "+" : Op.UnaryAddOp(),
    # "-" : Op.UnarySubOp(),
    "not" : Op.NotOp(),
    "~" : Op.InvertOp(),

    "+" : Op.AddOp(),
    "-" : Op.SubOp(),
    "*" : Op.MultOp(),
    "/" : Op.DivOp(),
    "//" : Op.FloorDivOp(),
    "%" : Op.ModOp(),
    "**" : Op.PowOp(),
    "<<" : Op.LShiftOp(),
    ">>" : Op.RShiftOp(),
    "|" : Op.BitOrOp(),
    "^" : Op.BitXorOp(),
    "&" : Op.BitAndOp(),
    "@" : Op.MatMultOp(),

    "and" : Op.AndOp(),
    "or" : Op.OrOp(),

    "+=" : As.AddAssign(),
    "-=" : As.SubtractAssign(),
    "*=" : As.MultiplyAssign(),
    "/=" : As.DivideAssign(),
    "//=" : As.IntDivideAssign(),
    "%=" : As.ModuloAssign(),
    "**=" : As.PowAssign(),
    "<<=" : As.BitLShiftAssign(),
    ">>=" : As.BitRShiftAssign(),
    "|=" : As.BitOrAssign(),
    "^=" : As.BitXorAssign(),
    "&=" : As.BitAndAssign(),
    "@=" : As.MatMultAssign(),


    "@[]" : Cnt.Subscript(),
    #"[]": Ct.List(),
    #"{}" : Ct.Dict(), #or set?
    #"if" : If(),

    #"raise" : SF.Raise(),
    #"pass" : SF.Pass()

    "def" : Fn.Def(),

    "global" : Global(),
    "nonlocal" : Nonlocal(),

    "class" : Class()
}

container = Cnt.Container()

default_special_forms_table["{}"] = container
default_special_forms_table["[]"] = container

