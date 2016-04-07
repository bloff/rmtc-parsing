from anoky.common.errors import TokenizingError
from anoky.Streams.StreamPosition import StreamPosition
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

        if opening_delimiter != self.__class__.OPENING_DELIMITER:
            raise TokenizingError(opening_delimiter_position, "Raw-comment tokenizer called with unknown opening sequence “%s”. Expected “%s”." % (opening_delimiter, self.__class__.OPENING_DELIMITER))

        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after


    def run(self):
        stream = self.context.stream

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
