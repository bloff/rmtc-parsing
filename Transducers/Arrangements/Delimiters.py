from Common.Util import is_not_none
from Syntax.Punctuator import Punctuator
from Syntax.__exports__ import Form, Identifier
from Syntax.PreTuple import PreTuple
from Syntax.Node import Element
from Syntax.Token import is_token, TOKEN
from Transducers.ArrangementRule import ArrangementRule
from Common.Errors import ArrangementError, TokenizingError
from Transducers.Arrangements.Block import Block


class DelimiterUtil:

    @staticmethod
    def is_opening_delimiter(element:Element, opening_delimiter_str:str):
        return is_token(element, TOKEN.BEGIN_MACRO, token_text=opening_delimiter_str)

    @staticmethod
    def is_opening_delimiter_among(element:Element, opening_delimiters:set):
        return is_token(element, TOKEN.BEGIN_MACRO) and element.text in opening_delimiters

    @staticmethod
    def has_head_element(opening_delimiter:Element):
        possible_head_element = opening_delimiter.prev
        return (is_not_none(possible_head_element, ".code.range.position_after.index") and
                possible_head_element.code.range.position_after.index == opening_delimiter.range.first_position.index)

    @staticmethod
    def has_unique_indentation_free_block(opening_delimiter_element):
        closing_delimiter_element = opening_delimiter_element.end
        begin_element = opening_delimiter_element.next
        assert is_token(begin_element, TOKEN.BEGIN)
        assert begin_element.end is not None
        end_element = begin_element.end
        assert end_element.next is closing_delimiter_element or is_token(end_element.next, TOKEN.BEGIN)

        return end_element.next is closing_delimiter_element and len(begin_element.indents) == 0

    @staticmethod
    def has_unique_block(opening_delimiter_element):
        closing_delimiter_element = opening_delimiter_element.end
        begin_element = opening_delimiter_element.next
        assert is_token(begin_element, TOKEN.BEGIN)
        assert begin_element.end is not None
        end_element = begin_element.end
        assert end_element.next is closing_delimiter_element or is_token(end_element.next, TOKEN.BEGIN)

        return end_element.next is closing_delimiter_element

    @staticmethod
    def _element_after(element) -> Element:
        if is_token(element, TOKEN.BEGIN_MACRO) or is_token(element, TOKEN.BEGIN):
            return element.end.next
        else:
            return element.next


    @staticmethod
    def join_all_args(new_form_element, begin_element, block_name, skip_count):
        # Takes a sequence of BEGIN ... ENDs and throws away the BEGIN/ENDs,
        # and wraps everything in a punctuator
        # so BEGIN ab, c, END BEGIN d, e END becomes PUNCTUATOR ab, c, d, e

        new_form = new_form_element.code

        punctuation = []
        while begin_element is not None:
            assert is_token(begin_element, TOKEN.BEGIN)
            assert begin_element.end is not None
            end_element = begin_element.end
            assert is_token(end_element, TOKEN.END)
            if len(begin_element.indents) > 0:
                raise ArrangementError(begin_element.indents[0].range.first_position, "Unexpected indentation inside %s." % block_name)
            punctuation.extend(begin_element.punctuation[0])
            new_form.remove(begin_element)
            begin_element = end_element.next
            new_form.remove(end_element)

        if len(punctuation) > 0:
            punctuator = Punctuator(new_form, punctuation, skip_count)
            return new_form_element.parent.replace(new_form_element, punctuator).next
        else:
            return new_form_element.next



class ApplyParenthesis(ArrangementRule):
    """
    Applies the transformation::

      BEGIN_MACRO("⦅") BEGIN  END END_MACRO  ⟨⦅⦆⟩

    """
    def __init__(self):
        ArrangementRule.__init__(self, "Application Parenthesis")
        self.block_arrangement = Block(Form)

    def applies(self, element):
        return DelimiterUtil.is_opening_delimiter(element, '⦅')

    def apply(self, element) -> Element:
        unique_block = DelimiterUtil.has_unique_block(element)
        if unique_block:
            # BEGIN_MACRO BEGIN ... END END_MACRO => BEGIN ... END
            parent = element.parent
            next_element = element.next
            parent.remove(element) # remove BEGIN_MACRO '('
            parent.remove(element.end) # remove END_MACRO ')'
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
    def __init__(self):
        ArrangementRule.__init__(self, "Parenthesis")

    def applies(self, element):
        return DelimiterUtil.is_opening_delimiter(element, '(') and DelimiterUtil.has_head_element(element)

    def apply(self, element) -> Element:
        new_form_element = element.parent.wrap(element.prev, element.end, Form)
        new_form = new_form_element.code

        begin_element = element.next
        new_form.remove(element) # remove BEGIN_MACRO '('
        new_form.remove(element.end)  # remove END_MACRO ')'
        return DelimiterUtil.join_all_args(new_form_element, begin_element, "head-prefixed parenthesized form", 1)

