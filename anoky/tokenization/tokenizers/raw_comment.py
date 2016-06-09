from anoky.common.errors import TokenizingError
from anoky.streams.stream_position import StreamPosition
from anoky.tokenization import tokenization_context
from anoky.tokenization.tokenizer import Tokenizer
import anoky.syntax.tokens as Tokens


class RawCommentTokenizer(Tokenizer):
    """
    Reads comments without interpolated code.
    """

    OPENING_DELIMITER = '#'

    def __init__(self, context: tokenization_context, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after


    def run(self):
        stream = self.context.stream

        # If the macro tokenizer was called with an unkown opening delimiter sequence, mark it as an error and exit
        if self.opening_delimiter != self.__class__.OPENING_DELIMITER:
            yield Tokens.ERROR(self.opening_delimiter, self.opening_delimiter_position,
                               self.opening_delimiter_position_after,
                               "Comment tokenizer called with unknown opening sequence “%s”" % self.opening_delimiter)
            return


        stream.push()
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
            value += stream.read()
