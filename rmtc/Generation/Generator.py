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

        from rmtc.Generation.SpecialForms.SpecialForms import Assign

        special_forms = {"=":Assign()}

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
                raise NotImplementedError()

                #func_code = GC.generate(headcode[0])

                #args_code = [GC.generate(a) for a in headcode[1:]]

                #return ast.Call(func_code, args_code, )



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

























