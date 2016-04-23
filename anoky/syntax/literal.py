from anoky.streams.stream_range import StreamRange
from anoky.syntax.code import Code


class Literal(Code):
    """
    A ``Code`` type representing a value.

    :param type: Some instance representing the type of the literal. type(value) is computed if None is given.
    :param value: The value associated with the literal.
    :param range: The ``StreamRange`` of where this literal appears.
    """
    def __init__(self, value, type_=None, range: StreamRange = None):
        super(Literal, self).__init__()
        self.type = type_ or type(value)
        """Some instance representing the type of the literal."""
        self.value = value
        """The value associated with the literal."""
        self.range = range if range is not None else StreamRange()


    def __str__(self):
        if isinstance(self.value, int):
            return str(self.value)
        elif isinstance(self.value, str):
            return '"%s"' % repr(self.value)[1:-1]
        else:
            # FIXME?
            return str(self.value)


    def copy(self):
        return Literal(self.value, self.type, self.range)