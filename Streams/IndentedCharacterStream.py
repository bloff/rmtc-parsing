from Common.StringStuff import EOF
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Streams._common import StreamError


class IndentedCharacterStream(CharacterStream):

    def __init__(self, parent:CharacterStream):
        CharacterStream.__init__(self, parent.name)
        self.parent = parent
        # The stack keeps the first position of the various indentation levels
        self.stack = [parent.copy_position()]
        self.current_relative_position = StreamPosition(self.name, 0, 1, 1, 1)
        self.relative_eof = False

    def unread(self, n:int=1) -> str:
        if n > 1:
            last = self.unread()
            assert last != EOF
            prev = self.unread(n-1)
            return prev + last
        else:
            if self.current_relative_position.index <= 0:
                raise StreamError("Tried to unread character beyond beginning of (sub)stream.")

            if self.relative_eof:
                self.relative_eof = False
                self.current_relative_position.index -= 1
                self._update_relative_position()
                return EOF
            else:
                char = None
                current_starting_column = self.stack[-1].visual_column
                while True:
                    char = self.parent.unread()
                    if self.parent.position.visual_column < current_starting_column:
                        if char == '\n':
                            break
                        else: continue
                    else:
                        break

                self._update_relative_position()
                self.current_relative_position.index -= 1

                return char

    def read(self) -> str:
        if self.relative_eof:
            raise StreamError("Tried to read character beyond EOF.")

        char = None
        current_starting_column = self.stack[-1].visual_column
        while self.parent.position.visual_column < current_starting_column:
            char = self.parent.read()
            if char == ' ':
                continue
            elif char == '\n':
                    break
            else:
                self.parent.unread()
                self._yield_eof()
                return EOF

        if char != '\n': char = self.parent.read()

        if char == '\n' and not self.next_line_check(current_starting_column):
            # if we find a newline character, and the next line
            # is either a blank line, or a line whose first non-whitespace
            # character begins at or after "current_starting_column",
            # then we yield the newline character to the top reader
            # but if we find a newline character preceeding a line whose first
            # non-whitespace begins before `current_starting_column`, then
            # we yield EOF to the top reader
            self.parent.unread()
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

    def next_line_check(self, current_starting_column):
        # assumes that a \n was just read by parent
        # returns True iff
        # the current line is empty, or
        # the first non-whitespace character of this line
        #  begins after `current_starting_column`
        while True:
            char = self.parent.read()
            if char == ' ':
                continue
            elif char == '\n' or char == EOF: # if the line was empty
                # unread the entire line
                self.parent.unread()
                self.parent.unread(self.parent.column - 1)
                return True
            else:
                first_non_whitespace_column = self.parent.column - 1
                self.parent.unread(first_non_whitespace_column)
                return first_non_whitespace_column >= current_starting_column


    @property
    def position(self) -> StreamPosition:
        return self.current_relative_position



    def push(self):
        self.stack.append(self.parent.copy_position())
        self._update_relative_position()
        self.current_relative_position.index = 0
        self.relative_eof = self.parent.prev_is_EOF()

    def pop(self):
        self.stack.pop()
        self._update_relative_position()
        self.current_relative_position.index = 0 # no unread to previous-level characters
        self.relative_eof = self.parent.prev_is_EOF()

    def _update_relative_position(self):
        fpos = self.stack[-1]
        cpos = self.parent.position
        crpos = self.current_relative_position
        crpos.line = cpos.line - fpos.line + 1
        crpos.column = max(cpos.column - fpos.visual_column + 1, 1)
        crpos.visual_column = max(cpos.visual_column - fpos.visual_column + 1, 1)


    @property
    def absolute_position(self) -> StreamPosition:
        return self.parent.absolute_position



if __name__ == "__main__":
    from Streams import StringStream, StreamPosition

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
        if char == 'c' and len(istream.stack) == 1:
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


