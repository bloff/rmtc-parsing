from rmtc.Common.Util import is_not_none
from rmtc.Syntax.Form import Form
from rmtc.Syntax.Node import Element, Node
from rmtc.Syntax.PreForm import PreForm
from rmtc.Syntax.Punctuator import Punctuator
from rmtc.Syntax.Code import Code
from rmtc.Syntax.Tuple import Tuple
from rmtc.Syntax.PreTuple import PreTuple
from rmtc.Syntax.Token import Token

_delimiters = {
                  PreForm:("⟅", "⟆", False),
                  PreTuple:("⟅", "⟆", True),
                  Form:("(", ")", False),
                  Tuple:("(", ")", True),
                  Punctuator:('⟨', '⟩', False),
                }

# TODO: refactor all __str__ and __repr__ methods to allow for each language to choose its own representation

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
        left, right, comma_separated = _delimiters[code.__class__]
        lisp_form = left
        elms = [lisp_printer(elm) for elm in code]
        lisp_form += (", " if comma_separated else " ").join(elms)
        if len(elms) == 1 and comma_separated: lisp_form += ","
        lisp_form += right
        return lisp_form
    elif isinstance(code, Node):
        return "NODE:\n" + (u"\n".join(lisp_printer(elm) for elm in code)) + u"\n"
    else:
        return str(code)
        # raise ErrorInPosition(None, "ERROR PRODUCING LISP FORM!")

def succinct_lisp_printer(code_or_element, max_length:int=40) -> str:
    s = lisp_printer(code_or_element)
    if max_length >= len(s):
        return s
    else:
        return s[0:max_length] + "..."

def indented_lisp_printer(code_or_element, current_line = None) -> str:
    if current_line is None:
        current_line = [0]

    if isinstance(code_or_element, list):
        return (u"\n".join(lisp_printer(elm) for elm in code_or_element)) + u"\n"

    line_prefix = ""
    if is_not_none(code_or_element, ".range.first_position.line") and code_or_element.range.first_position.line > current_line[0]:
        current_line[0] = code_or_element.range.first_position.line
        line_prefix = "\n" + " " * (code_or_element.range.first_position.column - 1)

    if code_or_element.__class__ in _delimiters:
        left, right, comma_separated = _delimiters[code_or_element.__class__]
        lisp_form = left
        elms = [indented_lisp_printer(elm, current_line) for elm in code_or_element]
        lisp_form += (", " if comma_separated else  " ").join(elms)
        lisp_form += right
        return line_prefix + lisp_form
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
    elif isinstance(code_or_element, Node):
        node_elms = [indented_lisp_printer(elm, current_line) for elm in code_or_element]
        return line_prefix + "NODE:\n" + u"\n".join(node_elms) + u"\n"
    elif isinstance(code_or_element, Element):
        return line_prefix +indented_lisp_printer(code_or_element.code, current_line)
    else:
        return line_prefix + str(code_or_element)
        # raise ErrorInPosition(None, "ERROR PRODUCING LISP FORM!")
