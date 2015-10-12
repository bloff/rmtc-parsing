from Common.Errors import ArrangementError
from Syntax.Node import Node, Element
from Syntax.Punctuator import Punctuator
from Syntax.PreTuple import PreTuple
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule


# Takes something like
# H     a b,  c d ;   e f, g, h :    x y, z
# and outputs
# H ( ((a b) (c d)) ((e f) g h) )  ((x y) z)
# where H is the first punctuator.skip_count elements

class DefaultPunctuation(ArrangementRule):

    def __init__(self):
        ArrangementRule.__init__(self, "Default Punctuation")

    def applies(self, element:Element):
        return isinstance(element.code, Punctuator)

    def apply(self, form_element):
        # A punctuator is a Node with a single Node inside it (here labeled "pnode")
        # The punctuator has an array ("punctuation") of elements of pnode, that are to be parsed
        # Currently these elements should be PUNCTUATION tokens, of value either ',', ';', or ':'

        punctuator = form_element.code
        """ :type : Punctuator """
        punctuation = punctuator.punctuation
        pnode = punctuator.first.code
        assert isinstance(pnode, Node)

        def _replace_punctuator_with_pform():
            parent = form_element.parent
            return parent.replace(form_element, pnode).next

        if len(punctuation) == 0 or len(pnode) < 2:
            if punctuator.last_element is not None:
                pnode.remove(punctuator.last_element)
            return _replace_punctuator_with_pform()

        start_of_big_group = None
        first_small_group = None
        first_big_group = None

        has_groups = False
        has_big_groups = False
        seen_colon = False

        if len(punctuation) > 0 and punctuation[0].number < punctuator.skip_count:
            raise ArrangementError(punctuation[0].range.first_position, "Unexpected punctuation '%s' before start of argument sequence."  % punctuation[0].value)

        start_of_group = pnode[punctuator.skip_count]
        if is_token(start_of_group, TOKEN.PUNCTUATION):
            if start_of_group.value != ':':
                raise ArrangementError(start_of_group.range.first_position, "Unexpected punctuation '%s' at start of argument sequence."  % start_of_group.value)
            else:
                seen_colon = True
                colon = start_of_group
                start_of_group = colon.next
                pnode.remove(colon)
                punctuation.pop(0)


        def finish_groups(last_element):
            if has_groups:
                if start_of_group:
                    new = pnode.wrap(start_of_group, last_element, PreTuple)
                else:
                    new = start_of_group
                if has_big_groups and start_of_big_group is not None:
                    pnode.wrap(start_of_big_group, new, PreTuple)


        for punctuation_token in punctuation:

            value = punctuation_token.value

            if value == "," or value == ";":
                has_groups = True
                if start_of_group is punctuation_token:
                    raise ArrangementError(punctuation_token.range.first_position, "Unexpected punctuation '%s'."  % punctuation_token.value)

                new_group = pnode.wrap(start_of_group, punctuation_token.prev, PreTuple)
                if first_small_group is None:
                    first_small_group = new_group
                if start_of_big_group is None:
                    start_of_big_group = new_group
                start_of_group = punctuation_token.next
            elif punctuation_token.value != ':':
                raise ArrangementError(punctuation_token.range.first_position, "Unknown punctuation '%s' in argument sequence."  % punctuation_token.value)


            if value == ";":
                has_big_groups = True
                if start_of_big_group:
                    if start_of_big_group is punctuation_token:
                        raise ArrangementError(punctuation_token.range.first_position, "Unexpected punctuation '%s'."  % punctuation_token.value)
                    new_big_group = pnode.wrap(start_of_big_group, punctuation_token.prev, PreTuple)
                    if first_big_group is None:
                        first_big_group = new_big_group
                start_of_big_group = None

            if value == ":":
                if seen_colon:
                    raise ArrangementError(punctuation_token.range.first_position, "Argument sequence should have a single colon ':'.")
                seen_colon = True
                finish_groups(punctuation_token.prev)
                has_groups = False
                has_big_groups = False
                if first_small_group is None:
                    first = pnode[1]
                elif first_big_group is None:
                    first = first_small_group
                else:
                    first = first_big_group
                pnode.wrap(first, punctuation_token.prev, PreTuple)
                start_of_group = punctuation_token.next
                start_of_big_group = None

            pnode.remove(punctuation_token)



        if punctuator.last_element is not None:
            finish_groups(punctuator.last_element)
            pnode.remove(punctuator.last_element)
        else:
            finish_groups(pnode.last)


        return _replace_punctuator_with_pform()


