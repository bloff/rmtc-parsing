import ast

from rmtc.Generation.Domain import LValueDomain, DeletionDomain, StatementDomain
from rmtc.Generation.GenerationContext import GenerationContext




def ctx_from_domain(GC:GenerationContext):
    if GC.domain == LValueDomain:
        return ast.Store()
    elif GC.domain == DeletionDomain:
        return ast.Del()
    else:
        return ast.Load()


def expr_wrap(code, GC:GenerationContext):
    if GC.domain == StatementDomain:
        return ast.Expr(code)
    return code