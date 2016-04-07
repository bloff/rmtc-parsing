import ast

from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Macro import Macro
from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Generation.Util import expr_wrap
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Seq import Seq





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

        if isinstance(aquote, Form) and aquote[0].code.full_name == "~":

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


        if isinstance(acode, Form) and acode[0].code.full_name == "~":

            assert len(acode) == 2

            return GC.generate(acode[1])


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
                            args=[ast.Str(acode.type), # assuming acode.type is a string
                                  value_code],
                            keywords=[])









