from Common.StringStuff import EOF
from Streams import StreamPosition


class WrongSeqError(Exception):
    pass


class CharacterStream(object):
    def __init__(self, name = None):
        self.name = name

    def read(self) -> str:
        """
        Reads a character from the stream.
        :return: The character that was read.
        """
        raise NotImplementedError()

    def unread(self, n:int = 1) -> str:
        """
        Unreads a character from a stream.
        :param n: The number of characters to unread.
        :return: The string which was unread.
        """
        raise NotImplementedError()


    def unread_seq(self, seq:str):
        """
        Unreads a character from a stream.
        :param seq: The sequence of characters to unread.
        :return: The string which was unread.
        :raises WrongSeqError when the sequence that was unread does not match the given string.
        """
        unread = self.unread(len(seq))
        if unread != seq:
            raise WrongSeqError("Tried to unread sequence %s, but got %s." % ( repr(seq), repr(unread)))

    def peek(self):
        """
        Returns the character that the stream will read next. Or EOF if it is the end of file.
        :return:
        """
        char = self.read()
        self.unread()
        return char

    def prev(self):
        """
        Returns the character that was read previously.
        :return:
        """
        char = self.unread()
        self.read()
        return char


    def next_is_EOF(self) -> bool:
        """
        Returns whether the next call to read() will produce EOF.
        """
        return self.peek() == EOF

    def prev_is_EOF(self) -> bool:
        """
        Returns whether the last call to read() has produced EOF.
        """
        return self.position.index > 0 and self.prev() == EOF


    @property
    def position(self) -> StreamPosition:
        """
        Returns a StreamPosition instance representing the current (relative) position of the stream. This should be read-only.
        If you want a position that you can keep and modify yourself, use the copy_position method.
        """
        raise NotImplementedError()

    @property
    def absolute_position(self) -> StreamPosition:
        """
        Returns a StreamPosition instance representing the current absolute position of the stream. This should be read-only.
        If you want a position that you can keep and modify yourself, use the copy_position method.
        """
        raise NotImplementedError()


    def position_of_unread(self, n:int=1) -> StreamPosition:
        self.unread(n)
        pos = self.copy_position()
        while n > 0:
            self.read()
            n -= 1
        return pos

    def position_of_unread_seq(self, seq:str) -> StreamPosition:
        self.unread_seq(seq)
        pos = self.copy_position()
        n = len(seq)
        while n > 0:
            self.read()
            n -= 1
        return pos

    def absolute_position_of_unread(self, n:int=1) -> StreamPosition:
        self.unread(n)
        pos = self.copy_absolute_position()
        while n > 0:
            self.read()
            n -= 1
        return pos

    def absolute_position_of_unread_seq(self, seq:str) -> StreamPosition:
        self.unread_seq(seq)
        pos = self.copy_absolute_position()
        n = len(seq)
        while n > 0:
            self.read()
            n -= 1
        return pos


    def copy_position(self) -> StreamPosition:
        """
        Returns a fresh copy of a StreamPosition instance representing the current (relative) position of the stream.
        """
        return self.position.copy()

    def copy_absolute_position(self) -> StreamPosition:
        """
        Returns a fresh copy of a StreamPosition instance representing the current absolute position of the stream.
        """
        return self.absolute_position.copy()

    @property
    def index(self) -> int:
        """
        Returns the index (or 'offset from start') of the current position of the stream.
        """
        return self.position.index

    @property
    def line(self) -> int:
        """
        Returns the line number of the current position of the stream.
        """
        return self.position.line

    @property
    def column(self) -> int:
        """
        Returns the column number of the current position of the stream.
        """
        return self.position.column

    @property
    def visual_column(self) -> int:
        """
        Returns the visual-column number of the current position of the stream.
        """
        return self.position.visual_column