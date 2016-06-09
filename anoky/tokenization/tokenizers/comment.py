import anoky.syntax.tokens as Tokens
from anoky.common.errors import TokenizingError
from anoky.streams.stream_position import StreamPosition
from anoky.tokenization.readtable import RT
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer
from anoky.tokenization.tokenizers import util


class CommentTokenizer(Tokenizer):
    """
    Reads comments with interpolated code.

    See `<https://bloff.github.io/lyc/2015/10/04/lexer-3.html>`_.
    """

    OPENING_DELIMITER = '##'
    CLOSING_DELIMITER = '<|'

    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after

        assert len(self.__class__.CLOSING_DELIMITER) == 1 # TODO: handle larger closing delimiters?


    def run(self):
        stream = self.context.stream

        # If the macro tokenizer was called with an unkown opening delimiter sequence, mark it as an error and exit
        if self.opening_delimiter != self.__class__.OPENING_DELIMITER:
            yield Tokens.ERROR(self.opening_delimiter, self.opening_delimiter_position,
                               self.opening_delimiter_position_after,
                               "Comment tokenizer called with unknown opening sequence “%s”" % self.opening_delimiter)
            return

        stream.push()
        seen_escape = False

        opening_comment_token = Tokens.BEGIN_MACRO(self.__class__.OPENING_DELIMITER, self.opening_delimiter_position, self.opening_delimiter_position_after)
        yield opening_comment_token

        value = ""
        value_first_position = stream.copy_absolute_position()
        while True:
            if stream.next_is_EOF():
                yield Tokens.COMMENT(value, value_first_position, stream.copy_absolute_position())
                yield Tokens.END_MACRO(opening_comment_token, "", stream.copy_absolute_position(), stream.copy_absolute_position())
                stream.pop()
                return
            char = stream.read()
            if char == '\\':
                if seen_escape: value += '\\'
                else: seen_escape = True
            else:
                if seen_escape:
                    if char == self.__class__.CLOSING_DELIMITER: value += self.__class__.CLOSING_DELIMITER
                    elif char == '$': value += '$'
                    else:
                        yield Tokens.COMMENT(value, value_first_position, stream.absolute_position_of_unread())
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                        yield Tokens.ERROR(char, stream.absolute_position_of_unread(), stream.copy_absolute_position(),
                                           "Unknown escape code sequence “%s”." % char)
                    seen_escape = False
                else:
                    if char == self.__class__.CLOSING_DELIMITER:
                        yield Tokens.COMMENT(value, value_first_position, stream.absolute_position_of_unread())
                        yield Tokens.END_MACRO(opening_comment_token, self.__class__.CLOSING_DELIMITER, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                        stream.pop()
                        return
                    elif char == '$':
                        yield Tokens.COMMENT(value, value_first_position, stream.absolute_position_of_unread())
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                        for token in util.interpolation(self.context):
                            yield token

                    else: value += char

