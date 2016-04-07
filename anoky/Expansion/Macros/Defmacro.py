import ast

from anoky.Expansion.ExpansionContext import ExpansionContext
from anoky.Expansion.Macro import Macro
from anoky.Generation.GenerationContext import GenerationContext
from anoky.Generation.SpecialForms.SpecialForms import SpecialForm
from anoky.Syntax.Node import Element




class DefMacro(Macro, SpecialForm):

    HEADTEXT = "defmacro"

    # (defmacro (macro_name args*) body_statements+)


    def expand(self, element:Element, EC:ExpansionContext):

        acode = element.code

        sig = acode[1].code

        mac_name = sig[0].code.full_name

        param_names = [p.code.full_name for p in sig[1:]]

        body = [s.code for s in acode[2:]]

        # TODO: implement multistatement definitions
        assert len(body) == 1

        # we are supposed to RUN this statement and take the result
        #  as the replacement, but for now this just uses the code itself
        rcode = body[0]

        mac = Macro(specs=(param_names, rcode))


        EC.macro_table[mac_name] = mac

        #__macros__[mac_name] = mac








    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code
        sig = acode[1].code
        mac_name = sig[0].code.full_name
        param_names = [p.code.full_name for p in sig[1:]]
        body = [s.code for s in acode[2:]]


        params_code = ast.List(elts=[ast.Str(s) for s in param_names],
                               ctx=ast.Load())

        from anoky.Expansion.Macros.Quote import akycode_to_ast
        # rcode_code =

        # __aky__.Macro( ... )
        mac_code = ast.Call(func=ast.Attribute(value=ast.Name(id="__aky__", ctx=ast.Load()),
                                               attr="Macro", ctx=ast.Load()),
                            args=[],
                            keywords=[ast.keyword(arg="specs",
                                                  value=ast.Tuple(elts=[params_code,
                                                                        rcode_code],
                                                                  ctx=ast.Load()))])

        target_code = ast.Subscript(value=ast.Name(id="__macros__", ctx=ast.Load()),
                                    slice=ast.Index(ast.Str(mac_name)),
                                    ctx=ast.Store())

        #
        assign_code = ast.Assign(targets=[target_code],
                                       value=mac_code)


        return assign_code
















class DefIdMacro(Macro, SpecialForm):

    HEADTEXT = "defidmacro"

    def expand(self, element:Element, context:ExpansionContext):

        raise NotImplementedError()

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()











localize_akymodule_import_code = ast.ImportFrom(module="__aky__",
                                                names=[
                            ast.alias(name="Form", asname="__aF__"),
                            ast.alias(name="Seq", asname="__aS__"),
                            ast.alias(name="Identifier", asname="__aI__"),
                            ast.alias(name="Literal", asname="__aL__")])

# aF = __aky__.Form
#
# from __aky__ import Form as aF
#
#

