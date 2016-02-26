from rmtc.Streams.StreamRange import StreamRange
from rmtc.Syntax.Node import Element

class Token(Element):
    """
    A token. Token inherits :ref:`Element` so that it is possible to have tokens reference other tokens.
    So a ``BEGIN`` token will have a pointer to the corresponding ``END`` token, and so on.
    """
    def __init__(self, type_, range:StreamRange):
        Element.__init__(self, None)
        self.type = type_
        """The type-number of the token."""
        self._range = range

    def __str__(self):
        s = "Token: %s, range=(%s‥%s)" % (self.type, repr(self.range.first_position.values), repr(self.range.position_after.values))
        if hasattr(self, 'value') and self.value is not None:
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

    def print(self):
        return self.type.name


def is_token(obj, token_type=None, token_value=None, token_text=None):
    """
    Whether the given object is a token, whose type/value/text conform to the given arguments
    (if non-null).
    """
    return isinstance(obj, Token) and \
          (token_type is None or isinstance(obj, token_type)) and \
          (token_value is None or obj.value == token_value) and \
          (token_text is None or obj.text == token_text)


