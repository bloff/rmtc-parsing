import ast

from anoky.common.errors import CodeGenerationError
from anoky.common.record import Record
from anoky.expansion.expansion_context import ExpansionContext

from anoky.generation.generation_context import GenerationContext
from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom



from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.literal import Literal
from anoky.syntax.node import Element, Node
from anoky.syntax.seq import Seq
from anoky.syntax.util import is_form


class Generator(object):

    def generate(self, element:Element, context:GenerationContext):

        raise NotImplementedError()



class DefaultGenerator(Generator):
    def generate_unit(self, unit: Node, **kwargs):

        GC, body_nodes = self.begin(**kwargs)

        body_nodes.extend(self.generate_elements(unit, GC))

        return ast.Module(body=body_nodes)

    def generate_elements(self, elements, GC) -> list:
        code = []
        for element in elements:
            new_gens = self.generate_element(element, GC)
            code.extend(new_gens)
        return code

    def generate_element(self, element, GC) -> list:
        element_code = GC.generate(element)
        if isinstance(element_code, list) or isinstance(element_code, tuple):
            return element_code
        else:
            assert isinstance(element_code, ast.AST)
            return [element_code]

    def begin(self, interactive=False, **kwargs) -> (GenerationContext, list):
        from anoky.generation.default_special_forms_table import default_special_forms_table
        context_root_bindings = Record(
            default_generator = self,
            generator = self,
            domain = SDom,
            special_forms = default_special_forms_table,
            interactive=interactive
        )
        context_root_bindings.update(kwargs)

        GC = GenerationContext(**context_root_bindings.__dict__)
        initialization_nodes = []

        # Prepend anoky unit initialization code
        # Something like:
        # import anoky.AnokyImporter as __akyimp__
        # import anoky.Module as __aky__
        # __macros__ = {}
        # __id_macros__ = {}
        # __special_forms__ = {}

        from anoky.generation.special_forms.import_ \
            import macrostore_init_code as mic, akyimport_init_code as aic
        initialization_nodes.extend(aic)
        initialization_nodes.extend(mic)


        return GC, initialization_nodes


    def end(self, py_ast, CG:GenerationContext):
        if CG.interactive:
            return ast.Interactive(body=py_ast)
        else:
            return ast.Module(body=py_ast)




    def generate(self, element, GC:GenerationContext):

        from anoky.generation.util import expr_wrap

        acode = element.code

        if isinstance(acode, Form):

            head = acode.first
            headcode = head.code

            if isinstance(headcode, Identifier) and headcode.full_name in GC.special_forms:

                    hcname = headcode.full_name

                    special_form = GC.special_forms[hcname]

                    generated_code = special_form.generate(element, GC)

                    return generated_code



            else:
                # function call
                # #(func arg1 arg2 arg3 ...)

                func_element = head
                #func_element_code = headcode

                with GC.let(domain=ExDom):
                    func_code = GC.generate(func_element)

                arg_elements = acode[1:]

                args = []
                keywords = []

                for arg_element in arg_elements:
                    arg_element_code = arg_element.code

                    if isinstance(arg_element_code, Form):
                        if is_form(arg_element_code, '='):
                            # keyword argument

                            kw_name = arg_element_code[1].code.full_name

                            with GC.let(domain=ExDom):
                                value_code = GC.generate(arg_element_code[2])

                            keywords.append(ast.keyword(kw_name, value_code))


                        elif is_form(arg_element_code, '*') and len(arg_element_code) == 2:
                            # stared argument - expand as list
                            with GC.let(domain=ExDom):
                                arg_code = GC.generate(arg_element_code[1])
                            args.append(ast.Starred(arg_code, ast.Load()))

                        elif is_form(arg_element_code, '**') and len(arg_element_code) == 2:
                            # double starred argument - expand as kwlist

                            assert len(arg_element_code) == 2
                            # verify no other dblstars already?

                            with GC.let(domain=ExDom):
                                arg_code = GC.generate(arg_element_code[1])

                            keywords.append(ast.keyword(None, arg_code))


                        else:
                            # positional argument

                            with GC.let(domain=ExDom):
                                arg_code = GC.generate(arg_element)

                            args.append(arg_code)

                    else:
                        # arg_element_code not a Form
                        # then generate as expression

                        with GC.let(domain=ExDom):
                                arg_code = GC.generate(arg_element)

                        args.append(arg_code)

                return expr_wrap(ast.Call(func_code, args, keywords), GC)



        if isinstance(acode, Seq):
            seq_codes = []
            for e in acode:
                seq_codes.append(GC.generate(e))

            if GC.domain == LVDom:
                return ast.Tuple(seq_codes, ast.Store())
            elif GC.domain in [ExDom, SDom]:
                return expr_wrap(ast.Tuple(seq_codes, ast.Load()), GC)
            else:
                raise CodeGenerationError(acode.range, "Unexpected seq in domain `%s`." % str(GC.domain))



        if isinstance(acode, Literal):

            if acode.type is str:
                return expr_wrap(ast.Str(acode.value), GC)
            elif acode.type in [int, float]:
                return expr_wrap(ast.Num(acode.value), GC)
            else:
                assert False



        if isinstance(acode, Identifier):

            if acode.full_name == "True":
                return expr_wrap(ast.NameConstant(True), GC)

            elif acode.full_name == "False":
                return expr_wrap(ast.NameConstant(False), GC)

            elif acode.full_name == "None":
                return expr_wrap(ast.NameConstant(None), GC)


            elif GC.domain == LVDom:
                return ast.Name(acode.full_name, ast.Store())

            elif GC.domain == DelDom:
                return ast.Name(acode.full_name, ast.Del())

            else:
                return expr_wrap(ast.Name(acode.full_name, ast.Load()), GC)























