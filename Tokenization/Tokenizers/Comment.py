from Common.Errors import TokenizingError
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Streams.StreamRange import StreamRange
from Tokenization.Readtable import RT_TOKEN, RT_MACRO, RT_CONSTITUENT, RT_WHITESPACE, RT_PUNCTUATION, RT_NEWLINE, \
    RT_CLOSING, RT_INVALID
from Tokenization.Tokenizers import Util
from .Tokenizer import Tokenizer, TokenizationContext
from Syntax.Token import token_BEGIN_MACRO, token_END_MACRO, token_COMMENT, token_CONSTITUENT
from .TokenizerRegistry import def_tokenizer_class


class CommentTokenizer(Tokenizer):
    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter != '#':
            raise TokenizingError(opening_delimiter_position, "Comment tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = '◁'

        assert len(opening_delimiter) == 1 and len(self.closing_delimiter) == 1 # TODO: handle larger string delimiters?


    def run(self):
        stream = self.context.stream
        seen_escape = False

        opening_comment_token = token_BEGIN_MACRO(self.opening_delimiter, self.opening_delimiter_position, self.opening_delimiter_position_after)
        yield opening_comment_token

        value = ""
        value_first_position = stream.copy_absolute_position()
        while True:
            if stream.next_is_EOF():
                yield token_COMMENT(value, value_first_position, stream.copy_absolute_position())
                yield token_END_MACRO(opening_comment_token, "", stream.copy_absolute_position(), stream.copy_absolute_position())
                return
            char = stream.read()
            if char == '\\':
                if seen_escape: value += '\\'
                else: seen_escape = True
            else:
                if seen_escape:
                    if char == self.closing_delimiter: value += self.closing_delimiter
                    elif char == '$': value += '$'
                    else:
                        raise TokenizingError(stream.absolute_position_of_unread(), "Unknown escape code sequence “%s”." % char)
                    seen_escape = False
                else:
                    if char == self.closing_delimiter:
                        yield token_COMMENT(value, value_first_position, stream.absolute_position_of_unread())
                        yield token_END_MACRO(opening_comment_token, self.closing_delimiter, stream.absolute_position_of_unread(), stream.copy_absolute_position())
                        return
                    elif char == '$':
                        yield token_COMMENT(value, value_first_position, stream.absolute_position_of_unread())
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

            if seq_type == RT_TOKEN:
                yield token_CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
            elif seq_type == RT_MACRO:
                assert 'tokenizer' in properties
                for token in Util.tokenize_macro(self.context, seq, properties):
                    yield token
            elif seq_type == RT_CONSTITUENT:
                first_position = stream.absolute_position_of_unread_seq(seq)
                concatenation =  seq + Util.read_and_concatenate_constituent_sequences(stream, readtable)
                yield token_CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())

            # Step 3
            elif (seq_type == RT_WHITESPACE or
                  seq_type == RT_PUNCTUATION or
                  seq_type == RT_NEWLINE or
                  seq_type == RT_CLOSING or
                  seq_type == RT_INVALID
                  ):
                first_position = stream.absolute_position_of_unread_seq(seq)
                error_message = properties.error_message if 'error_message' in properties else "Unexpected sequence after comment interpolation character '$'."
                raise TokenizingError(first_position, error_message)

def_tokenizer_class('Comment', CommentTokenizer)