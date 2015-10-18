from Common.Errors import TokenizingError
from Streams.StreamPosition import StreamPosition
from Streams.StreamRange import StreamRange
from Tokenization.Readtable import RT
from Tokenization.Tokenizers import Util
from Tokenization.TokenizationContext import TokenizationContext
from Tokenization.Tokenizer import Tokenizer
from Syntax.Token import token_STRING, token_BEGIN_MACRO, token_END_MACRO, token_CONSTITUENT


class StringTokenizer(Tokenizer):
    """
    Reads strings with interpolated code.

    See `<https://bloff.github.io/lyc/2015/10/04/lexer-3.html>`_.
    """
    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != '“':
            raise TokenizingError(opening_delimiter_position, "String tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = '”'

        assert len(opening_delimiter) == 1 and len(self.closing_delimiter) == 1 # TODO: handle larger string delimiters?


    def run(self):
        stream = self.context.stream
        seen_escape = False

        opening_string_token = token_BEGIN_MACRO(self.opening_delimiter, self.opening_delimiter_position, self.opening_delimiter_position_after)
        yield opening_string_token

        value = ""
        value_first_position = stream.copy_absolute_position()
        while True:
            if stream.next_is_EOF():
                raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.copy_absolute_position()), "Expected closing string-delimiter «%s», matching opening delimiter «%s» at position %s." % (self.closing_delimiter, self.opening_delimiter, self.opening_delimiter_position.nameless_str))
            char = stream.read()
            if char == '\\':
                if seen_escape: value += '\\'
                else: seen_escape = True
            else:
                if seen_escape:
                    if char == 'n': value += '\n'
                    elif char == 't': value += '\t'
                    elif char in ('␤', '␉', '$'): value += char
                    elif char == self.closing_delimiter: value += self.closing_delimiter
                    else:
                        raise TokenizingError(stream.absolute_position_of_unread(), "Unknown escape code sequence “%s”." % char)
                    seen_escape = False
                else:
                    if char == self.closing_delimiter:
                        yield token_STRING(value, value_first_position, stream.absolute_position_of_unread())
                        yield token_END_MACRO(opening_string_token, self.closing_delimiter, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                        return
                    elif char == '$':
                        yield token_STRING(value, value_first_position, stream.absolute_position_of_unread())
                        for token in self.escape():
                            yield token
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                    elif char == '␤': value += '\n'
                    elif char == '␉': value += '\t'
                    else: value += char

    def escape(self):
        stream = self.context.stream
        readtable = self.context.readtable

        if stream.next_is_EOF():
            raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.copy_absolute_position()),
                                  "Expected closing string-delimiter «%s», matching opening delimiter «%s» at position %s." % (self.closing_delimiter, self.opening_delimiter, self.opening_delimiter_position.nameless_str))
        else:
            seq, properties = readtable.probe(stream)

            assert 'type' in properties
            seq_type = properties.type

            if seq_type == RT.ISOLATED_CONSTITUENT:
                yield token_CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
            elif seq_type == RT.MACRO:
                assert 'tokenizer' in properties
                for token in Util.tokenize_macro(self.context, seq, properties):
                    yield token
            elif seq_type == RT.CONSTITUENT:
                first_position = stream.absolute_position_of_unread_seq(seq)
                concatenation =  seq + Util.read_and_concatenate_constituent_sequences(stream, readtable)
                yield token_CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())

            # Step 3
            elif (seq_type == RT.WHITESPACE or
                  seq_type == RT.PUNCTUATION or
                  seq_type == RT.NEWLINE or
                  seq_type == RT.CLOSING or
                  seq_type == RT.INVALID
                  ):
                first_position = stream.absolute_position_of_unread_seq(seq)
                error_message = properties.error_message if 'error_message' in properties else "Unexpected sequence after string interpolation character '$'."
                raise TokenizingError(first_position, error_message)




