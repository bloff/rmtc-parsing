from Common.Errors import TokenizingError
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Streams.StreamRange import StreamRange
from .Tokenizer import Tokenizer, TokenizationContext
from Syntax.Token import token_BEGIN_MACRO, token_END_MACRO
from .TokenizerRegistry import def_tokenizer_class, get_tokenizer_class


_delimiter_pairs = {
    '(' : ')',
    '⦅' : '⦆',
    '[' : ']',
    '⟦' : '⟧',
    '{' : '}',
    '⦃' : '⦄',
    '‘' : '’',
    '⟨' : '⟩',
    }

class DelimiterTokenizer(Tokenizer):
    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter not in _delimiter_pairs:
            raise TokenizingError(opening_delimiter_position, "Unregistered delimiter pair, for opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = _delimiter_pairs[opening_delimiter]


    def run(self):
        stream = self.context.stream
        opening_delimiter_token = token_BEGIN_MACRO(self.opening_delimiter, self.opening_delimiter_position, self.opening_delimiter_position_after)
        yield opening_delimiter_token

        tokenizer = self.context.DefaultTokenizer(self.context)
        for token in tokenizer.run():
            yield token

        cdem = self.closing_delimiter
        cdem_position = stream.copy_absolute_position()

        if stream.next_is_EOF():
            raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.copy_absolute_position()), "Expected closing delimiter «%s», matching opening delimiter «%s» at position %s." % (cdem, self.opening_delimiter, self.opening_delimiter_position.nameless_str))

        # Make sure that the previous stream ended when it read a closing delimiter matching our opening delimiter
        for i in range(len(cdem)):
            if stream.read() != cdem[i]:
                raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.absolute_position_of_unread()), "Expected closing delimiter «%s», matching opening delimiter «%s» at position (%s)." % (cdem, self.opening_delimiter, self.opening_delimiter_position.nameless_str))

        closing_delimiter_token = token_END_MACRO(opening_delimiter_token, cdem, cdem_position, stream.copy_absolute_position())
        yield closing_delimiter_token

def_tokenizer_class('Delimiter', DelimiterTokenizer)