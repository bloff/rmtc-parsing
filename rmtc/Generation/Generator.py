import ast

from rmtc.Common.Record import Record
from rmtc.Expansion.ExpansionContext import ExpansionContext

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom



from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element, Node
from rmtc.Syntax.Seq import Seq
from rmtc.Syntax.Util import is_form


class Generator(object):

    def generate(self, element:Element, context:GenerationContext):

        raise NotImplementedError()



class DefaultGenerator(Generator):


    def generate_unit(self, unit:Node, **kwargs):

        assert(isinstance(unit, Node))

        # from rmtc.Generation.SpecialForms.SpecialForms import Assign, \
        #     Attribute
        # from rmtc.Generation.SpecialForms.AugAssign import AddAssign
        # from rmtc.Generation.SpecialForms.Operation import AddOp

        from rmtc.Generation.DefaultSpecialFormsTable import default_special_forms_table
        special_forms = default_special_forms_table


        context_root_bindings = Record(
            default_generator = self,
            generator = self,
            domain = SDom,
            special_forms = special_forms
        )
        context_root_bindings.update(kwargs)

        GC = GenerationContext(**context_root_bindings.__dict__)

        body_nodes = []


        from rmtc.Generation.SpecialForms.Import \
            import macrostore_init_code as mic, akyimport_init_code as aic
        body_nodes.extend(aic)
        body_nodes.extend(mic)


        for element in unit:

            element_code = GC.generate(element)

            if isinstance(element_code, list) or isinstance(element_code, tuple):
                body_nodes.extend(element_code)

            else:

                assert isinstance(element_code, ast.AST)

                body_nodes.append(element_code)





        return ast.Module(body=body_nodes)




    def generate(self, element, GC:GenerationContext):

        from rmtc.Generation.Util import expr_wrap

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

            # are seqs ever not tuples

            seq_codes = []

            # NEED TO FIX THIS

            # there's a better way to do this probably
            if GC.domain == LVDom:
                with GC.let(domain=LVDom):
                    for e in seq_codes:
                        seq_codes.append(GC.generate(e))
                return ast.Tuple(seq_codes, ast.Store())

            with GC.let(domain=ExDom):
                # does var scope extend outside with block?
                #seq_codes = [GC.generate(e) for e in acode]
                for e in acode:
                    seq_codes.append(GC.generate(e))



            # elif GC.domain == SDom:


            return expr_wrap(ast.Tuple(seq_codes, ast.Load()), GC)



        if isinstance(acode, Literal):

            if acode.type == "STRING(PLACEHOLDER)":
                return expr_wrap(ast.Str(acode.value), GC)

            elif acode.type in ["INT(PLACEHOLDER)", ]:
            # .. acode.type is numeric
                return expr_wrap(ast.Num(acode.value), GC)



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























