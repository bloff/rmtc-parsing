import ast

from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Macro import Macro
from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Seq import Seq


class RawMacro(Macro, SpecialForm):

    HEADTEXT = "rawmacro"


    def expand(self, element:Element, EC:ExpansionContext):


        for child in element.code:

            EC.expand(child)




    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        rawspecs = acode[1].code

        macro_name_element = rawspecs[0]

        macro_name = rawspecs[0].code.full_name
        macro_name_safe = "__macro_"+macro_name+"__"


        rawspec_element_param = rawspecs[1].code.full_name

        rawspec_context_param = rawspecs[2].code.full_name




        expand_body_elements = acode[2:]

        expand_body_code = [GC.generate(b) for b in expand_body_elements]
        # The... second-to-last form? of the original element should be
        #  responsible for generating (i.e. should return) code that will
        #  complete the macro expansion;
        #  the final statement executed in an .expand method would actually
        #  be doing the replacing
        #
        final_body_code = expand_body_code[-1]
        # element.replace(final_body_code)
        #ast.Call( ... )


        expand_args_code = ast.arguments(
            args=[ast.arg(arg="self"),
                  ast.arg(arg=rawspec_element_param,
                          annotation=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="Element", ctx=ast.Load())),
                  ast.arg(arg=rawspec_context_param,
                          annotation=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="ExpansionContext", ctx=ast.Load()))],
            kwonlyargs=[], defaults=[], kw_defaults=[]
        )



        expand_method_code = ast.FunctionDef(name="expand",
                                             args=expand_args_code,
                                             body=expand_body_code,
                                             decorator_list=[]
                                             )



        class_body_code = []

        #class_body_code.append(ast.Import([ast.alias(name="rmtc.Module", asname="__aky__")]))

        class_body_code.append(ast.Assign(targets=[ast.Name(id="HEADTEXT",
                                                            ctx=ast.Store())],
                                          value=ast.Str(macro_name)))

        class_body_code.append(expand_method_code)





        classdef_code = ast.ClassDef(
                name=macro_name_safe,
                bases=[ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="Macro", ctx=ast.Load())],
                keywords=[], decorator_list=[],
                body=class_body_code)


        # __macros_macro_name__()
        instantiate_macro_code = ast.Call(func=ast.Name(id=macro_name_safe, ctx=ast.Load()),
                                          args=[], keywords=[])

        # EC.macro_table[macro_name]
        context_code = ast.Subscript(
                value=ast.Attribute(value=ast.Name(id="EC", ctx=ast.Load()),
                                    attr="macro_table", ctx=ast.Load()),
                slice=ast.Index(ast.Str(macro_name)), ctx=ast.Store())


        # __macros__[macro_name] = EC.macro_table[macro_name] = __macros_macro_name__()
        register_macro_code = ast.Assign(targets=[
            ast.Subscript(value=ast.Name(id="__macros__", ctx=ast.Load()),
                          slice=ast.Index(ast.Str(macro_name)),
                          ctx=ast.Store()),
        #    context_code
        ],
                                         value=instantiate_macro_code)


        generated_code = [classdef_code, register_macro_code]

        return generated_code













