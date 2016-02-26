from enum import Enum

from rmtc.Streams.StreamPosition import StreamPosition
from rmtc.Streams.StreamRange import StreamRange
from rmtc.Syntax.Token import Token, is_token


class _TokenTypes(Enum):
    """
    Enumeration of token types.
    """
    WHITESPACE = 0
    BEGIN = 1
    END = 2
    INDENT = 3
    CONSTITUENT = 4
    BEGIN_MACRO = 5
    END_MACRO = 6
    STRING = 7
    COMMENT = 8
    PUNCTUATION = 9

class BEGIN(Token):
    """
    A token representing the beginning of a segment.
    """
    def __init__(self, position:StreamPosition):
        Token.__init__(self, _TokenTypes.BEGIN, StreamRange(position, position))
        self.end = None
        """The corresponding END token."""
        self.indents = []
        """A list of INDENT (indentation) tokens for this block of code."""

    def add_indent(self, indent):
        self.indents.append(indent)

    def find_punctuation(self, value, before=None):
        if before is None: before = self.end
        punct = None
        elm = self.next
        while elm is not None and elm is not before:
            if is_token(elm, PUNCTUATION, ':'):
                punct = elm
                break
            elm = elm.next
        return punct

    # def add_punctuation(self, punctuation_token):
    #     self.punctuation.append(punctuation_token)


class END(Token):
    """
    A token representing the end of a segment.
    """
    def __init__(self, begin_token, position:StreamPosition):
        Token.__init__(self, _TokenTypes.END, StreamRange(position, position))
        self.begin = begin_token
        begin_token.end = self


class INDENT(Token):
    """
    A token representing an indentation inside a segment.
    """
    def __init__(self, begin_token, position:StreamPosition):
        assert isinstance(begin_token, BEGIN)
        Token.__init__(self, _TokenTypes.INDENT, StreamRange(position, position))
        self.begin = begin_token
        begin_token.add_indent(self)

class PUNCTUATION(Token):
    """
    A punctuation token.
    """
    def __init__(self, begin_token, value:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, _TokenTypes.PUNCTUATION, StreamRange(first_position, position_after))
        self.begin = begin_token
        self.value = value

    def print(self):
        return "'%s'" % self.value


class ARGBREAK(PUNCTUATION):
    """
    A generated punctuation token meant to denote an argument break.
    """
    def __init__(self):
        PUNCTUATION.__init__(self, None, None, None, None)

    def print(self):
        return "ARGBREAK"



class CONSTITUENT(Token):
    """
    A constituent token, usually a string of consecutive constituent sequences (as defined by the readtable).
    """
    def __init__(self, value:str, first_position:StreamPosition, position_after:StreamPosition, meta=None):
        Token.__init__(self, _TokenTypes.CONSTITUENT, StreamRange(first_position, position_after))
        self.value = value
        self.meta = meta


class BEGIN_MACRO(Token):
    """
    A token representing the beginning of a reader macro (such as '(', '[', '#', etc)
    """
    def __init__(self, text:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, _TokenTypes.BEGIN_MACRO, StreamRange(first_position, position_after))
        self.text = text

class END_MACRO(Token):
    """
    A token representing the end of a reader macro (such as ')', ']', etc)
    """
    def __init__(self, begin_token, text:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self,_TokenTypes.END_MACRO, StreamRange(first_position, position_after))
        self.text = text
        self.begin = begin_token
        begin_token.end = self

class STRING(Token):
    """
    A token representing a string of characters (usually appears between the BEGIN_MACRO and END_MACRO tokens
    of a reader macro for strings.
    """
    def __init__(self, value:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, _TokenTypes.STRING, StreamRange(first_position, position_after))
        self.value = value

class COMMENT(Token):
    """
    A token representing a comment.
    """
    def __init__(self, value:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, _TokenTypes.COMMENT, StreamRange(first_position, position_after))
        self.value = value

