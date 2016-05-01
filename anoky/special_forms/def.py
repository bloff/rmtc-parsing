import ast

from anoky.generation.domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element


# def
# lambda
# call?
# return
#
# yield



class Def(SpecialForm):

# #(def (fname argform*) body_statement+)
# where each argform is one of
#   arg
#   (type, arg)
#   (= arg initializer)
#   (type, (= arg initializer))
#
#   (* arg)
#   (** arg)
#
#   (type, (* arg))
#   (type, (** arg))

    HEADTEXT = "def"
    DOMAIN = SDom

    def generate(self, element:Element, GC:GenerationContext):


        acode = element.code

        func_specs = acode[1].code

        assert isinstance(func_specs[0].code, Identifier)

        function_name = func_specs[0].code.full_name

        arguments = self.generate_arguments(*func_specs[1:], GC=GC)

        body_elements = acode[2:]

        body_code = []
        with GC.let(domain=SDom):
            for body_element in body_elements:
                body_code.append(GC.generate(body_element))

        decorators_code = []

        returns_code = None

        return ast.FunctionDef(function_name, arguments, body_code,
                               decorators_code, returns_code)



    def generate_arguments(self, *params, GC:GenerationContext):

        poststar = False

        argslist = []
        kwonlyargslist = []
        vararg = None
        kwarg = None
        defaults = []
        kw_defaults = []

        for param_element in params:

            param_code = param_element.code

            if isinstance(param_code, Identifier) and param_code.full_name == '*':

                poststar = True


            elif isinstance(param_code, Identifier):
                # arg

                arg_object = ast.arg(arg=param_code.full_name, annotation=None)

                #if self.vararg is not None or self.kwarg is not None:
                if poststar:
                    # argument is keyword-only

                    kwonlyargslist.append(arg_object)

                else:

                    assert not poststar

                    argslist.append(arg_object)



            elif isinstance(param_code, Form):

                #assert isinstance(param_code[0].code, Identifier) and
                if param_code[0].code.full_name == '=':
                    # (= arg initializer)

                    assert len(param_code) == 3

                    with GC.let(domain=ExDom):
                        initializer_code = GC.generate(param_code[2])

                    assert isinstance(param_code[1].code, Identifier)
                    arg_object = ast.arg(arg=param_code[1].code.full_name, annotation=None)

                    if poststar:

                        kwonlyargslist.append(arg_object)
                        kw_defaults.append(initializer_code)

                    else:

                        argslist.append(arg_object)
                        defaults.append(initializer_code)


                elif param_code[0].code.full_name == '*':
                    # (* arg)

                    #assert isinstance(param_code[1].code, Identifier)

                    starg = ast.arg(arg=param_code[1].code.full_name, annotation=None)

                    assert vararg is None

                    vararg = starg

                    poststar = True




                else:
                    assert param_code[0].code.full_name == '**'
                    # (** arg)

                    #assert isinstance(param_code[1].code, Identifier)

                    dblstarg = ast.arg(arg=param_code[1].code.full_name, annotation=None)

                    assert kwarg is None

                    kwarg = dblstarg

                    poststar = True





            else:
                # (type, arg)
                # (type, (= arg initializer))
                # (type, (* arg))
                # (type, (** arg))

                #assert isinstance(param_code, Seq)

                annotation_element = param_code[0]

                # if isinstance(annotation_code, Identifier):
                #     annotation = ast.Name(id=annotation_code.full_name, ctx=ast.Load())
                #
                # elif isinstance(annotation_code, Literal):
                #     annotation =

                with GC.let(domain=ExDom):
                    annotation_code = GC.generate(annotation_element)

                # and now the arg itself..

                param_code = param_code[1].code

                if isinstance(param_code, Identifier):

                    #assert param_code.full_name != '*'

                    arg_object = ast.arg(arg=param_code.full_name, annotation=annotation_code)

                    if poststar:

                        kwonlyargslist.append(arg_object)

                    else:

                        argslist.append(arg_object)


                else:

                    assert isinstance(param_code, Form)

                    #assert isinstance(param_code[0].code, Identifier) and
                    if param_code[0].code.full_name == '=':
                        # (= arg initializer)

                        assert len(param_code) == 3

                        with GC.let(domain=ExDom):
                            initializer_code = GC.generate(param_code[2])

                        assert isinstance(param_code[1].code, Identifier)
                        arg_object = ast.arg(arg=param_code[1].full_name, annotation=annotation_code)

                        if poststar:

                            kwonlyargslist.append(arg_object)
                            kw_defaults.append(initializer_code)

                        else:

                            argslist.append(arg_object)
                            defaults.append(initializer_code)





                    elif param_code[0].code.full_name == '*':
                        # (* arg)

                        #assert isinstance(param_code[1].code, Identifier)

                        starg = ast.arg(arg=param_code[1].code.full_name, annotation=annotation_code)

                        assert vararg is None

                        vararg = starg

                        poststar = True




                    else:
                        assert param_code[0].code.full_name == '**'
                        # (** arg)

                        #assert isinstance(param_code[1].code, Identifier)

                        dblstarg = ast.arg(arg=param_code[1].code.full_name, annotation=annotation_code)

                        assert kwarg is None

                        kwarg = dblstarg

                        poststar = True





        return ast.arguments(args=argslist, vararg=vararg, kwonlyargs=kwonlyargslist,
                             kwarg=kwarg, defaults=defaults, kw_defaults=kw_defaults)











