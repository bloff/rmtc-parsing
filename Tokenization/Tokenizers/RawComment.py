from Common.Errors import TokenizingError
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Tokenization.Tokenizers.Tokenizer import TokenizationContext
from .Tokenizer import Tokenizer
from Syntax.Token import token_BEGIN_MACRO, token_END_MACRO, token_COMMENT
from .TokenizerRegistry import def_tokenizer_class


class RawCommentTokenizer(Tokenizer):
    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition, readtable):
        Tokenizer.__init__(self, context)

        if opening_delimiter != '##':
            raise TokenizingError(opening_delimiter_position, "Raw-comment tokenizer called with unknown opening sequence “%s”" % opening_delimiter)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after


    def run(self):
        stream = self.context.stream

        opening_comment_token = token_BEGIN_MACRO(self.opening_delimiter, self.opening_delimiter_position, self.opening_delimiter_position_after)
        yield opening_comment_token

        value = ""
        value_first_position = stream.copy_absolute_position()
        while True:
            if stream.next_is_EOF():
                yield token_COMMENT(value, value_first_position, stream.copy_absolute_position())
                yield token_END_MACRO(opening_comment_token, "", stream.copy_absolute_position(), stream.copy_absolute_position())
                return
            stream.read()

def_tokenizer_class('Raw Comment', RawCommentTokenizer)