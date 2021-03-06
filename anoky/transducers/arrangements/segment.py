import anoky.syntax.tokens as Tokens
import anoky.transducers.arrangements.util as Util
from anoky.common.errors import ArrangementError
from anoky.syntax.token import is_token
from anoky.syntax.node import Element
from anoky.syntax.preform import PreForm
from anoky.syntax.preseq import PreSeq
from anoky.transducers.arrangement_rule import ArrangementRule


# returns element after the head

class Segment(ArrangementRule):
    """
    Arrangement for Segments, triggered on the pattern ``BEGIN ⋅``.

    If the ``BEGIN`` token has zero ``INDENT`` tokens, does the transformation::

      BEGIN⋅ head  END  ⟨⟅head ⟆⟩⋅

    where ``⟅⟆`` is a ``Node`` of type ``self.wrap_class``. ``⟨⟩`` is a ``Punctuator``, which gets the list of punctuation tokens
    associated with the ``BEGIN`` token.

    If the ``BEGIN`` token has one INDENT, does the transformation::

        BEGIN⋅ head  INDENT  END  ⟨⟅head  INDENT ⟆⟩⋅


    Currently more than one INDENT token is unimplemented (and raises ``NotImplementedError``).
    """
    def __init__(self, wrap_class = PreForm):
        ArrangementRule.__init__(self, "Segment")
        self.wrap_class = wrap_class
        """The type of node to wrap segment in. Usually ``PreForm``."""

    def applies(self, element):
        return is_token(element, Tokens.BEGIN)

    def apply(self, element) -> Element:
        if len(element.indents) == 0:
            return self._unindented_segment_apply(element)
        elif len(element.indents) == 1:
            return self._single_indented_segment_apply(element)
        elif len(element.indents) == 2:
            return self._double_indented_segment_apply(element)
        else:
            raise ArrangementError(element.indents[2].range.first_position,
                                 "Only two indentation levels are allowed in segment (%d indentation levels found in segment that begins in position %s)." % (len(element.indents), element.range.first_position.nameless_str))

    def _unindented_segment_apply(self, begin_token) -> Element:
        new_form_element = begin_token.parent.wrap(begin_token, begin_token.end, self.wrap_class)
        new_form = new_form_element.code

        new_form.remove(new_form.first) # remove BEGIN
        new_form.remove(new_form.last)  # remove END

        return new_form_element.next


    def _single_indented_segment_apply(self, begin_token) -> Element:
        # First we wrap everything from BEGIN to END in a new Node (of the given wrap_class, which is usually PreForm)
        new_form_element = begin_token.parent.wrap(begin_token, begin_token.end, self.wrap_class)
        new_form = new_form_element.code

        indent  = begin_token.indents[0]
        # punctuation = begin_token.punctuation

        has_colon = begin_token.find_punctuation(':', indent) is not None

        new_form.remove(new_form.first) # remove BEGIN
        new_form.remove(new_form.last)  # remove END





        if not has_colon: # If the segment does not have a colon, then we are in list-of-args mode
            # In list-of-args mode, we replace every newline with an ARGBREAK, and "open-up"
            # every segment in the indented block that doesn't have indented sub-blocks or a colon

            first_begin_after_indentation = indent.next

            # replace indent with ARGBREAK when there are some elements
            # between the head and the indent token
            if indent.prev is not new_form.first:
                new_form.insert(indent, Tokens.ARGBREAK())

            new_form.remove(indent)

            # at this point, new_form was transformed like this:
            # BEGIN head xxx INDENT BEGIN ... END END => head xxx ARGBREAK BEGIN ... END
            # BEGIN head INDENT BEGIN ... END END => head BEGIN ... END

            # remove BEGIN/END pairs of non-indented, non-colon-having segments
            Util.explode_list_of_args(first_begin_after_indentation)


        return new_form_element.next

    # BEGIN h a INDENT $b INDENT c END  ₐ⟅h⟨a⟩ b c⟆ₐ
    # b <- BEGIN a  :  END  ⟅a⟨⟩⟆ₐ
    # b <- BEGIN  END  ⟨⟩
    # b <- BEGIN  INDENT  END  error
    # out[2].punctuation := in[0].punctuation

    def _double_indented_segment_apply(self, begin_token) -> Element:
        new_form_element = begin_token.parent.wrap(begin_token, begin_token.end, self.wrap_class)
        new_form = new_form_element.code

        indent0, indent1 = begin_token.indents

        first_args_begin = indent0.next

        colon = begin_token.find_punctuation(':', indent0)
        if colon is not None:
            raise ArrangementError(colon.range.first_position, "Dual indented segment cannot have ':' in its first line.")


        # replace first INDENT with ARGBREAK
        new_break = Tokens.ARGBREAK()
        new_form.insert(indent0, new_break)
        new_form.remove(indent0)


        # explode the args
        # (the explode function stops when it hits the second INDENT)
        Util.explode_list_of_args(first_args_begin)


        # wrap everything after head and before second INDENT in preseq inside a punctuator

        begin_token.parent.wrap(begin_token.next.next, indent1.prev, PreSeq)


        # remove BEGIN and END
        new_form.remove(new_form.first)
        new_form.remove(new_form.last)


        return new_form_element.next








        #raise NotImplementedError()