import ast

from rmtc.Generation.GenerationContext import GenerationContext
from rmtc.Generation.SpecialForms.SpecialForms import SpecialForm
from rmtc.Generation.Domain import StatementDomain as SDom,\
    ExpressionDomain as ExDom, LValueDomain as LVDom, DeletionDomain as DelDom
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Identifier import Identifier

from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Element




# list, tuple?, dict
# comprehensions
# subscription
#
# del



# #([] ... )

# #({} ... )



# («[]» (for (in i lst) (f i))) # list compr
# («[]» something else) # list
#
# («{}» (for (in i lst) expr)) # set compr
# («{}» something else) # set
#
# («{}» (for (in i lst) (= expr expr))) # dict compr
# («{}» (= something else)) # dict






class Container(SpecialForm):


    def generate(self, element:Element, GC:GenerationContext):


        acode = element.code

        head = acode[0].code
        assert isinstance(head, Identifier)
        headtext = head.full_name

        if headtext == "[]":


            #raise NotImplementedError()

            # "ast.List(elts, ctx)
            #  A list or tuple. elts holds a list of nodes representing the elements.
            #  ctx is Store if the container is an assignment target (i.e. (x,y)=pt),
            #  and Load otherwise."


            if len(acode) is 2 and isinstance(acode[1].code, Form) \
                and isinstance(acode[1].code[0].code, Identifier) \
                and acode[1].code[0].code.full_name == "for":

                for_form = acode[1].code

                # list comprehension

# («[]» (for (in i lst) (f i))) # list compr


                in_el = for_form[1]
                in_el_code = in_el.code

                #with GC.let(domain=ExDom):

                assert isinstance(in_el_code[0].code, Identifier) \
                    and in_el_code[0].code.full_name == "in"

                target_element = in_el_code[1]
                iter_element = in_el_code[2]

                with GC.let(domain=LVDom):
                    target_code = GC.generate(target_element)

                with GC.let(domain=ExDom):
                    iter_code = GC.generate(iter_element)



                generators = [ ast.comprehension(target=target_code,
                                                 iter=iter_code,
                                                 ifs=[]) ]


                to_evaluate_element = for_form[2]

                with GC.let(domain=ExDom):

                    to_evaluate_code = GC.generate(to_evaluate_element)


                return ast.ListComp(to_evaluate_code, generators)


            else:

                els = self.generate_as_expressions(GC, *acode[1:])

                if GC.domain == LVDom:
                    return ast.List(els, ast.Store())
                return self.expr_wrap(ast.List(els, ast.Load()), GC)




        else:
            assert headtext == "{}"

            #
            # "class Set(elts)
            #  A set. elts holds a list of nodes representing the elements."
            #
            # "class Dict(keys, values)
            #  A dictionary. keys and values hold lists of nodes with
            #  matching order (i.e. they could be paired with zip()).
            #
            #  Changed in version 3.5: It is now possible to expand one
            #  dictionary into another, as in {'a': 1, **d}. In the AST, the
            #  expression to be expanded (a Name node in this example) goes in
            #  the values list, with a None at the corresponding position in keys."

# («{}» (for (in i lst) expr)) # set compr
# («{}» something else) # set
#
# («{}» (for (in i lst) (= expr expr))) # dict compr
# («{}» (= something else)) # dict


            if len(acode) is 2 and isinstance(acode[1].code, Form) \
                and isinstance(acode[1].code[0].code, Identifier) \
                and acode[1].code[0].code.full_name == "for":

                raise NotImplementedError()


            else:

                if len(acode) is 1:

                    return ast.Dict([], [])


                if isinstance(acode[1].code, Form) \
                    and isinstance(acode[1].code[0].code, Identifier) \
                    and acode[1].code[0].code.full_name == "=":

                    #dict

                    keys = []
                    values = []

                    #with GC.let(domain=ExDom):

                    for kvpair_el in acode[1:]:

                        kvpair = kvpair_el.code

                        key_code = GC.generate(kvpair[1])
                        value_code = GC.generate(kvpair[2])

                        keys.append(key_code)
                        values.append(value_code)

                    return ast.Dict(keys, values)

                else:

                    #set

                    el_codes = self.generate_as_expressions(GC, *acode[1:])

                    return ast.Set(el_codes)





    @staticmethod
    def generate_as_expressions(GC:GenerationContext, *args:Element):

        expr_codes = []

        with GC.let(domain=ExDom):

            for arg_element in args:
                expr_codes.append(GC.generate(arg_element))

        return expr_codes






class List(Container):

    HEADTEXT = "[]"

#     # #([] ...)
#     #
#
#     def generate(self, element:Element, GC:GenerationContext):
#
#         raise NotImplementedError()
#
#
#

class Set(Container):

    HEADTEXT = "{}"
#
#     def generate(self, element:Element, GC:GenerationContext):
#
#         raise NotImplementedError()


class Dict(Container):

    HEADTEXT = "{}"





class Comprehension(Container):

    LENGTH = 2




class ListComp(Comprehension):

    HEADTEXT = "[]"


class SetComp(Comprehension):

    HEADTEXT = "{}"


class DictComp(Comprehension):

    HEADTEXT = "{}"






















class Subscript(SpecialForm):

# #(@[] base_object id_or_seq)  ??
#

    HEADTEXT = "@[]"

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        with GC.let(domain=ExDom):
            base_object_code = GC.generate(acode[1])

        if isinstance(acode[2].code, Literal):

            if GC.domain == LVDom:
                return ast.Subscript(base_object_code, ast.Index(GC.generate(acode[2])), ast.Store())

            # if GC.domain == DelDom
            # else

        #elif slice

        #else extslice



















class Delete(SpecialForm):

    HEADTEXT = "del"
    DOMAIN = SDom

    # (del (seq, to, delete))

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()
