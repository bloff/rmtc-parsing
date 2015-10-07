class StreamPosition(object):
    def __init__(self, stream_name:str, *args):
        self.stream_name = stream_name

        if len(args) == 0:
            args = [-1, 0, 0, 0]
        elif len(args) == 1:
            assert isinstance(args[0], tuple)
            args = args[0]

        assert len(args) == 4

        self.index = args[0]
        self.line = args[1]
        self.column = args[2]
        self.visual_column = args[3]

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

