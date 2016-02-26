from rmtc.Common.Errors import ArrangementError
from rmtc.Common.Util import is_not_none
from rmtc.Syntax import Tokens as Tokens
from rmtc.Syntax.Node import Element
from rmtc.Syntax.Punctuator import Punctuator
from rmtc.Syntax.Token import is_token


def is_opening_delimiter(element:Element, opening_delimiter_str:str):
    """
    Returns ``True`` if the given element is a ``BEGIN_MACRO`` token with ``text == opening_delimiter_str``.
    """
    return is_token(element, Tokens.BEGIN_MACRO, token_text=opening_delimiter_str)


def is_opening_delimiter_among(element:Element, opening_delimiters:set):
    """
    Returns ``True`` if the given element is a ``BEGIN_MACRO`` token with ``text in opening_delimiters``.
    """
    return is_token(element, Tokens.BEGIN_MACRO) and element.text in opening_delimiters


def has_head_element(opening_delimiter:Element):
    """
    Returns ``True`` if the given element is preceeded by an element with no whitespace in between.
    """
    possible_head_element = opening_delimiter.prev
    return (is_not_none(possible_head_element, ".code.range.position_after.index") and
            possible_head_element.code.range.position_after.index == opening_delimiter.range.first_position.index)



def has_unique_block(opening_delimiter_element):
    """
    Returns ``True`` if the given ``BEGIN_MACRO`` token is of the form::

       BEGIN_MACRO BEGIN  END END_MACRO

    (so there is a single ``BEGIN`` / ``END`` pair between the given ``BEGIN_MACRO`` and ``END_MACRO`` pair)
    """
    closing_delimiter_element = opening_delimiter_element.end
    begin_element = opening_delimiter_element.next
    assert is_token(begin_element, Tokens.BEGIN)
    assert begin_element.end is not None
    end_element = begin_element.end
    assert end_element.next is closing_delimiter_element or is_token(end_element.next, Tokens.BEGIN)

    return end_element.next is closing_delimiter_element


def _element_after(element) -> Element:
    """
    Skips ``BEGIN_MACRO`` / ``END_MACRO`` and ``BEGIN`` / ``END`` pairs.
    """
    if is_token(element, Tokens.BEGIN_MACRO) or is_token(element, Tokens.BEGIN):
        return element.end.next
    else:
        return element.next



def join_all_args(element_containing_node, begin_element, block_name, punctuator_skip_count):
    """
    Applies the transformation::

       ⟅(BEGIN  END)*⟆   ⟨⟅*⟆⟩

    where the left-hand ``⟅⟆`` denotes some :ref:`Node`. This removes BEGIN and END tokens, and the list of punctuation
    tokens given to the punctuator is the appending of all lists of punctuation tokens in each ``BEGIN  END`` pair.

    E.g. ``⟅BEGIN ab, c, END BEGIN d, e END⟆`` becomes ``⟨ab, c, d, e⟩``
    """

    node = element_containing_node.code

    punctuation = []
    while begin_element is not None:
        assert is_token(begin_element, Tokens.BEGIN)
        assert begin_element.end is not None
        end_element = begin_element.end
        assert is_token(end_element, Tokens.END)
        if len(begin_element.indents) > 0:
            raise ArrangementError(begin_element.indents[0].range.first_position, "Unexpected indentation inside %s." % block_name)
        punctuation.extend(begin_element.punctuation)
        node.remove(begin_element)
        begin_element = end_element.next
        node.remove(end_element)

    if len(punctuation) > 0:
        punctuator = Punctuator(node, punctuation, punctuator_skip_count)
        return element_containing_node.parent.replace(element_containing_node, punctuator).next
    else:
        return element_containing_node.next


def explode_list_of_args(first_begin_token):
    """
    Suppose we have a node with a sequence of segments, given by ``BEGIN``/``END`` token pairs::

         (BEGIN  END)* 

    and we are given the first ``BEGIN`` token.

    Then this function removes all ``BEGIN`` and ``END`` pairs that have neither a colon nor indentation, and returns a list
    concatenating every list of punctuation tokens in the removed ``BEGIN`` tokens.

    Furthermore, it adds commas im place of each removed ``END`` token that is not preceeded by a comma.

    E.g. ``⟅BEGIN ab, c, END BEGIN d, e END BEGIN h : a1 a2 END⟆`` becomes ``ab, c, d, e BEGIN h : a1 a2 END⟩.``

    :param first_begin_token: The first ``BEGIN`` token in the sequence.
    """

    node = first_begin_token.parent
    begin_token = first_begin_token

    while is_token(begin_token, Tokens.BEGIN):
        assert begin_token.end is not None
        end_token = begin_token.end
        assert is_token(end_token, Tokens.END)
        after_end = end_token.next
        make_preform = len(begin_token.indents) > 0 or begin_token.find_punctuation(':')

        if not make_preform: # if there is no INDENT token and no colons
            arg_break = Tokens.ARGBREAK()
            node.insert(end_token.prev, arg_break)
            node.remove(begin_token)
            node.remove(end_token)
        else:
            arg_break = Tokens.ARGBREAK()
            node.insert(end_token, arg_break)
        begin_token = after_end



def element_after(element) -> Element:
    if is_token(element, Tokens.BEGIN_MACRO) or is_token(element, Tokens.BEGIN):
        return element.end.next
    else:
        return element.next