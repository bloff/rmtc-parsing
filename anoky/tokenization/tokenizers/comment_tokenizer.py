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
    CLOSING_DELIMITER = '◁'

    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != self.__class__.OPENING_DELIMITER:
            raise TokenizingError(opening_delimiter_position, "Comment tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after

        assert len(self.__class__.CLOSING_DELIMITER) == 1 # TODO: handle larger closing delimiters?


    def run(self):
        stream = self.context.stream

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
                        raise TokenizingError(stream.absolute_position_of_unread(), "Unknown escape code sequence “%s”." % char)
                    seen_escape = False
                else:
                    if char == self.__class__.CLOSING_DELIMITER:
                        yield Tokens.COMMENT(value, value_first_position, stream.absolute_position_of_unread())
                        yield Tokens.END_MACRO(opening_comment_token, self.__class__.CLOSING_DELIMITER, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                        stream.pop()
                        return
                    elif char == '$':
                        yield Tokens.COMMENT(value, value_first_position, stream.absolute_position_of_unread())
                        for token in self.escape():
                            yield token
                        value = ""
                        value_first_position = stream.copy_absolute_position()
                    else: value += char

    def escape(self):
        stream = self.context.stream
        readtable = self.context.readtable

        if stream.next_is_EOF():
            return
        else:
            seq, properties = readtable.probe(stream)

            assert 'type' in properties
            seq_type = properties.type

            if seq_type == RT.ISOLATED_CONSTITUENT:
                yield Tokens.CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
            elif seq_type == RT.MACRO:
                assert 'tokenizer' in properties
                for token in util.tokenize_macro(self.context, seq, properties):
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
                error_message = properties.error_message if 'error_message' in properties else "Unexpected sequence after comment interpolation character '$'."
                raise TokenizingError(first_position, error_message)

