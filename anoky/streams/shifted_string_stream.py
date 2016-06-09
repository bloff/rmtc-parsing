from anoky.streams.stream_position import StreamPosition
from anoky.streams.string_stream import StringStream


class ShiftedStringStream(StringStream):

    def __init__(self, string, name="<string>", shift: int = 0):
        super().__init__(string, name)
        self.shift = shift
        self.shifted_stream_position = StreamPosition(name, 0, 1, 1, 1)

    @property
    def position(self) -> StreamPosition:
        self.shifted_stream_position.values = self.current_stream_position.values
        self.shifted_stream_position.index -= self.shift
        return self.shifted_stream_position

    @property
    def absolute_position(self) -> StreamPosition:
        return self.position
