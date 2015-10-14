from Streams.StreamPosition import StreamPosition
from Streams.StreamRange import StreamRange
from enum import Enum
from Syntax.Node import Element


class TOKEN(Enum):
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

class Token(Element):
    """
    A token.
    """
    def __init__(self, type_:TOKEN, range:StreamRange):
        Element.__init__(self, None)
        self.type = type_
        """The type of the token."""
        self._range = range

    def __str__(self):
        s = "Token: %s, range=(%s‥%s)" % (self.type, repr(self.range.first_position.values), repr(self.range.position_after.values))
        if hasattr(self, 'value'):
            if isinstance(self.value, str): r = repr(self.value)[1:-1]
            else: r = self.value
            s += ', value=“%s”' % r
        elif hasattr(self, 'text'): s += ', text=“%s”' % self.text

        s += ')'
        return s

    @property
    def range(self) -> StreamRange:
        """The range where the token appears, if no ``Code`` instance is
        associated with this token (when seen as an ``Element``. Otherwise,
        the range of that ``Code`` instance."""
        if self.code is not None:
            return self.code.range
        else:
            return self._range

    @range.setter
    def range(self, value):
        self._range = value


class token_BEGIN(Token):
    """
    A token representing the beginning of a block of code.
    """
    def __init__(self, position:StreamPosition):
        Token.__init__(self, TOKEN.BEGIN, StreamRange(position, position))
        self.end = None
        """The corresponding END token."""
        self.indents = []
        """A list of INDENT (indentation) tokens for this block of code."""
        self.punctuation = [[]]
        """A list containing, for each INDENT token, a list of PUNCTUATION tokens appearing before it in this block of code."""

    def add_indent(self, indent):
        self.indents.append(indent)
        self.punctuation.append([])

    def add_punctuation(self, punctuation_token):
        self.punctuation[-1].append(punctuation_token)


class token_END(Token):
    """
    A token representing the end of a block of code.
    """
    def __init__(self, begin_token, position:StreamPosition):
        Token.__init__(self, TOKEN.END, StreamRange(position, position))
        self.begin = begin_token
        begin_token.end = self


class token_INDENT(Token):
    """
    A token representing an indentation inside a block of code.
    """
    def __init__(self, begin_token, position:StreamPosition):
        assert isinstance(begin_token, token_BEGIN)
        Token.__init__(self, TOKEN.INDENT, StreamRange(position, position))
        self.begin = begin_token
        begin_token.add_indent(self)

class token_PUNCTUATION(Token):
    """
    A punctuation token.
    """
    def __init__(self, begin_token, value:str, first_position:StreamPosition, position_after:StreamPosition):
        assert isinstance(begin_token, token_BEGIN)
        Token.__init__(self, TOKEN.PUNCTUATION, StreamRange(first_position, position_after))
        self.begin = begin_token
        self.value = value
        begin_token.add_punctuation(self)


class token_CONSTITUENT(Token):
    """
    A constituent token, usually a string of consecutive constituent sequences (as defined by the readtable).
    """
    def __init__(self, value:str, first_position:StreamPosition, position_after:StreamPosition, meta=None):
        Token.__init__(self, TOKEN.CONSTITUENT, StreamRange(first_position, position_after))
        self.value = value
        self.meta = meta


class token_BEGIN_MACRO(Token):
    """
    A token representing the beginning of a reader macro (such as '(', '[', '#', etc)
    """
    def __init__(self, text:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, TOKEN.BEGIN_MACRO, StreamRange(first_position, position_after))
        self.text = text

class token_END_MACRO(Token):
    """
    A token representing the end of a reader macro (such as ')', ']', etc)
    """
    def __init__(self, begin_token, text:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self,TOKEN.END_MACRO, StreamRange(first_position, position_after))
        self.text = text
        self.begin = begin_token
        begin_token.end = self

class token_STRING(Token):
    """
    A token representing a string of characters (usually appears between the BEGIN_MACRO and END_MACRO tokens
    of a reader macro for strings.
    """
    def __init__(self, value:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, TOKEN.STRING, StreamRange(first_position, position_after))
        self.value = value

class token_COMMENT(Token):
    """
    A token representing a comment.
    """
    def __init__(self, value:str, first_position:StreamPosition, position_after:StreamPosition):
        Token.__init__(self, TOKEN.COMMENT, StreamRange(first_position, position_after))
        self.value = value

def is_token(obj, token_type=None, token_value=None, token_text=None):
    """
    Whether the given object is a token, whose type/value/text conform to the given arguments
    (if non-null).
    """
    return isinstance(obj, Token) and \
          (token_type is None or obj.type == token_type) and \
          (token_value is None or obj.value == token_value) and \
          (token_text is None or obj.text == token_text)


