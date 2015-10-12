from Syntax.Punctuator import Punctuator
from Syntax.PreForm import PreForm
from Syntax.Node import Element
from Syntax.Token import is_token, TOKEN
from Transducers.Arrangements.ArrangementRule import ArrangementRule
from Common.Errors import ArrangementError


# returns element after the head
def _element_after(element) -> Element:
    if is_token(element, TOKEN.BEGIN_MACRO) or is_token(element, TOKEN.BEGIN):
        return element.end.next
    else:
        return element.next

class Block(ArrangementRule):
    def __init__(self, wrap_class = PreForm):
        ArrangementRule.__init__(self, "Single-Indented Block")
        self.wrap_class = wrap_class

    def applies(self, element):
        return is_token(element, TOKEN.BEGIN)

    def apply(self, element) -> Element:
        if len(element.indents) == 0:
            return self._unindented_block_apply(element)
        elif len(element.indents) == 1:
            return self._single_indented_block_apply(element)
        elif len(element.indents) == 2:
            return self._double_indented_block_apply(element)
        else:
            raise ArrangementError(element.indents[2].range.first_position,
                                 "Only two indentation levels are allowed in (default) block (%d indentation levels found in block that begins in position %s)." % (len(element.indents), element.range.first_position.nameless_str))

    # BEGIN h  END  ₐ⟅h⟨⟩⟆ₐ
    # out[2].punctuation := in[0].punctuation
    def _unindented_block_apply(self, element) -> Element:
        new_form_element = element.parent.wrap(element, element.end, self.wrap_class)
        new_form = new_form_element.code

        punctuation = element.punctuation[0]
        new_form.remove(new_form.first) # remove BEGIN
        new_form.remove(new_form.last)  # remove END

        punctuator = Punctuator(new_form_element.code, punctuation, 1)

        return new_form_element.parent.replace(new_form_element, punctuator).next


    # BEGIN h  INDENT  END  ₐ⟅h⟨⟩ ⟆ₐ
    # out[2].punctuation := in[0].punctuation
    def _single_indented_block_apply(self, element) -> Element:
        new_form_element = element.parent.wrap(element, element.end, self.wrap_class)
        new_form = new_form_element.code

        indent  = element.indents[0]
        assert len(element.punctuation) == 2 and element.punctuation[1] == []
        punctuation = element.punctuation[0]

        new_form.remove(new_form.first) # remove BEGIN
        new_form.remove(new_form.last)  # remove END

        punctuator = Punctuator(new_form_element.code, punctuation, 1, indent)

        # new_form.remove(indent) # remove INDENT

        return new_form_element.parent.replace(new_form_element, punctuator).next

    # BEGIN h a INDENT $b INDENT c END  ₐ⟅h⟨a⟩ b c⟆ₐ
    # b  BEGIN a  :  END  ⟅a⟨⟩⟆ₐ
    # b  BEGIN  END  ⟨⟩
    # b  BEGIN  INDENT  END  error
    # out[2].punctuation := in[0].punctuation
    def _double_indented_block_apply(self, element) -> Element:
        new_form_element = element.parent.wrap(element, element.end, self.wrap_class)
        new_form = new_form_element.code


        raise NotImplementedError()

        # indent  = element.indents[0]
        # assert len(element.punctuation) == 2 and element.punctuation[1] == []
        # punctuation = element.punctuation[0]
        #
        # new_form.remove(new_form.first) # remove BEGIN
        # new_form.remove(new_form.last)  # remove END
        # head = new_form.first
        #
        # first_arg = _element_after(head)
        #
        # if first_arg is indent:
        #     pass
        # elif first_arg is indent.prev:
        #     if is_token(first_arg, TOKEN.PUNCTUATION, ':'):
        #         new_form.remove(first_arg)
        #     # else let it be
        # else:
        #     new_argseq_element = new_form.wrap(first_arg, indent.prev, ArgSeq)
        #     new_argseq_element.code.punctuation = punctuation
        #
        # new_form.remove(indent)
        # return new_form_element.next