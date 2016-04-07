import ast

from anoky.common.errors import CodeGenerationError
from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom
from anoky.generation.generation_context import GenerationContext
from anoky.generation.generator import Generator

#from anoky.generation.special_forms.AugAssign import *


from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element


##=====================
from anoky.syntax.seq import Seq


##=====================




class SpecialForm(Generator):

    HEADTEXT = None
    LENGTH = None
    DOMAIN = None

    def generate(self, element:Element, GC:GenerationContext):
        raise NotImplementedError()

    def precheck(self, element:Element, GC:GenerationContext):
        acode = element.code
        # assert isinstance(acode[0], Identifier) ?
        if self.LENGTH:
            if isinstance(self.LENGTH, int):
                # if a number
                if self.LENGTH != len(acode):
                    raise CodeGenerationError(element.range, "Special form `%s` expected %d arguments, got %d."%(self.HEADTEXT, self.LENGTH, len(acode)))
            else:
                # if range or list
                if len(acode) not in self.LENGTH:
                    valid_numbers = ", ".join(self.LENGTH[:-1]) + " or " + self.LENGTH[-1]
                    raise CodeGenerationError(element.range, "Special form `%s` expected %d arguments, got %d."%(self.HEADTEXT, valid_numbers, len(acode)))
        if self.DOMAIN:
            if isinstance(self.DOMAIN, str):
                if self.DOMAIN != GC.domain:
                    raise CodeGenerationError(element.range, "Special form `%s` appeared in domain '%s', but can only appear in domain '%s'."%(self.HEADTEXT, GC.domain, self.DOMAIN))
            else:
                # if list or set
                if GC.domain not in self.DOMAIN:
                    valid_domains = "'"+ "', '".join(self.LENGTH[:-1]) + " or '" + self.LENGTH[-1] + "'"
                    raise CodeGenerationError(element.range, "Special form `%s` appeared in domain '%s', but can only appear in domains ."%(self.HEADTEXT, GC.domain, valid_domains))



##=================================
#
# import
#
# class
#
#





class Attribute(SpecialForm):

# #(. base_object attribute_name)

    HEADTEXT = "."
    LENGTH = 3

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain=ExDom):
            base_object_code = GC.generate(acode[1])

        att_name = acode[2].code.full_name

        if GC.domain == LVDom:
            return ast.Attribute(base_object_code, att_name, ast.Store())

        elif GC.domain == DelDom:
            return ast.Attribute(base_object_code, att_name, ast.Del())

        else:
            return ast.Attribute(base_object_code, att_name, ast.Load())






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

        with GC.let(domain=SDom):
            for body_statement in body_elements:

                body_codes.append(GC.generate(body_statement))







        return ast.ClassDef(name=class_name,
                            bases=base_classes_codes,
                            keywords=[],
                            #starargs
                            #kwargs
                            body=body_codes,
                            decorator_list=[]
                            )









class ScopeStatement(SpecialForm):

    DOMAIN = SDom

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        assert len(acode) > 1

        var_names = []

        for id_el in acode[1:]:

            assert isinstance(id_el.code, Identifier)

            var_names.append(id_el.code.full_name)

        return self.SCOPE(var_names)


class Global(ScopeStatement):

    HEADTEXT = "global"

    SCOPE = ast.Global


class Nonlocal(ScopeStatement):

    HEADTEXT = "nonlocal"

    SCOPE = ast.Nonlocal






