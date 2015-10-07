from Common.StringStuff import EOF, special_visual_width_characters
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Streams._common import StreamError


class StringStream(CharacterStream):

    def __init__(self, string, name="<string>"):
        CharacterStream.__init__(self, name)
        self.string = string
        self.current_stream_position = StreamPosition(self.name, 0, 1, 1, 1)
        self.stream_positions = [self.current_stream_position]
        self.eof = False


    def read(self) -> str:
        if self.eof:
            raise StreamError("Tried to read character beyond EOF.")
        idx = self.current_stream_position.index
        if idx >= len(self.string):
            self._update_position_read(EOF) # sets self.eof to True if necessary
            self.eof = True
            return EOF
        chr = self.string[idx]
        self._update_position_read(chr)
        return chr

    def _update_position_read(self, chr):
        cpos = self.current_stream_position
        # if we had previously calculated and buffered the current stream position
        if cpos.index + 1 < len(self.stream_positions):
            self.current_stream_position = self.stream_positions[cpos.index + 1]
        else:
            if chr == '\n':
                pos = StreamPosition(self.name, cpos.index + 1, cpos.line + 1, 1, 1)
            elif chr != EOF:
                if chr in special_visual_width_characters:
                    pos = StreamPosition(self.name,
                                         cpos.index + 1,
                                         cpos.line,
                                         cpos.column + 1,
                                         cpos.visual_column + special_visual_width_characters[chr])
                else:
                    pos = StreamPosition(self.name, cpos.index + 1, cpos.line, cpos.column + 1, cpos.visual_column + 1)
            else:
                pos = StreamPosition(self.name, cpos.index + 1, -1, -1, -1)
            self.current_stream_position = pos
            self.stream_positions.append(pos)

    def unread(self, n:int=1) -> str:
        if self.current_stream_position.index < n:
            raise StreamError("Tried to unread beyond beginning of stream.")

        start_index = self.current_stream_position.index - n
        ret = self.string[start_index:self.current_stream_position.index]
        self.current_stream_position = self.stream_positions[start_index]
        self.eof = self.current_stream_position.line == -1
        return ret


    def prev(self):
        assert self.current_stream_position.index > 0
        if self.eof:
            return EOF
        else:
            return self.string[self.current_stream_position.index - 1]

    @property
    def position(self) -> StreamPosition:
        return self.current_stream_position

    @property
    def absolute_position(self) -> StreamPosition:
        return self.current_stream_position



if __name__ == "__main__":
    string = """
a b
    c d
    e f
g h
"""
    pstream = StringStream(string)

    char = None
    while char != EOF:
        pos = pstream.copy_position()
        char = pstream.read()
        print("char %s: %s" %(repr(char), repr(pos.values)))