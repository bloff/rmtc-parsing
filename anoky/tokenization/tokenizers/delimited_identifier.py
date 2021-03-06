import anoky.syntax.tokens as Tokens
from anoky.common.errors import TokenizingError
from anoky.streams.stream_position import StreamPosition
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer


class DelimitedIdentifierTokenizer(Tokenizer):
    """
    Reads identifiers surrounded by delimiters. Hence one can write identifiers with special chararacters, e.g., ``«1234 some identifier»``.
    """

    OPENING_DELIMITER = "«"
    CLOSING_DELIMITER = "»"

    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != self.__class__.OPENING_DELIMITER:
            raise TokenizingError(opening_delimiter_position, "Multiple-escape tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after


    def run(self):
        stream = self.context.stream
        value = ""
        while True:
            if stream.next_is_EOF():
                raise TokenizingError(stream.position, "Expected closing multiple-escape-delimiter «%s», matching opening delimiter «%s» at position %s." % (self.closing_delimiter, self.opening_delimiter, self.opening_delimiter_position.nameless_str))
            char = stream.read()
            if char == self.__class__.CLOSING_DELIMITER:
                yield Tokens.CONSTITUENT(value, self.opening_delimiter_position, stream.copy_absolute_position())
                # yield Tokens.END_MACRO(opening_string_token, self.closing_delimiter, stream.position_of_unread(), stream.position)
                return
            else:
                value += char

