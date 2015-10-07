from Common.Util import is_not_none
from .Node import Node, Element
from .Identifier import Identifier
from .Form import Form, PreForm
# from Semantics.Code.Symbol import Symbol
from Syntax.Punctuator import Punctuator
from Syntax.Code import Code
from Syntax.Literal import Literal
from .Tuple import Tuple, PreTuple
from .Token import Token
from Common.Errors import LycError
import Syntax._common as common

_delimiters = {
                  PreForm:("ₐ⟅", "⟆ₐ"),
                  PreTuple:("⟅", "⟆"),
                  Form:("⦅", "⦆"),
                  Tuple:("(", ")"),
                  Punctuator:('⟨', '⟩'),
                }

def lisp_printer(code_or_element) -> str:
    if isinstance(code_or_element, list):
        return (u"\n".join(lisp_printer(elm) for elm in code_or_element)) + u"\n"

    if isinstance(code_or_element, Token):
        if code_or_element.code is not None:
            return lisp_printer(code_or_element.code)
        else:
            ret = code_or_element.type.name
            if hasattr(code_or_element, 'text') and code_or_element.text is not None:
                text = code_or_element.text
                if len(text) < 32:
                    ret += "('" + text + "')"
                else:
                    ret += "('" + text[:32] + "'...)"
        return ret
    elif isinstance(code_or_element, Element):
        return lisp_printer(code_or_element.code)
    assert isinstance(code_or_element, Code)
    code = code_or_element
    if code.__class__ in _delimiters:
        left, right = _delimiters[code.__class__]
        lisp_form = left
        elms = [lisp_printer(elm) for elm in code]
        lisp_form += " ".join(elms)
        lisp_form += right
        return lisp_form
    elif isinstance(code, Identifier) or isinstance(code, Literal):
        return str(code)
    elif isinstance(code, Node):
        return "NODE:\n" + (u"\n".join(lisp_printer(elm) for elm in code)) + u"\n"
    else:
        raise LycError(None, "ERROR PRODUCING LISP FORM!")

def indented_lisp_printer(code_or_element, current_line = None) -> str:
    if current_line is None:
        current_line = [0]

    if isinstance(code_or_element, list):
        return (u"\n".join(lisp_printer(elm) for elm in code_or_element)) + u"\n"

    line_prefix = ""
    if is_not_none(code_or_element, ".range.first_position") and code_or_element.range.first_position.line > current_line[0]:
        current_line[0] = code_or_element.range.first_position.line
        line_prefix = "\n" + " " * (code_or_element.range.first_position.column - 1)

    if code_or_element.__class__ in _delimiters:
        left, right = _delimiters[code_or_element.__class__]
        lisp_form = left
        elms = [indented_lisp_printer(elm, current_line) for elm in code_or_element]
        lisp_form += " ".join(elms)
        lisp_form += right
        return line_prefix + lisp_form
    # elif isinstance(code, Literal):
    #     v = code.val
    #     if isinstance(v, basestring):
    #         return u"“" + v + u"”"
    #     else:
    #         return unicode(str(v))
    elif isinstance(code_or_element, Token):
        if code_or_element.code is not None:
            return line_prefix + indented_lisp_printer(code_or_element.code, current_line)
        else:
            ret = code_or_element.type.name
            if hasattr(code_or_element, 'text') and code_or_element.text is not None:
                text = code_or_element.text
                if len(text) < 32:
                    ret += "('" + text + "')"
                else:
                    ret += "('" + text[:32] + "'...)"
        return line_prefix + ret
    elif isinstance(code_or_element, Identifier) or isinstance(code_or_element, Literal):
        return line_prefix + str(code_or_element)
    elif isinstance(code_or_element, Node):
        node_elms = [indented_lisp_printer(elm, current_line) for elm in code_or_element]
        return line_prefix + "NODE:\n" + u"\n".join(node_elms) + u"\n"
    elif isinstance(code_or_element, Element):
        return line_prefix +indented_lisp_printer(code_or_element.code, current_line)
    else:
        raise LycError(None, "ERROR PRODUCING LISP FORM!")



common.printer = lisp_printer