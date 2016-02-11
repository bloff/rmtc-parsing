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

                raise NotImplementedError()

                # list comprehension

            else:

                els = []


                for el in acode[1:]:


                    el_code = GC.generate(el)

                    els.append(el_code)

                if GC.domain == LVDom:
                    return ast.List(els, ast.Store())
                return ast.List(els, ast.Load())




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

                    el_codes = []

                    for item in acode[1:]:

                        item_code = GC.generate(item)

                        el_codes.append(item_code)

                    return ast.Set(el_codes)






# class List(SpecialForm):
#
#     # #([] ...)
#     #
#
#     def generate(self, element:Element, GC:GenerationContext):
#
#         raise NotImplementedError()
#
#
#
# class Set(SpecialForm):
#
#     def generate(self, element:Element, GC:GenerationContext):
#
#         raise NotImplementedError()


#class Dict










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





def ListComp(SpecialForm):

    raise NotImplementedError()

















class Delete(SpecialForm):

    HEADTEXT = "del"
    DOMAIN = SDom

    # (del (seq, to, delete))

    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()
