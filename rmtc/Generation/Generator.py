import ast

from rmtc.Common.Record import Record

#from rmtc.Generation.SpecialForms.SpecialForms import *
from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom



from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element, Node
from rmtc.Syntax.Seq import Seq


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
        for element in unit:
            body_nodes.append(GC.generate(element))

        return ast.Module(body=body_nodes)




    def generate(self, element, GC:GenerationContext):

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
                        if isinstance(arg_element_code[0].code, Identifier) \
                            and arg_element_code[0].code.full_name == '=':
                            # keyword argument

                            kw_name = arg_element_code[1].code.full_name

                            with GC.let(domain=ExDom):
                                value_code = GC.generate(arg_element_code[2])

                            keywords.append(ast.keyword(kw_name, value_code))


                        elif isinstance(arg_element_code[0].code, Identifier) \
                            and arg_element_code[0].code.full_name == '*':
                            # starred argument

                            assert len(arg_element_code) == 2
                            # verify no other stars already?

                            with GC.let(domain=ExDom):
                                arg_code = GC.generate(arg_element_code[1])

                            args.append(ast.Starred(arg_code, ast.Load()))



                        elif isinstance(arg_element_code[0].code, Identifier) \
                            and arg_element_code[0].code.full_name == '**':
                            # double starred argument

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

                        with GC.let(domain=ExDom):
                                arg_code = GC.generate(arg_element)

                        args.append(arg_code)




                return ast.Call(func_code, args, keywords)



        if isinstance(acode, Seq):

            # are seqs ever not tuples

            seq_codes = []
            with GC.let(domain=ExDom):
                # does var scope extend outside with block?
                #seq_codes = [GC.generate(e) for e in acode]
                for e in acode:
                    seq_codes.append(GC.generate(e))

            if GC.domain == LVDom:
                return ast.Tuple(seq_codes, ast.Store())

            else:
                return ast.Tuple(seq_codes, ast.Load())



        if isinstance(acode, Literal):

            if acode.type == "STRING(PLACEHOLDER)":
                return ast.Str(acode.value)

            elif acode.type in ["INT(PLACEHOLDER)", ]:
            # .. acode.type is numeric
                return ast.Num(acode.value)



        if isinstance(acode, Identifier):

            if acode.full_name == "True":
                return ast.NameConstant(True)

            elif acode.full_name == "False":
                return ast.NameConstant(False)

            elif acode.full_name == "None":
                return ast.NameConstant(None)


            elif GC.domain == LVDom:
                return ast.Name(acode.full_name, ast.Store())

            elif GC.domain == DelDom:
                return ast.Name(acode.full_name, ast.Del())

            else:
                return ast.Name(acode.full_name, ast.Load())

























