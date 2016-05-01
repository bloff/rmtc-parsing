import ast

from anoky.expansion.expansion_context import ExpansionContext
from anoky.generation.domain import ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import expr_wrap
from anoky.macros.macro import Macro
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.literal import Literal
from anoky.syntax.node import Element, Node
from anoky.syntax.seq import Seq
from anoky.syntax.util import is_identifier, is_form


class Quote(SpecialForm):

    HEADTEXT = "quote" # or "'"?
    LENGTH = 2

    # def __init__(self):
    #     Macro.__init__(self)

    def expand(self, element:Element, EC:ExpansionContext):
        quote_form = element.code
        for subcode in quote_form[1:]:
            # expand any escaped code
            Quote.expand_inner_escapes(subcode, EC)



    def generate(self, element:Element, GC:GenerationContext):

        assert len(element.code) > 1

        asts = [Quote.generate_quote_ast(subcode, GC) for subcode in element.code[1:]]

        if len(asts) == 1:
            return expr_wrap(asts[0], GC)
        else:
            return expr_wrap(ast.List(asts, ast.Load()), GC)



    @staticmethod
    def expand_inner_escapes(element:Element, EC:ExpansionContext):
        aquote = element.code
        # If we have a quote escape, expand sub-elements
        if is_form(aquote, "~"):
            assert len(aquote) == 2
            EC.expand(aquote[1])

        # otherwise, recurse on nodes, ignore the rest
        elif isinstance(aquote, Node):
            for e in aquote:
                Quote.expand_inner_escapes(e, EC)





    @staticmethod
    def generate_quote_ast(element:Element, GC:GenerationContext):

        # allow passing code instead of element?

        acode = element.code


        if isinstance(acode, Form) and is_identifier(acode[0], "~"):

            assert len(acode) == 2

            with GC.let(domain=ExpressionDomain):
                literal_value = GC.generate(acode[1])

            a = ast.Call(func=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                            attr="force_literal",
                                            ctx=ast.Load()),
                         args=[literal_value],
                         keywords=[])

            return a


        elif isinstance(acode, Form) or isinstance(acode, Seq):

            #return __aky__.Form(*[akycode_to_ast(e) for e in acode])

            children_ast = [Quote.generate_quote_ast(e, GC) for e in acode]

            a = ast.Call(func=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                            attr="Form" if isinstance(acode, Form) else "Seq",
                                            ctx=ast.Load()),
                         args=children_ast,
                         keywords=[])

            return a


        elif isinstance(acode, Identifier):

            return ast.Call(func=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                            attr="Identifier", ctx=ast.Load()),
                            args=[ast.Str(acode.full_name)],
                            keywords=[])

        else:

            assert isinstance(acode, Literal)

            if acode.type is str:
                value_code = ast.Str(acode.value)
            else:
                assert acode.type in [int, float]
                value_code = ast.Num(acode.value)

            return ast.Call(func=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                            attr="Literal", ctx=ast.Load()),
                            args=[ast.Name(id=acode.type.__name__, ctx=ast.Load()), # assuming acode.type is a string
                                  value_code],
                            keywords=[])









