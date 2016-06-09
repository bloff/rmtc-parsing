import ast

from anoky.generation.domain import StatementDomain as SDom, ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element
from anoky.syntax.util import is_form


class With(SpecialForm):

    HEADTEXT = "with"
    DOMAIN = SDom

    # (with ((f) (as x y)) body+

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        context_element = acode[1]
        context_element_code = context_element.code
        assert len(context_element_code) > 0

        with_items = []

        with GC.let(domain=ExpressionDomain):

            for ctxel in context_element_code:


                if is_form(ctxel.code, "as"):

                    ctxelcode = ctxel.code

                    assert len(ctxel) == 3
                    ctx_expr = GC.generate(ctxelcode[1])

                    opt_var = GC.generate(ctxelcode[2])

                    with_items.append(ast.withitem(context_expr=ctx_expr,
                                                   optional_vars=opt_var))

                else:

                    ctx_expr = GC.generate(ctxel)

                    with_items.append(ast.withitem(context_expr=ctx_expr,
                                                   optional_vars=None))

            body_items = []

            with GC.let(domain=SDom):

                for bodyel in acode[2:]:
                    extend_body(body_items, GC.generate(bodyel))


        return ast.With(items=with_items,
                        body=body_items)