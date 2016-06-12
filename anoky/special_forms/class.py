import ast

from anoky.generation.domain import ExpressionDomain as ExDom, StatementDomain
from anoky.generation.generation_context import GenerationContext
from anoky.generation.util import extend_body
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element, Identifier, Seq
from anoky.syntax.form import Form
from anoky.syntax.util import is_identifier


class Class(SpecialForm):

    HEADTEXT = "class"

    # #(class name (base, classes) body1 body2 ...)

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code


        #name
        spec = acode[1]
        if isinstance(spec.code, Form):
            assert is_identifier(spec.code[0])
            class_name = spec.code[0].code.full_name

            with GC.let(domain=ExDom):
                base_classes_codes = []

                for base_class in spec.code[1:]:
                    extend_body(base_classes_codes, GC.generate(base_class))

        elif isinstance(spec.code, Identifier):
            class_name = spec.code.full_name
            base_classes_codes = []

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