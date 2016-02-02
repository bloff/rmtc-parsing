
#import rmtc.Generation.SpecialForms.SpecialForms as SF
from rmtc.Generation.SpecialForms.SpecialForms import Assign, Attribute
import rmtc.Generation.SpecialForms.Operation as Op
import rmtc.Generation.SpecialForms.AugAssign as Aug
import rmtc.Generation.SpecialForms.Container as Ct



default_special_forms_table = {
    "=" : Assign(),
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

    "+=" : Aug.AddAssign(),
    "-=" : Aug.SubtractAssign(),
    "*=" : Aug.MultiplyAssign(),
    "/=" : Aug.DivideAssign(),
    "//=" : Aug.IntDivideAssign(),
    "%=" : Aug.ModuloAssign(),
    "**=" : Aug.PowAssign(),
    "<<=" : Aug.BitLShiftAssign(),
    ">>=" : Aug.BitRShiftAssign(),
    "|=" : Aug.BitOrAssign(),
    "^=" : Aug.BitXorAssign(),
    "&=" : Aug.BitAndAssign(),
    "@=" : Aug.MatMultAssign(),


    "@[]" : Ct.Subscript(),
    #"[]": Ct.List(),
    #"{}" : Ct.Dict(), #or set?
    #"if" : If(),

    #"raise" : SF.Raise(),
    #"pass" : SF.Pass()
}



