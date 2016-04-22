from anoky.common.errors import TokenizingError
from anoky.streams.stream_position import StreamPosition
from anoky.streams.stream_range import StreamRange
from anoky.tokenization.readtable import RT

from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer
import anoky.syntax.tokens as Tokens
from anoky.tokenization.tokenizers.util import skip_white_lines


class DelimiterTokenizer(Tokenizer):
    """
    Reads blocks of code surrounded by pairs of delimiters.
    """

    DELIMITER_PAIRS = {
        '(' : ')',
        '[' : ']',
        '{' : '}',
        "`" : "`",
        "\(" : "\)"}

    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter not in self.__class__.DELIMITER_PAIRS:
            raise TokenizingError(opening_delimiter_position, "Unregistered delimiter pair, for opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = self.__class__.DELIMITER_PAIRS[opening_delimiter]


    def run(self):
        stream = self.context.stream
        readtable = self.context.readtable

        opening_delimiter_token = Tokens.BEGIN_MACRO(self.opening_delimiter, self.opening_delimiter_position, self.opening_delimiter_position_after)
        yield opening_delimiter_token

        skip_white_lines(stream, readtable)
        col_of_first_non_whitespace = stream.visual_column
        if stream.next_is_EOF():
            raise TokenizingError(stream.copy_absolute_position(), "No characters found after opening delimiter '%s'." % self.opening_delimiter)
        if col_of_first_non_whitespace < 1:
            raise TokenizingError(stream.copy_absolute_position(), "Indentation too small after opening delimiter '%s'." % self.opening_delimiter)

        stream.push()


        tokenizer = self.context.DefaultTokenizer(self.context)
        for token in tokenizer.run():
            yield token

        stream.pop()

        cdem = self.closing_delimiter
        cdem_position = stream.copy_absolute_position()

        skip_white_lines(stream, readtable)

        if stream.next_is_EOF():
            raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.copy_absolute_position()), "Expected closing delimiter «%s», matching opening delimiter «%s» at position %s." % (cdem, self.opening_delimiter, self.opening_delimiter_position.nameless_str))
        else:
            seq, properties = readtable.probe(stream)
            if properties.type == RT.CLOSING:
                if seq != self.closing_delimiter:
                    raise TokenizingError(stream.copy_absolute_position(),
                                          "Expected '%s' closing sequence was not found, `%s` was found instead." % (
                                              cdem, seq))
                else:
                    closing_delimiter_token = Tokens.END_MACRO(opening_delimiter_token, cdem, cdem_position,
                                                               stream.copy_absolute_position())
                    yield closing_delimiter_token







class SharpDelimiterTokenizer(DelimiterTokenizer):
    """
    Reads blocks of code surrounded by pairs of delimiters. Expects to be called with `#(`, `#{` or `#{`,
    and removes the sharp from the emitted token.
    """

    DELIMITER_PAIRS = {
        '#(' : ')',
        '#[' : ']',
        '#{' : '}',
        "'" : "'"}

    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter not in self.__class__.DELIMITER_PAIRS:
            raise TokenizingError(opening_delimiter_position, "Unregistered delimiter pair, for opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter[1:]
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = self.__class__.DELIMITER_PAIRS[opening_delimiter]

