from typing import Union
from Common.Instance import Instance
from Syntax.Code import Code
from Syntax.Form import Form
from Syntax.Identifier import Identifier
from Syntax.Literal import Literal
from Syntax.Node import Element
from Syntax.Tuple import Tuple

def _identifier_eq(name, semantic_extra, equal_to_name, equal_to_semantic_extra):
    return ((equal_to_semantic_extra is None or semantic_extra == equal_to_semantic_extra) and
            name == equal_to_name)

def get_code(code_or_element: Union[Code, Element]) -> Code:
    if isinstance(code_or_element, Code):
        return code_or_element
    else:
        assert isinstance(code_or_element, Element)
        return code_or_element.code


def is_identifier(
        code_or_element: Union[Code, Element],
        name:str=None
        ) -> bool:
    if code_or_element is None: return False
    code = get_code(code_or_element)
    if name is None:
        return isinstance(code, Identifier)
    else:
        if not isinstance(code, Identifier): return False
        name, semantic_extra = Identifier.split_name(name)
        return _identifier_eq(code.name, code.semantic_extra, name, semantic_extra)


def identifier_in(arg: Union[Code, Element, str], collection_of_str):
    if isinstance(arg, str):
        name, syntactic_extra, semantic_extra = Identifier.split_name(arg)
        for itm in collection_of_str:
            equal_to_name, equal_to_semantic_extra = Identifier.split_name(itm)
            if _identifier_eq(name, syntactic_extra, semantic_extra, equal_to_name, equal_to_semantic_extra ):
                return True
        return False
    else:
        if arg is None: return False
        code = get_code(arg)
        return any(is_identifier(code, name) for name in collection_of_str)

def is_literal(
        code_or_element: Union[Code, Element],
        type:Instance=None
        ) -> bool:
    if code_or_element is None: return False
    code = get_code(code_or_element)
    if type is None:
        return isinstance(code, Literal)
    else:
        return isinstance(code, Literal) and code.type is type


def is_form(
        code_or_element: Union[Code, Element],
        form_head_identifier_name:str=None
        ) -> bool:
    if code_or_element is None: return False
    code = get_code(code_or_element)
    if form_head_identifier_name is None:
        return isinstance(code, Form)
    else:
        return isinstance(code, Form) and is_identifier(code.first, form_head_identifier_name)


def is_tuple(code_or_element: Union[Code, Element]) -> bool:
    if code_or_element is None: return False
    code = get_code(code_or_element)
    return isinstance(code, Tuple)
