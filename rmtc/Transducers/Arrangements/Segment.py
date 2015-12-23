import rmtc.Syntax.Tokens as Tokens
from rmtc.Common.Errors import ArrangementError
from rmtc.Syntax.Node import Element
from rmtc.Syntax.PreForm import PreForm
from rmtc.Syntax.Punctuator import Punctuator
from rmtc.Syntax.Token import is_token
from rmtc.Transducers.ArrangementRule import ArrangementRule
import rmtc.Transducers.Arrangements.Util as Util

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

    (``INDENT`` is signaled as the ``end_punctuation_marker`` of the punctuator, see :ref:`Punctuator`).

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

        punctuation = begin_token.punctuation
        new_form.remove(new_form.first) # remove BEGIN
        new_form.remove(new_form.last)  # remove END

        punctuator = Punctuator(new_form_element.code, punctuation, 1)

        return new_form_element.parent.replace(new_form_element, punctuator).next


    def _single_indented_segment_apply(self, begin_token) -> Element:
        # First we wrap everything from BEGIN to END in a new Node (of the given wrap_class, which is usually PreForm)
        new_form_element = begin_token.parent.wrap(begin_token, begin_token.end, self.wrap_class)
        new_form = new_form_element.code

        indent  = begin_token.indents[0]
        punctuation = begin_token.punctuation

        new_form.remove(new_form.first) # remove BEGIN
        new_form.remove(new_form.last)  # remove END


        has_colon = any(is_token(p, Tokens.PUNCTUATION, ':') for p in punctuation)

        if not has_colon: # If the segment does not have a colon, then we are in list-of-args mode
            # In list-of-args mode, we replace every newline with a comma, and "open-up"
            # every segment in the indented block that doesn't have indented sub-blocks or a colon

            first_begin_after_indentation = indent.next

            # replace indent with comma
            new_comma = Tokens.PUNCTUATION(None, ",", None, None)
            new_form.insert(indent, new_comma)
            punctuation.append(new_comma)
            new_form.remove(indent)

            # remove BEGIN/END pairs of non-indented, non-colon-having segments
            extra_punctuation = Util.explode_list_of_args(first_begin_after_indentation)
            punctuation.extend(extra_punctuation)

            punctuator = Punctuator(new_form_element.code, punctuation, 1)
        else: # otherwise, we are in list-of-forms mode
            punctuator = Punctuator(new_form_element.code, punctuation, 1, indent)

        return new_form_element.parent.replace(new_form_element, punctuator).next

    # BEGIN h a INDENT $b INDENT c END  ₐ⟅h⟨a⟩ b c⟆ₐ
    # b  BEGIN a  :  END  ⟅a⟨⟩⟆ₐ
    # b  BEGIN  END  ⟨⟩
    # b  BEGIN  INDENT  END  error
    # out[2].punctuation := in[0].punctuation
    def _double_indented_segment_apply(self, element) -> Element:
        # new_form_element = element.parent.wrap(element, element.end, self.wrap_class)
        # new_form = new_form_element.code

        raise NotImplementedError()