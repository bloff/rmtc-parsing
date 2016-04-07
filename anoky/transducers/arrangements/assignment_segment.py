import anoky.syntax.tokens as Tokens
import anoky.transducers.arrangements.util as Util
from anoky.common.errors import ArrangementError
from anoky.syntax.token import is_token
from anoky.syntax.util import is_identifier
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Element
from anoky.syntax.preseq import PreSeq
from anoky.transducers.arrangement_rule import ArrangementRule


# returns element after the head

class AssignmentSegment(ArrangementRule):
    """
    Arrangement for Assignment Segments, triggered on the pattern ``BEGIN ⋅ ... = INDENT``.

    If the ``BEGIN`` token has one INDENT, does the transformation::

        BEGIN⋅  = INDENT  END  ⟨⟅= ⟅,⟆ ⟅,⟆⟆⟩⋅

    More than one INDENT signals error.
    """
    def __init__(self):
        ArrangementRule.__init__(self, "Assignment Segment")

    def applies(self, element):
        return is_token(element, Tokens.BEGIN) and \
               len(element.indents) > 0 and \
               (is_identifier(element.indents[0].prev, "=") or
                is_identifier(element.indents[0].prev, ":=")) and \
                element.next is not element.indents[0].prev

    def apply(self, element) -> Element:
        if len(element.indents) == 1:
            return self._single_indented_segment_apply(element)
        else:
            raise ArrangementError(element.indents[2].range.first_position,
                                 "Only one indentation level is allowed in assigning segment (%d indentation levels found in segment that begins in position %s)." % (len(element.indents), element.range.first_position.nameless_str))


    def _single_indented_segment_apply(self, begin_token) -> Element:
        # BEGIN  = INDENT  END
        new_form_element = begin_token.parent.wrap(begin_token, begin_token.end, Form)
        # (BEGIN  = INDENT  END)
        new_form = new_form_element.code

        indent  = begin_token.indents[0]
        assignment_symbol_elm = indent.prev

        has_colon = begin_token.find_punctuation(':', indent) is not None
        if has_colon:
            raise ArrangementError(has_colon.range, "Unexpected `:` in assignment segment.")

        new_form.wrap(begin_token.next, assignment_symbol_elm.prev, PreSeq)
        # (BEGIN ⟅,⟆ = INDENT  END)
        new_form.remove(new_form.first)
        # (⟅,⟆ = INDENT  END)
        new_form.remove(new_form.last)
        # (⟅,⟆ = INDENT  )
        new_form.remove(assignment_symbol_elm)
        # (⟅,⟆ INDENT  )
        new_form.prepend(Identifier("="))
        # (= ⟅,⟆ INDENT  )


        if is_identifier(assignment_symbol_elm, '='):
            first_begin_after_indentation = indent.next
            # remove BEGIN/END pairs of non-indented, non-colon-having segments
            Util.explode_list_of_args(first_begin_after_indentation)

        rvalue_elm = new_form.wrap(indent.next, new_form.last, PreSeq)
        # (= ⟅,⟆ INDENT ⟅,⟆ )
        new_form.remove(indent)
        # (= ⟅,⟆ ⟅,⟆ )

        return new_form_element.next
