
from anoky.Common.StringStuff import EOF
from anoky.Streams.CharacterStream import CharacterStream
from anoky.Streams.StreamPosition import StreamPosition


class IndentedCharacterStream(CharacterStream):
    """
    A character stream for parsing with indentation by ignoring leading whitespace.
   """

    def __init__(self, parent:CharacterStream):
        CharacterStream.__init__(self, parent.name)

        # The stream from which we obtain the (absolute) characters.
        self._parent = parent
        # Keeps the first StreamPosition_ of the various indentation levels
        self._stack = [parent.copy_position()]

        # Keeps the StreamPosition_ of the current character, relative to the position in the top of the stack
        self.current_relative_position = StreamPosition(self.name, 0, 1, 1, 1)

        # Remembers whether the substream has finished reading
        self.relative_eof = False

    def unread(self, n:int=1) -> str:
        """
        Unreads characters from the current substream. Raises an error if an attempt is made
        at unreading beyond the beginning.

        :param n: The number of characters to unread.
        :type n: int
        """
        if n > 1:
            last = self.unread()
            assert last != EOF
            prev = self.unread(n-1)
            return prev + last
        else:
            if self.current_relative_position.index <= 0:
                raise Exception("Tried to unread character beyond beginning of (sub)stream.")

            if self.relative_eof:
                self.relative_eof = False
                self.current_relative_position.index -= 1
                self._update_relative_position()
                return EOF
            else:
                char = None
                current_starting_column = self._stack[-1].visual_column
                while True:
                    char = self._parent.unread()
                    if self._parent.position.visual_column < current_starting_column:
                        if char == '\n':
                            break
                        else: continue
                    else:
                        break

                self._update_relative_position()
                self.current_relative_position.index -= 1

                return char

    def read(self) -> str:
        """
        Reads the next character of the current substream. Raises an error if an attempt is made at reading beyond the EOF.

        :rtype : str
        :returns The next character in the current substream, or EOF if there are no more characters.
        """

        if self.relative_eof:
            raise Exception("Tried to read character beyond EOF.")

        char = None
        current_starting_column = self._stack[-1].visual_column
        while self._parent.position.visual_column < current_starting_column:
            char = self._parent.read()
            if char == ' ':
                continue
            elif char == '\n':
                    break
            else:
                self._parent.unread()
                self._yield_eof()
                return EOF

        if char != '\n': char = self._parent.read()

        if char == '\n' and not self._next_line_check(current_starting_column):
            # if we find a newline character, and the next line
            # is either a blank line, or a line whose first non-whitespace
            # character begins at or after "current_starting_column",
            # then we yield the newline character to the top reader
            # but if we find a newline character preceeding a line whose first
            # non-whitespace begins before `current_starting_column`, then
            # we yield EOF to the top reader
            self._parent.unread()
            self._yield_eof()
            return EOF

        self._update_relative_position()
        self.current_relative_position.index += 1
        return char

    def _yield_eof(self):
        self.relative_eof = True
        self.current_relative_position.index += 1
        self.current_relative_position.line = -1
        self.current_relative_position.column = -1
        self.current_relative_position.visual_column = -1

    def _next_line_check(self, current_starting_column):
        # assumes that a \n was just read by parent
        # returns True iff
        # the current line is empty, or
        # the first non-whitespace character of this line
        #  begins after `current_starting_column`
        while True:
            char = self._parent.read()
            if char == ' ':
                continue
            elif char == '\n' or char == EOF: # if the line was empty
                # unread the entire line
                self._parent.unread()
                self._parent.unread(self._parent.column - 1)
                return True
            else:
                first_non_whitespace_column = self._parent.column - 1
                self._parent.unread(first_non_whitespace_column)
                return first_non_whitespace_column >= current_starting_column


    @property
    def position(self) -> StreamPosition:
        """
        Returns the current relative position (the position relative to the last ``push`` operation).
        """
        return self.current_relative_position


    def push(self):
        self._stack.append(self._parent.copy_position())
        self._update_relative_position()
        self.current_relative_position.index = 0
        self.relative_eof = self._parent.prev_is_EOF()

    def pop(self):
        self._stack.pop()
        self._update_relative_position()
        self.current_relative_position.index = 0 # no unread to previous-level characters
        self.relative_eof = self._parent.prev_is_EOF()

    def _update_relative_position(self):
        fpos = self._stack[-1]
        cpos = self._parent.position
        crpos = self.current_relative_position
        crpos.line = cpos.line - fpos.line + 1
        crpos.column = max(cpos.column - fpos.visual_column + 1, 1)
        crpos.visual_column = max(cpos.visual_column - fpos.visual_column + 1, 1)


    @property
    def absolute_position(self) -> StreamPosition:
        """
        Returns the current absolute position (the position of the current character in the parent stream).
        """
        return self._parent.absolute_position



if __name__ == "__main__":
    from anoky.Streams.StringStream import StringStream
    from anoky.Streams.StreamPosition import StreamPosition


    string = """
a b
    c d


    e f
g h
"""
    pstream = StringStream(string)

    import random


    istream = IndentedCharacterStream(pstream)

    eof1 = False

    while True:
        rpos = istream.copy_position()
        apos = istream.copy_absolute_position()
        char = istream.read()
        if char == 'c' and len(istream._stack) == 1:
            istream.unread()
            istream.push()
            print("#"* 10 + "   PUSH   " + "#" * 10)
            continue
        if char == EOF:
            if not eof1:
                eof1 = True
                istream.pop()
                print("#"* 10 + "   POP   " + "#" * 10)
                continue
            else:
                print("#"* 10 + "   EOF   " + "#" * 10)
                break


        print("char %s: abs%s  rel%s" % (repr(char), repr(apos.values), repr(rpos.values)))

        if random.randint(0,4) == 0:
            unreadcount = min(random.randint(0, 5), istream.position.index)
            if unreadcount > 0:
                print("#"* 10 + "   UNREAD %d  " % unreadcount + "#" * 10)
                istream.unread(unreadcount)


