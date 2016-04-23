import ast

from anoky.expansion.expansion_context import ExpansionContext
from anoky.expansion.macro import Macro
from anoky.generation.domain import ExpressionDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.special_forms.special_forms import SpecialForm
from anoky.generation.util import expr_wrap
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.literal import Literal
from anoky.syntax.node import Element
from anoky.syntax.seq import Seq
from anoky.syntax.util import is_identifier


class Quote(Macro, SpecialForm):

    HEADTEXT = "quote" # or "'"?
    LENGTH = 2

    # def __init__(self):
    #     Macro.__init__(self)

    def expand(self, element:Element, EC:ExpansionContext):

        acode = element.code
        aquote = element.code[1].code

        # expand any escaped code
        Quote.expand_inner_escapes(acode[1], EC)



    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code
        aquote = element.code[1].code

        quote_ast = Quote.generate_quote_ast(acode[1], GC)
        return expr_wrap(quote_ast, GC)


    @staticmethod
    def expand_inner_escapes(element:Element, EC:ExpansionContext):

        aquote = element.code

        if isinstance(aquote, Form) and is_identifier(aquote[0], "~"):

            assert len(aquote) == 2

            EC.expand(aquote[1])

        elif isinstance(aquote, Form) or isinstance(aquote, Seq):
        # or, isinstance(aquote, Node)

            for e in aquote:

                Quote.expand_inner_escapes(e, EC)

        # and that should be it.





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









