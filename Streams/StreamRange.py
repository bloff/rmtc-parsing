from Streams.StreamPosition import StreamPosition


class StreamRange(object):
    """
    Represents a contiguous interval in a stream.
    """
    def __init__(self, first_position:StreamPosition=None, position_after:StreamPosition=None):
        if first_position is not None:
            assert position_after is not None
            assert first_position.stream_name == position_after.stream_name
        self.first_position = first_position
        """
        The position of the first character in the range.
        """
        self.position_after = position_after
        """
        The position of the character immediately after the last character of the range. Equal to first_position if the range has length 0.
        """

    @property
    def stream_name(self):
        return self.first_position.stream_name if self.first_position is not None else None

    # Updates the current range to include the given range,
    # provided that the given range belongs to the same filename;
    def update(self, range):
        if range.stream_name is None:
            return
        elif self.stream_name is None:
            self.first_position = range.first_position
            self.position_after = range.position_after
        elif self.stream_name != range.stream_name:
            return

        self.first_position = self.first_position if self.first_position.index <= range.first_position.index else range.first_position
        self.position_after = self.position_after if self.position_after.index >= range.position_after.index else range.position_after

    def __str__(self):
        first_pos = self.first_position.nameless_str if self.first_position is not None else "?"
        pos_after = self.position_after.nameless_str if self.first_position is not None else "?"
        return "%s:(%s‥%s)" %(self.stream_name, first_pos, pos_after)