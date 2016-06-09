import ast

from anoky.generation.domain import ExpressionDomain as ExDom, StatementDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element, Identifier, Seq


class Class(SpecialForm):

    HEADTEXT = "class"

    # #(class name (base, classes) body1 body2 ...)

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code


        #name
        name_element = acode[1]
        assert isinstance(name_element.code, Identifier)
        class_name = name_element.full_name

        #bases
        base_classes_element = acode[2]
        if isinstance(base_classes_element.code, Identifier):
            with GC.let(domain=ExDom):
                base_classes_codes = [ GC.generate(base_classes_element) ]

        else:
            assert isinstance(base_classes_element.code, Seq)

            with GC.let(domain=ExDom):

                base_classes_codes = []

                for base_class in base_classes_element.code:

                    base_classes_codes.append(GC.generate(base_class))


        #keywords

        # "class keyword(arg, value)
        #  A keyword argument to a function call or class definition.
        #  arg is a raw string of the parameter name, value is a node to pass in."

        #starargs

        #kwargs


        body_elements = acode[3:]

        assert len(body_elements) > 0

        body_codes = []

        with GC.let(domain=StatementDomain):
            for body_statement in body_elements:
                extend_body(body_codes, GC.generate(body_statement))







        return ast.ClassDef(name=class_name,
                            bases=base_classes_codes,
                            keywords=[],
                            #starargs
                            #kwargs
                            body=body_codes,
                            decorator_list=[]
                            )