class RawSpecialForm(Macro, SpecialForm):

    HEADTEXT = "rawspecial"

    def expand(self, element:Element, EC:ExpansionContext):

         for child in element.code:
            EC.expand(child)


    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code



        sf_name_element = acode[1]

        sf_name = sf_name_element.code.full_name
        sf_name_safe = "__specialform_"+sf_name+"__"



        rawexpand = acode[2].code

        # assert isinstance(rawexpand[0].code, Identifier) \
        #     and rawexpand[0].code.full_name == "expand"

        rawexpand_params = rawexpand[1].code

        rawexpand_element_param = rawexpand_params[0].code.full_name

        rawexpand_context_param = rawexpand_params[1].code.full_name


        expand_body_elements = rawexpand[2:]

        expand_body_code = [GC.generate(b) for b in expand_body_elements]
        # The... second-to-last form? of the original element should be
        #  responsible for generating (i.e. should return) code that will
        #  complete the macro expansion;
        #  the final statement executed in an .expand method would actually
        #  be doing the replacing


        expand_args_code = ast.arguments(
            args=[ast.arg(arg="self"),
                  ast.arg(arg=rawexpand_element_param,
                          annotation=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="Element", ctx=ast.Load())),
                  ast.arg(arg=rawexpand_context_param,
                          annotation=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="ExpansionContext", ctx=ast.Load()))],
            kwonlyargs=[], defaults=[], kw_defaults=[]
        )



        expand_method_code = ast.FunctionDef(name="expand",
                                             args=expand_args_code,
                                             body=expand_body_code,
                                             decorator_list=[]
                                             )




        rawgenerate = acode[3].code

        rawgenerate_params = rawgenerate[1].code

        rawgenerate_element_param = rawgenerate_params[0].code.full_name

        rawgenerate_context_param = rawgenerate_params[1].code.full_name


        generate_body_elements = rawgenerate[2:]

        generate_body_code = [GC.generate(b) for b in generate_body_elements]


        generate_args_code = ast.arguments(
            args=[ast.arg(arg="self"),
                  ast.arg(arg=rawgenerate_element_param,
                          annotation=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="Element", ctx=ast.Load())),
                  ast.arg(arg=rawgenerate_context_param,
                          annotation=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="GenerationContext", ctx=ast.Load()))],
            kwonlyargs=[], defaults=[], kw_defaults=[]
        )



        generate_method_code = ast.FunctionDef(name="generate",
                                             args=generate_args_code,
                                             body=generate_body_code,
                                             decorator_list=[]
                                             )


        class_body_code = []

        class_body_code.append(ast.Import([ast.alias(name="rmtc.Module", asname="__aky__")]))

        class_body_code.append(ast.Assign(targets=[ast.Name(id="HEADTEXT",
                                                            ctx=ast.Store())],
                                          value=ast.Str(sf_name)))

        class_body_code.append(expand_method_code)
        class_body_code.append(generate_method_code)




        classdef_code = ast.ClassDef(
                name=sf_name_safe,
                bases=[ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="Macro", ctx=ast.Load()),
                       ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                     attr="SpecialForm", ctx=ast.Load())],
                keywords=[], decorator_list=[],
                body=class_body_code)


        # __specialform_sf_name__()
        instantiate_macro_code = ast.Call(func=ast.Name(id=sf_name_safe, ctx=ast.Load()),
                                          args=[], keywords=[])

        # EC.macro_table[sf_name]
        expansion_context_code = ast.Subscript(
                value=ast.Attribute(value=ast.Name(id="EC", ctx=ast.Load()),
                                    attr="macro_table", ctx=ast.Load()),
                slice=ast.Index(ast.Str(sf_name)), ctx=ast.Store())

        # GC.special_forms[sf_name]
        generation_context_code = ast.Subscript(
                value=ast.Attribute(value=ast.Name(id="GC", ctx=ast.Load()),
                                    attr="special_forms", ctx=ast.Load()),
                slice=ast.Index(ast.Str(sf_name)), ctx=ast.Store())


        # __special_forms__[sf_name] = EC.macro_table[sf_name] \
        #   = GC.special_forms[sf_name] = __specialform_sf_name__()
        register_macro_code = ast.Assign(targets=[
            ast.Subscript(value=ast.Name(id="__special_forms__", ctx=ast.Load()),
                          slice=ast.Index(ast.Str(sf_name)),
                          ctx=ast.Store()),
        #    expansion_context_code,
        #    generation_context_code
        ],
                                         value=instantiate_macro_code)


        generated_code = [classdef_code, register_macro_code]

        return generated_code



















##==============================
#   for reference..
#
# acode = element.code
# ast.Assign(targets=[ast.Name(id="acode", ctx=ast.Store())],
#            value=ast.Attribute(value=ast.Name(id="element",
#                                               ctx=ast.Load()),
#                                attr="code", ctx=ast.Load()))


