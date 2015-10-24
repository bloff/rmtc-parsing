from Common.Errors import TokenizingError
from Streams.StreamPosition import StreamPosition
from Tokenization.TokenizationContext import TokenizationContext
from Tokenization.Tokenizer import Tokenizer
import Syntax.Tokens as Tokens


# _multiple_escape_delimiter_pairs = {
#     '“' : '”',
#     '‘' : '’',
#     }

class DelimitedIdentifierTokenizer(Tokenizer):
    """
    Reads identifiers surrounded by delimiters. Hence one can write identifiers with special chararacters, e.g., ``«1234 some identifier»``.
    """
    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != "«":
            raise TokenizingError(opening_delimiter_position, "Multiple-escape tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = "»"


    def run(self):
        stream = self.context.stream
        seen_escape = False

        # opening_string_token = Tokens.BEGIN_MACRO(self.opening_delimiter, self.opening_delimiter_position, stream.position)
        # yield opening_string_token

        value = ""
        while True:
            if stream.next_is_EOF():
                raise TokenizingError(stream.position, "Expected closing multiple-escape-delimiter «%s», matching opening delimiter «%s» at position %s." % (self.closing_delimiter, self.opening_delimiter, self.opening_delimiter_position.nameless_str))
            char = stream.read()
            if char == '\\':
                if seen_escape: value += '\\'
                else: seen_escape = True
            else:
                if seen_escape:
                    if char == 'n': value += '\n'
                    elif char == 't': value += '\t'
                    elif char in ('␤', '␉',): value += char
                    elif char == self.closing_delimiter: value += self.closing_delimiter
                    else:
                        raise TokenizingError(stream.absolute_position_of_unread(), "Unknown escape code sequence “%s”." % char)
                else:
                    if char == self.closing_delimiter:
                        yield Tokens.CONSTITUENT(value, self.opening_delimiter_position, stream.copy_absolute_position())
                        # yield Tokens.END_MACRO(opening_string_token, self.closing_delimiter, stream.position_of_unread(), stream.position)
                        return
                    elif char == '␤': value += '\n'
                    elif char == '␉': value += '\t'
                    else: value += char
