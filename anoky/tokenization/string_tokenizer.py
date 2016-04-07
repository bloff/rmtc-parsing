from anoky.common.errors import TokenizingError
from anoky.streams.stream_position import StreamPosition
from anoky.streams.stream_range import StreamRange
from anoky.tokenization.readtable import RT
from anoky.tokenization.tokenizers import util
from anoky.tokenization import tokenization_context
from anoky.tokenization.tokenizer import Tokenizer
import anoky.syntax.tokens as Tokens
from anoky.tokenization.tokenizers.util import skip_white_lines


class StringTokenizer(Tokenizer):
    """
    Reads "strings" with interpolated code.

    See `<https://bloff.github.io/lyc/2015/10/04/lexer-3.html>`_.
    """
    MY_OPENING_DELIMITER = '"'
    MY_CLOSING_DELIMITER = '"'
    MY_CLOSING_DELIMITER_LENGTH = 1

    def __init__(self, context: tokenization_context, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != self.__class__.MY_OPENING_DELIMITER:
            raise TokenizingError(opening_delimiter_position, "String tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after



    def run(self):
        stream = self.context.stream
        readtable = self.context.readtable

        self.push_stream()

        seen_escape = False

        opening_string_token = Tokens.BEGIN_MACRO(self.__class__.MY_OPENING_DELIMITER,
                                                 self.opening_delimiter_position,
                                                 self.opening_delimiter_position_after)
        yield opening_string_token

        value = ""
        value_first_position = stream.copy_absolute_position()
        while True:
            if stream.next_is_EOF():
                stream.pop()
                skip_white_lines(stream, readtable)
                k_chars = stream.readn(self.__class__.MY_CLOSING_DELIMITER_LENGTH)
                if k_chars != self.__class__.MY_CLOSING_DELIMITER:
                    raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.copy_absolute_position()),
                                      "Expected closing string-delimiter «%s», matching opening delimiter «%s» at position %s." %
                                      (self.__class__.MY_CLOSING_DELIMITER, self.__class__.MY_OPENING_DELIMITER, self.opening_delimiter_position.nameless_str))
                else:
                    value += '\n'
                    yield Tokens.STRING(value, value_first_position, stream.absolute_position_of_unread())
                    yield Tokens.END_MACRO(opening_string_token, self.__class__.MY_CLOSING_DELIMITER, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                    return

            char = stream.read()
            if char == '\\':
                if seen_escape: value += '\\'
                else: seen_escape = True
            else:
                if seen_escape:
                    if char == 'n': value += '\n'
                    elif char == 't': value += '\t'
                    elif char in ('␤', '␉', '$'): value += char
                    elif char == self.__class__.MY_CLOSING_DELIMITER: value += self.__class__.MY_CLOSING_DELIMITER
                    else:
                        raise TokenizingError(stream.absolute_position_of_unread(), "Unknown escape code sequence “%s”." % char)
                    seen_escape = False
                else:
                    if char == '$':
                        yield Tokens.STRING(value, value_first_position, stream.absolute_position_of_unread())
                        for token in self.escape():
                            yield token
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                    else:
                        value += char
                        last_k_chars = value[-self.__class__.MY_CLOSING_DELIMITER_LENGTH:]
                        if last_k_chars == self.__class__.MY_CLOSING_DELIMITER:
                            value = value[:-self.__class__.MY_CLOSING_DELIMITER_LENGTH]
                            yield Tokens.STRING(value, value_first_position, stream.absolute_position_of_unread())
                            yield Tokens.END_MACRO(opening_string_token, self.__class__.MY_CLOSING_DELIMITER, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                            stream.pop()
                            return

        stream.pop()

    def escape(self):
        stream = self.context.stream
        readtable = self.context.readtable

        if stream.next_is_EOF():
            raise TokenizingError(StreamRange(self.opening_delimiter_position, stream.copy_absolute_position()),
                                  "Expected closing string-delimiter «%s», matching opening delimiter «%s» at position %s." % (self.__class__.MY_CLOSING_DELIMITER, self.__class__.MY_OPENING_DELIMITER, self.opening_delimiter_position.nameless_str))
        else:
            seq, properties = readtable.probe(stream)

            assert 'type' in properties
            seq_type = properties.type

            if seq_type == RT.ISOLATED_CONSTITUENT:
                yield Tokens.CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
            elif seq_type == RT.MACRO:
                assert 'tokenizer' in properties

                abs_macro_seq_position = stream.absolute_position_of_unread_seq(seq)
                abs_macro_seq_position_after = stream.copy_absolute_position()

                TokenizerClass = self.context[properties.tokenizer]
                assert issubclass(TokenizerClass, Tokenizer)
                tokenizer = TokenizerClass(self.context, seq, abs_macro_seq_position, abs_macro_seq_position_after)
                for token in tokenizer.run():
                    yield token
            elif seq_type == RT.CONSTITUENT:
                first_position = stream.absolute_position_of_unread_seq(seq)
                concatenation = seq + util.read_and_concatenate_constituent_sequences(stream, readtable)
                yield Tokens.CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())

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

    def push_stream(self):
        self.context.stream.push()

class BlockStringTokenizer(StringTokenizer):

    def push_stream(self):
        stream = self.context.stream
        readtable = self.context.readtable
        skip_white_lines(stream, readtable)
        col_of_first_non_whitespace = stream.visual_column
        if stream.next_is_EOF():
            raise TokenizingError(stream.copy_absolute_position(), "No characters found after opening delimiter '%s'." % self.opening_delimiter)
        if col_of_first_non_whitespace < 1:
            raise TokenizingError(stream.copy_absolute_position(), "Indentation too small after opening delimiter '%s'." % self.opening_delimiter)

        stream.push()

