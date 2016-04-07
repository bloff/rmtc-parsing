import anoky.Syntax.Tokens as Tokens
from anoky.common.errors import TokenizingError
from anoky.Syntax.Form import Form
from anoky.Syntax.Identifier import Identifier
from anoky.Syntax.Node import Element
from anoky.Syntax.PreSeq import PreSeq
from anoky.Syntax.Punctuator import Punctuator
from anoky.Syntax.Token import is_token
from anoky.transducers.arrangement_rule import ArrangementRule
from anoky.transducers.arrangements.segment import Segment
import anoky.transducers.arrangements.util as Util


class ApplyParenthesis(ArrangementRule):
    """
    Applies the transformation::

      BEGIN_MACRO("⦅") BEGIN ⋅  END END_MACRO  ⟨⦅⦆⟩ ⋅

    Signals error if there is more than one ``BEGIN  END`` sequence.
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Application Parenthesis")
        self.block_arrangement = Segment(Form)

    def applies(self, element):
        return Util.is_opening_delimiter(element, '⦅')

    def apply(self, element) -> Element:
        unique_block = Util.has_unique_block(element)
        if unique_block:
            # BEGIN_MACRO BEGIN ... END END_MACRO => BEGIN ... END
            parent = element.parent
            next_element = element.next
            next_element.range.first_position = element.range.first_position
            next_element.end.range.position_after = element.end.range.position_after
            parent.remove(element) # remove BEGIN_MACRO '⦅'
            parent.remove(element.end) # remove END_MACRO '⦆'
            return self.block_arrangement.apply(next_element)
        else:
            raise TokenizingError(element.range, "Unexpected multiple blocks inside double-parenthesis.")
            # # BEGIN_MACRO BEGIN ... END BEGIN ... END END_MACRO => block( BEGIN ... END BEGIN ... END )
            # new_pre_block_element = element.parent.wrap(element, element.end, Form)
            # pre_block = new_pre_block_element.code
            # pre_block.remove(element) # remove BEGIN_MACRO '('
            # pre_block.remove(element.end) # remove END_MACRO '('
            # pre_block.prepend(Identifier("block"))
            # return new_pre_block_element.next


# head( [BEGIN ... END]* ) => ⦅head <...>*))


class ParenthesisWithHead(ArrangementRule):
    """
    Applies the transformation::

      head BEGIN_MACRO("(") ⋅ BEGIN  END END_MACRO  ⟨⦅head ⦆⟩ ⋅

    when there is zero whitespace between ``head`` and the ``BEGIN_MACRO`` token.
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Parenthesis")

    def applies(self, element):
        return Util.is_opening_delimiter(element, '(') and Util.has_head_element(element)

    def apply(self, beginmacro_token) -> Element:
        new_form_element = beginmacro_token.parent.wrap(beginmacro_token.prev, beginmacro_token.end, Form)
        new_form = new_form_element.code

        begin_element = beginmacro_token.next
        last_element = new_form.last
        new_form.remove(beginmacro_token) # remove BEGIN_MACRO('(')
        new_form.remove(last_element)  # remove END_MACRO(')')
        if begin_element is last_element: # if we have something like a[] or a{} or so...
            return new_form_element.next
        else:
            # return Util.join_all_args(new_form_element, begin_element, "head-prefixed parenthesized form", 1)
            Util.explode_list_of_args(begin_element)
            return new_form_element.next


class ParenthesisNoHead(ArrangementRule):
    """
    Applies the transformation::

      BEGIN_MACRO("(") ⋅ (BEGIN  END)* END_MACRO  ⟨⟅*⟆⟩ ⋅

    which removes BEGIN and END tokens, wraps what's left in a PreTuple, and that in a Punctuator. The list of punctuation
    tokens given to the punctuator is the appending of all lists of punctuation tokens in each ``BEGIN  END`` pair.
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Parenthesis")
        self.apply_parenthesis_arrangement = ApplyParenthesis()

    def applies(self, element):
        return Util.is_opening_delimiter(element, '(') and not Util.has_head_element(element)

    def apply(self, element) -> Element:
        first_begin = element.next
        assert is_token(first_begin, Tokens.BEGIN)

        new_seq_element = element.parent.wrap(element, element.end, PreSeq)
        new_seq = new_seq_element.code

        begin_element = element.next
        last_element = new_seq.last
        new_seq.remove(element) # remove BEGIN_MACRO('(')
        new_seq.remove(last_element)  # remove END_MACRO(')')
        #if begin_element is last_element: # if we have something like a[] or a{} or so...
        #    return new_tuple_element.next
        #else:
        #    return \
        Util.explode_list_of_args(begin_element)
        return new_seq_element.next


class Delimiters(ArrangementRule):
    """
    Applies the transformations::

      head BEGIN_MACRO("[") ⋅ (BEGIN  END)* END_MACRO  ⟨⦅@[] head *⦆⟩ ⋅

      BEGIN_MACRO("[") ⋅ (BEGIN  END)* END_MACRO  ⟨⦅[] *⦆⟩ ⋅

    Where ``[``  can be any string in the ``opening_delimiters`` attribute.
    """
    def __init__(self, opening_delimiters):
        ArrangementRule.__init__(self, "Delimiters")
        self.opening_delimiters = opening_delimiters

    def applies(self, element):
        return Util.is_opening_delimiter_among(element, self.opening_delimiters)

    def apply(self, element) -> Element:
        has_head = Util.has_head_element(element)
        if has_head:
            new_form_element = element.parent.wrap(element.prev, element.end, Form)
            new_form = new_form_element.code
            new_form.prepend(Identifier("@" + element.text + element.end.text, element.range))
            # @[] head BEGIN_MACRO('[') begin ... end END_MACRO(']')
        else:
            new_form_element = element.parent.wrap(element, element.end, Form)
            new_form = new_form_element.code
            new_form.prepend(Identifier(element.text + element.end.text, element.range))
            # @[] BEGIN_MACRO('[') begin head ... end END_MACRO(']')


        begin_element = element.next
        last_element = new_form.last
        new_form.remove(element) # remove BEGIN_MACRO('[')
        new_form.remove(new_form.last)  # remove END_MACRO(']')
        if begin_element is last_element: # if we have something like a[] or a{} or so...
            return new_form_element.next
        else:
            # return Util.join_all_args(new_form_element, begin_element, "head-prefixed parenthesized form", 2 if has_head else 1)
            Util.explode_list_of_args(begin_element)
            return new_form_element.next





class Quote(ArrangementRule):
    """
    Applies the transformation::

      BEGIN_MACRO("‘") ⋅  END_MACRO  ⦅quote ⦆ ⋅

    Where ``‘`` can be any string in the ``opening_delimiters`` attribute.
    """
    def __init__(self, opening_delimiters):
        ArrangementRule.__init__(self, "SingleQuote")
        self.opening_delimiters = opening_delimiters

    def applies(self, element):
        return Util.is_opening_delimiter_among(element, self.opening_delimiters)

    def apply(self, element) -> Element:
        new_form_element = element.parent.wrap(element, element.end, Form)
        new_form = new_form_element.code
        new_form.prepend(Identifier("quote", element.range))

        new_form.remove(element) # remove BEGIN_MACRO '
        new_form.remove(new_form.last)  # remove END_MACRO '

        return new_form_element.next


