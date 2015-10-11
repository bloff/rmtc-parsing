class StreamPosition(object):
    """
    A class representing a position in a stream.
    """
    def __init__(self, stream_name:str, *args):
        """
        Initializer.

        :param stream_name: The name of the stream
        :type stream_name: str
        :param args:
            Either:
               * Not given, equivalent to (-1, 0, 0, 0)
               * A 4-tuple containing the index, line, column and visual_column values.
               * The 4 values given as separate parameters
        :return: A StreamPosition
        """
        self.stream_name = stream_name
        """The name of the stream."""

        if len(args) == 0:
            args = [-1, 0, 0, 0]
        elif len(args) == 1:
            assert isinstance(args[0], tuple)
            args = args[0]

        assert len(args) == 4

        self.index = args[0]
        """The number of characters between the start of the stream and the position."""
        self.line = args[1]
        """The line number of the position."""
        self.column = args[2]
        """The column number of the position."""
        self.visual_column = args[3]
        """The visual-column number of the position (for variable-width characters, this might be different of the column number)."""

    def __cmp__(self, other):
        if self.index < other.index: return -1
        elif self.index > other.index: return 1
        else: return 0

    @property
    def nameless_str(self):
        return "%d:%d" %( self.line, self.column )

    @property
    def values(self):
        return self.index, self.line, self.column, self.visual_column

    @values.setter
    def values(self, values:tuple):
        self.index, self.line, self.column, self.visual_column = values

    def copy(self):
        return StreamPosition(self.stream_name, self.values)

    def __str__(self):
        return "%s:%d:%d" %( self.stream_name, self.line, self.column)

    def __repr__(self):
        return "StreamPosition(%s, %d, %d, %d, %d)" %( self.stream_name, self.index, self.line, self.column, self.visual_column )

