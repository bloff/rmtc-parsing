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
from rmtc.Syntax.Util import is_form, is_identifier


class Container(SpecialForm):


    def generate(self, element:Element, GC:GenerationContext):


        acode = element.code

        head = acode[0].code
        assert isinstance(head, Identifier)
        headtext = head.full_name




##==================MOVE TO SUBCLASSES==========

        assert headtext == "{}"


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

    def generate(self, element:Element, GC:GenerationContext):


        acode = element.code

        if len(acode) is 2 and is_form(acode[1], "for"):

            for_form = acode[1].code

            # list comprehension

            # («[]» (for (in i lst) (f i))) # list compr

            in_el = for_form[1]
            in_el_code = in_el.code

            #with GC.let(domain=ExDom):

            assert is_identifier(in_el, "in")

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


        # (.. )
        if is_form(acode[2], ".."):

            #slice

            raise NotImplementedError()





        #if isinstance(acode[2].code, Literal):
        else:

            with GC.let(domain=ExDom):
                index_code = GC.generate(acode[2])


            return ast.Subscript(base_object_code,
                                 ast.Index(index_code),
                                 ast.Store() if GC.domain == LVDom else ast.Load())

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
