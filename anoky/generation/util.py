import ast

from anoky.generation.domain import LValueDomain, DeletionDomain, StatementDomain
from anoky.generation.generation_context import GenerationContext




def ctx_from_domain(GC:GenerationContext):
    if GC.domain == LValueDomain:
        return ast.Store()
    elif GC.domain == DeletionDomain:
        return ast.Del()
    else:
        return ast.Load()


def expr_wrap(code, GC:GenerationContext):
    if GC.domain == StatementDomain:
        if hasattr(code, "line_no") and hasattr(code, "col_offset"):
            return ast.Expr(code, line_no=code.line_no, col_offset=code.col_offset)
        else:
            return ast.Expr(code)
    return code