class ParenthesisNoHead(ArrangementRule):
    def __init__(self):
        ArrangementRule.__init__(self, "Parenthesis")
        self.apply_parenthesis_arrangement = ApplyParenthesis()

    def applies(self, element):
        return DelimiterUtil.is_opening_delimiter(element, '(') and not DelimiterUtil.has_head_element(element)

    def apply(self, element) -> Element:
        first_begin = element.next
        assert is_token(first_begin, TOKEN.BEGIN)
        has_colon = any(is_token(p, TOKEN.PUNCTUATION, ':') for p in first_begin.punctuation[0])
        if has_colon:
            return self.apply_parenthesis_arrangement.apply(element)
        else:
            return self._as_tuple(element)


    def _as_tuple(self, element) -> Element:
        new_tuple_element = element.parent.wrap(element, element.end, PreTuple)
        new_tuple = new_tuple_element.code

        begin_element = element.next
        new_tuple.remove(element) # remove BEGIN_MACRO '('
        new_tuple.remove(element.end)  # remove END_MACRO ')'
        return DelimiterUtil.join_all_args(new_tuple_element, begin_element, "tuple", 0)

    # def _as_pre_block(self, element):
    #     unique_block = DelimiterUtil.has_unique_block(element)
    #     if unique_block:
    #         # BEGIN_MACRO BEGIN ... END END_MACRO => BEGIN ... END
    #         parent = element.parent
    #         next_element = element.next
    #         parent.remove(element) # remove BEGIN_MACRO '('
    #         parent.remove(element.end) # remove END_MACRO ')'
    #         return next_element
    #     else:
    #         # BEGIN_MACRO BEGIN ... END BEGIN ... END END_MACRO => block( BEGIN ... END BEGIN ... END )
    #         new_pre_block_element = element.parent.wrap(element, element.end, Form)
    #         pre_block = new_pre_block_element.code
    #         pre_block.remove(element) # remove BEGIN_MACRO '('
    #         pre_block.remove(element.end) # remove END_MACRO '('
    #         pre_block.prepend(Identifier("block"))
    #         return new_pre_block_element.next

# class ArgSeqArrangement(ArrangementRule):
#     def __init__(self):
#         ArrangementRule.__init__(self, "ArgSeq")
#
#     def applies(self, element):
#         return DelimiterUtil.is_opening_delimiter(element, '⟨')
#
#     def apply(self, element) -> Element:
#
#         new_form_element = element.parent.wrap(element, element.end, Punctuator)
#         new_form = new_form_element.code
#         # ( begin-macro begin ... end end-macro )
#
#
#         unique_block = DelimiterUtil.has_unique_block(element)
#         new_form.remove(element) # remove BEGIN_MACRO
#         new_form.remove(new_form.last)  # remove END_MACRO ')'
#
#         if unique_block:
#             new_form.remove(new_form.first) # remove BEGIN
#             new_form.remove(new_form.last)  # remove END
#
#         return new_form_element.next

class Delimiters(ArrangementRule):
    def __init__(self, opening_delimiters):
        ArrangementRule.__init__(self, "Delimiters")
        self.opening_delimiters = opening_delimiters

    def applies(self, element):
        return DelimiterUtil.is_opening_delimiter_among(element, self.opening_delimiters)

    def apply(self, element) -> Element:
        has_head = DelimiterUtil.has_head_element(element)
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
        new_form.remove(element) # remove BEGIN_MACRO('[')
        new_form.remove(new_form.last)  # remove END_MACRO(']')

        return DelimiterUtil.join_all_args(new_form_element, begin_element, "head-prefixed parenthesized form", 2 if has_head else 1)






class Quote(ArrangementRule):
    def __init__(self, opening_delimiters):
        ArrangementRule.__init__(self, "SingleQuote")
        self.opening_delimiters = opening_delimiters

    def applies(self, element):
        return DelimiterUtil.is_opening_delimiter_among(element, self.opening_delimiters)

    def apply(self, element) -> Element:
        new_form_element = element.parent.wrap(element, element.end, Form)
        new_form = new_form_element.code
        new_form.prepend(Identifier("quote", element.range))
        # @[] begin-macro begin head ... end end-macro

        # unique_indentation_free_block = DelimiterUtil.has_unique_indentation_free_block(element)
        new_form.remove(element) # remove BEGIN_MACRO '
        new_form.remove(new_form.last)  # remove END_MACRO '

        # if unique_indentation_free_block:
        #     new_form.remove(new_form[2] if has_head else new_form[1]) # remove BEGIN
        #     new_form.remove(new_form.last)  # remove END
        #     if has_head: new_form.insert(new_form[1], Identifier(':'))
        return new_form_element.next


