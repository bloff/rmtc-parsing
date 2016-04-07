import anoky.Syntax.Tokens as Tokens
from anoky.Common.Errors import ArrangementError
from anoky.Syntax.Node import Node, Element
from anoky.Syntax.PreSeq import PreSeq
from anoky.Syntax.Token import is_token
from anoky.Syntax.Tokens import PUNCTUATION, INDENT
from anoky.Syntax.Util import is_form, is_seq, is_identifier
from anoky.Transducers.ArrangementRule import ArrangementRule


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

    def __init__(self, skip_count):
        ArrangementRule.__init__(self, "Default Punctuation")
        self.skip_count = skip_count

    def applies(self, element: Element):
        raise NotImplementedError()

    def apply(self, element: Element):

        node = element.code
        assert isinstance(node, Node)

        if len(node) < 2:
            return element.next

        first_small_group = None
        seen_colon = False

        # 1. Check to make sure there are no punctuation tokens before the skip_count
        start_of_group = node[0]
        for i in range(self.skip_count):
            if is_token(start_of_group, Tokens.PUNCTUATION):
                raise ArrangementError(start_of_group.range,
                                       "Unexpected punctuation '%s' before start of argument sequence." % start_of_group.value)
            start_of_group = start_of_group.next

        # 2. Remove leading break, if any
        while is_token(start_of_group, Tokens.ARGBREAK):
            nxt = start_of_group.next
            node.remove(start_of_group)
            start_of_group = nxt

        # 2. The first token after skip_count cannot be punctuation, unless it's a colon ':'
        if is_token(start_of_group, Tokens.PUNCTUATION):
            if start_of_group.value != ':':
                raise ArrangementError(start_of_group.range.first_position,
                                       "Unexpected punctuation '%s' at start of argument sequence." % start_of_group.value)
            else:
                seen_colon = True
                colon = start_of_group
                start_of_group = colon.next
                node.remove(colon)
                # and after this colon there should not be any punctuation
                if is_token(start_of_group, Tokens.PUNCTUATION) and not is_token(start_of_group, Tokens.ARGBREAK):
                    raise ArrangementError(start_of_group.range.first_position,
                                           "Unexpected punctuation '%s' after ':'." % start_of_group.value)
                # but there should be *something*
                elif start_of_group is None:
                    raise ArrangementError(colon.range, "Nothing after `:`!")

        # This function will wrap the last group of tokens in a PreSeq
        def finish_groups(last_element_in_group):
            nonlocal first_small_group
            if start_of_group not in [None, node[0], last_element_in_group, start_of_group]:
                node.wrap(start_of_group, last_element_in_group, PreSeq)

        if start_of_group is None:
            return element.next

        # Iterate through all elements of the node, in search of ',' or ':' punctuation tokens, or ARGBREAK tokens
        # If there are two or more elements between such tokens, wrap them in a PreSeq
        # Stop if an INDENT token is found
        for punctuation_token in node.iterate_from(start_of_group):

            # an ARGBREAK token will wrap the previous tokens (from start_of_group to this point)
            if is_token(punctuation_token, Tokens.ARGBREAK):
                if start_of_group is punctuation_token:
                    # ARGBREAKS after punctuation tokens are ignored
                    start_of_group = punctuation_token.next
                    node.remove(punctuation_token)
                else:
                    # wrap-previous-tokens(start_of_group, punctuation_token, PreSeq)
                    new_group = node.wrap(start_of_group, punctuation_token.prev, PreSeq)
                    if first_small_group is None:
                        first_small_group = new_group
                    start_of_group = punctuation_token.next
                    node.remove(punctuation_token)
            elif is_token(punctuation_token, Tokens.PUNCTUATION, ','):
                if start_of_group is punctuation_token:
                    raise ArrangementError(punctuation_token.range.first_position,
                                           "Unexpected punctuation '%s'." % punctuation_token.value)
                # wrap-previous-tokens(start_of_group, punctuation_token, PreSeq)
                new_group = node.wrap(start_of_group, punctuation_token.prev, PreSeq)
                if first_small_group is None:
                    first_small_group = new_group
                start_of_group = punctuation_token.next
                node.remove(punctuation_token)

            elif is_token(punctuation_token, Tokens.PUNCTUATION, ':'):
                if seen_colon:
                    raise ArrangementError(punctuation_token.range.first_position,
                                           "Argument sequence should have a single colon ':'.")
                if start_of_group is punctuation_token:
                    raise ArrangementError(punctuation_token.range.first_position,
                                           "Unexpected punctuation '%s'." % punctuation_token.value)
                seen_colon = True
                finish_groups(punctuation_token.prev)
                if first_small_group is None:
                    first = start_of_group
                else:
                    first = first_small_group
                node.wrap(first, punctuation_token.prev, PreSeq)
                start_of_group = punctuation_token.next
                node.remove(punctuation_token)
            elif is_token(punctuation_token, Tokens.PUNCTUATION):
                raise ArrangementError(punctuation_token.range.first_position,
                                       "Default punctuator cannot parse unknown punctuation token '%s'." % punctuation_token.value)
            elif is_token(punctuation_token, Tokens.INDENT):
                finish_groups(punctuation_token.prev)
                node.remove(punctuation_token)
                return element.next

        finish_groups(node.last)

        return element.next


class DefaultFormPunctuation(DefaultPunctuation):
    def __init__(self):
        DefaultPunctuation.__init__(self, 1)

    def applies(self, element: Element):
        return is_form(element.code)


class DefaultSeqPunctuation(DefaultPunctuation):
    def __init__(self):
        DefaultPunctuation.__init__(self, 0)

    def applies(self, element: Element):
        return is_seq(element.code)

class ForPunctuation(DefaultPunctuation):
    def __init__(self):
        DefaultPunctuation.__init__(self, 1)

    def applies(self, element: Element):
        return is_form(element.code, "for")

    def apply(self, element: Element):
        form = element.code
        elm = form[1]
        in_elm = None
        colon_elm = None
        ind_elm = None
        while elm is not None:
            if is_identifier(elm, 'in'):
                in_elm = elm
            elif is_token(elm, PUNCTUATION, ':'):
                colon_elm = elm
                break
            elm = elm.next

        if colon_elm is None or in_elm is None:
            raise ArrangementError(element.range, "`for` form must be punctuated by `in` and `:`.")
        if in_elm.prev is form[0]:
            raise ArrangementError(element.range, "No element before `in` in `for` form.")
        if in_elm.next is colon_elm:
            raise ArrangementError(element.range, "No element between `in` and `:` in `for` form.")

        form.wrap(form[1], in_elm.prev, PreSeq)
        form.wrap(in_elm.next, colon_elm.prev, PreSeq)
        form.remove(in_elm)

        return DefaultPunctuation.apply(self, element)

class Skip2Punctuation(DefaultPunctuation):
    def __init__(self, form_heads:set):
        DefaultPunctuation.__init__(self, 2)
        self.form_heads = form_heads

    def applies(self, element: Element):
        return is_form(element.code) and is_identifier(element.code.head) and element.code.head.code.full_name in self.form_heads
