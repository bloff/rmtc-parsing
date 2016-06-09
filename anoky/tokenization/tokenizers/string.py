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
    ALLOW_RUNOFF_CLOSING_DELIMITER = False
    MY_OPENING_DELIMITER = '"'
    MY_CLOSING_DELIMITER = '"'
    MY_CLOSING_DELIMITER_LENGTH = 1
    MY_INTERPOL_CHAR = '$'  # assuming interpolation marker is only a single character
    #MY_INTERPOL_CHAR_LENGTH?

    def __init__(self, context: tokenization_context, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != self.__class__.MY_OPENING_DELIMITER:
            raise TokenizingError(opening_delimiter_position, "String tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after



    def run(self):
        stream = self.context.stream
        readtable = self.context.readtable

        if stream.next_is_EOF():
            yield Tokens.ERROR(self.__class__.MY_OPENING_DELIMITER, self.opening_delimiter_position,
                               self.opening_delimiter_position_after,
                               "No characters found after opening delimiter %s." % repr(self.__class__.MY_OPENING_DELIMITER))
            return

        stream.push()

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
                if self.__class__.ALLOW_RUNOFF_CLOSING_DELIMITER:
                    position_before_skipping_white_lines = stream.copy_absolute_position()
                    skip_white_lines(stream, readtable)
                    position_before_attempting_to_read_k_chars = stream.copy_absolute_position()
                    k_chars = stream.readn(self.__class__.MY_CLOSING_DELIMITER_LENGTH)
                    if k_chars != self.__class__.MY_CLOSING_DELIMITER:
                        yield Tokens.ERROR(k_chars, position_before_attempting_to_read_k_chars, stream.copy_absolute_position(),
                                          "Expected closing string-delimiter «%s», matching opening delimiter «%s» at position %s.%s" %
                                          (self.__class__.MY_CLOSING_DELIMITER,
                                           self.__class__.MY_OPENING_DELIMITER,
                                           self.opening_delimiter_position.nameless_str,
                                           "" if k_chars is None else " Found " + repr(k_chars)))
                        return
                    else:
                        value += '\n'
                        yield Tokens.STRING(value, value_first_position, position_before_skipping_white_lines)
                        yield Tokens.END_MACRO(opening_string_token, self.__class__.MY_CLOSING_DELIMITER, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                        return
                else:
                    yield Tokens.ERROR("", stream.copy_absolute_position(), stream.copy_absolute_position(),
                                       "Expected closing string-delimiter «%s», matching opening delimiter «%s» at position %s." %
                                       (self.__class__.MY_CLOSING_DELIMITER,
                                        self.__class__.MY_OPENING_DELIMITER,
                                        self.opening_delimiter_position.nameless_str))
                return

            char = stream.read()
            if char == '\\':
                if seen_escape: value += '\\'
                else: seen_escape = True
            else:
                if seen_escape:
                    if char == 'n': value += '\n'
                    elif char == 't': value += '\t'
                    elif char in ('␤', '␉', self.MY_INTERPOL_CHAR): value += char
                    elif char == self.__class__.MY_CLOSING_DELIMITER: value += self.__class__.MY_CLOSING_DELIMITER
                    else:
                        yield Tokens.STRING(value, value_first_position, stream.absolute_position_of_unread())
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                        yield Tokens.ERROR(char, stream.absolute_position_of_unread(), stream.copy_absolute_position(), "Unknown escape code sequence “%s”." % char)
                    seen_escape = False
                else:
                    if char == self.MY_INTERPOL_CHAR:
                        yield Tokens.STRING(value, value_first_position, stream.absolute_position_of_unread())
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                        for token in util.interpolation(self.context):
                            yield token
                    else:
                        value += char
                        last_k_chars = value[-self.__class__.MY_CLOSING_DELIMITER_LENGTH:]
                        if last_k_chars == self.__class__.MY_CLOSING_DELIMITER:
                            value = value[:-self.__class__.MY_CLOSING_DELIMITER_LENGTH]
                            closing_delimiter_first_position = stream.absolute_position_of_unread(self.__class__.MY_CLOSING_DELIMITER_LENGTH)
                            yield Tokens.STRING(value, value_first_position, closing_delimiter_first_position)
                            yield Tokens.END_MACRO(opening_string_token, self.__class__.MY_CLOSING_DELIMITER,
                                                   closing_delimiter_first_position, stream.copy_absolute_position())
                            stream.pop()
                            return

        stream.pop()


class BlockStringTokenizer(StringTokenizer):

    ALLOW_RUNOFF_CLOSING_DELIMITER = True

    def run(self):
        stream = self.context.stream
        readtable = self.context.readtable
        skip_white_lines(stream, readtable)


        for token in super(BlockStringTokenizer, self).run():
            yield token

