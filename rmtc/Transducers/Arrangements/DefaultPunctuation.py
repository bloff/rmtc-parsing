from jinja2.lexer import TOKEN_TILDE

from rmtc.Common.Errors import ArrangementError
from rmtc.Syntax.Node import Node, Element
from rmtc.Syntax.Punctuator import Punctuator
from rmtc.Syntax.PreSeq import PreSeq
from rmtc.Syntax.Token import is_token
import rmtc.Syntax.Tokens as Tokens
from rmtc.Syntax.Tokens import PUNCTUATION
from rmtc.Transducers.ArrangementRule import ArrangementRule


class DefaultPunctuation(ArrangementRule):
    """
    Processes punctuators, by organizing ,-and-;-separated lists into nested tuples.

    Takes something like::

        ⟨⟅H     a b,  c d ;   e f, g, h :    x y, z⟆⟩

    And outputs::

        ⟅H ( ((a b) (c d)) ((e f) g h) )  ((x y) z)⟆

    where ``H`` is the first punctuator.skip_count elements, and ``⟅⟆`` denotes
    some subclass of :ref:`Node`.

    If the punctuator has a non-None ``end_punctuation_marker`` attribute, then takes::

        ⟨⟅H     a b,  c d ;   e f, g, h :    x y, z   X ⟆⟩

    And outputs::

        ⟅H ( ((a b) (c d)) ((e f) g h) )  ((x y) z) ⟆

    where ``X`` is the punctuator's ``end_punctuation_marker``.

    """

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
        # punctuation = punctuator.punctuation
        pnode = punctuator.first.code
        assert isinstance(pnode, Node)

        def _replace_punctuator_with_pform():
            parent = form_element.parent
            return parent.replace(form_element, pnode).next

        if len(pnode) < 2:
            if punctuator.end_punctuation_marker is not None:
                pnode.remove(punctuator.end_punctuation_marker)
            return _replace_punctuator_with_pform()

        first_small_group = None

        seen_colon = False


        # 1. Check to make sure there are no punctuation tokens before the skip_count
        start_of_group = pnode[0]
        for i in range(punctuator.skip_count):
            if is_token(start_of_group, Tokens.PUNCTUATION):
                raise ArrangementError(start_of_group.range, "Unexpected punctuation '%s' before start of argument sequence." % start_of_group.value)
            start_of_group = start_of_group.next

        # 2. Remove leading break, if any
        while is_token(start_of_group, Tokens.ARGBREAK):
            nxt = start_of_group.next
            pnode.remove(start_of_group)
            start_of_group = nxt

        # 2. The first token after skip_count cannot be punctuation, unless it's a colon ':'
        if is_token(start_of_group, Tokens.PUNCTUATION):
            if start_of_group.value != ':':
                raise ArrangementError(start_of_group.range.first_position, "Unexpected punctuation '%s' at start of argument sequence."  % start_of_group.value)
            else:
                seen_colon = True
                colon = start_of_group
                start_of_group = colon.next
                pnode.remove(colon)
                # and after this colon there should not be any punctuation
                if is_token(start_of_group, Tokens.PUNCTUATION) and not is_token(start_of_group, Tokens.ARGBREAK):
                    raise ArrangementError(start_of_group.range.first_position, "Unexpected punctuation '%s' after ':'."  % start_of_group.value)


        # This function will wrap the last group of tokens in a PreSeq
        def finish_groups(last_element_in_group):
            nonlocal first_small_group
            if start_of_group is not None and start_of_group is not last_element_in_group:
                new_seq = pnode.wrap(start_of_group, last_element_in_group, PreSeq)
                if first_small_group is None:
                    first_small_group = new_seq


        # Iterate through all elements of the node, in search of ',' or ':' punctuation tokens, or ARGBREAK tokens
        for punctuation_token in pnode.iterate_from(start_of_group):

            # an ARGBREAK token will wrap the previous tokens (from start_of_group to this point)
            if is_token(punctuation_token, Tokens.ARGBREAK):
                if start_of_group is punctuation_token:
                    # ARGBREAKS after punctuation tokens are ignored
                    start_of_group = punctuation_token.next
                    pnode.remove(punctuation_token)
                else:
                    # wrap-previous-tokens(start_of_group, punctuation_token, PreSeq)
                    new_group = pnode.wrap(start_of_group, punctuation_token.prev, PreSeq)
                    if first_small_group is None:
                        first_small_group = new_group
                    start_of_group = punctuation_token.next
                    pnode.remove(punctuation_token)
            elif is_token(punctuation_token, Tokens.PUNCTUATION, ','):
                if start_of_group is punctuation_token:
                    raise ArrangementError(punctuation_token.range.first_position, "Unexpected punctuation '%s'."  % punctuation_token.value)
                # wrap-previous-tokens(start_of_group, punctuation_token, PreSeq)
                new_group = pnode.wrap(start_of_group, punctuation_token.prev, PreSeq)
                if first_small_group is None:
                    first_small_group = new_group
                start_of_group = punctuation_token.next
                pnode.remove(punctuation_token)

            elif is_token(punctuation_token, Tokens.PUNCTUATION, ':'):
                if seen_colon:
                    raise ArrangementError(punctuation_token.range.first_position, "Argument sequence should have a single colon ':'.")
                if start_of_group is punctuation_token:
                    raise ArrangementError(punctuation_token.range.first_position, "Unexpected punctuation '%s'."  % punctuation_token.value)
                seen_colon = True
                finish_groups(punctuation_token.prev)
                if first_small_group is None:
                    first = start_of_group
                else:
                    first = first_small_group
                pnode.wrap(first, punctuation_token.prev, PreSeq)
                start_of_group = punctuation_token.next
                pnode.remove(punctuation_token)
            elif is_token(punctuation_token, Tokens.PUNCTUATION):
                raise ArrangementError(punctuation_token.range.first_position, "Default punctuator cannot parse unknown punctuation token '%s'."  % punctuation_token.value)


        if punctuator.end_punctuation_marker is not None:
            finish_groups(punctuator.end_punctuation_marker.prev)
            pnode.remove(punctuator.end_punctuation_marker)
        else:
            finish_groups(pnode.last)


        return _replace_punctuator_with_pform()


g = 1
def f():
    g = 10
    def ff():
        global g
        g = 20
    ff()
    print(g)

f()