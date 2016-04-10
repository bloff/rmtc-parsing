from sys import maxsize as MAX_INT

from anoky.common.errors import TokenizingError
from anoky.streams.indented_character_stream import IndentedCharacterStream
from anoky.streams.stream_position import StreamPosition
from anoky.tokenization.readtable import RT
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer
import anoky.syntax.tokens as Tokens
from anoky.tokenization.tokenizers import util


class LispModeTokenizer(Tokenizer):
    """
    This implements the classic readtable-macro parsing algorithm (i.e. without indentation),
    adapted to be able to parse forms and seqs.
    """

    DELIMITER_PAIRS = {
        '#(': ')',
        '(': ')',
    }

    def __init__(self,
                 context: TokenizationContext,
                 opening_delimiter: str,
                 opening_delimiter_position: StreamPosition,
                 opening_delimiter_position_after: StreamPosition):
        Tokenizer.__init__(self, context)

        if opening_delimiter not in self.__class__.DELIMITER_PAIRS:
            raise TokenizingError(opening_delimiter_position,
                                  "Lisp mode tokenizer called with unknown opening delimiter sequence `%s`" % opening_delimiter)

        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after
        self.closing_delimiter = self.__class__.DELIMITER_PAIRS[opening_delimiter]

        if opening_delimiter[0] == "#":
            self.opening_delimiter = opening_delimiter
            # toggle '(' tokenizer between LispMode and Delimiter tokenizers
            readtable = context.readtable
            self.set_delimiter_tokenizers(readtable, "LispModeTokenizer", "SharpDelimiterTokenizer")
        else:
            self.opening_delimiter = '#' + opening_delimiter



    def run(self):
        readtable = self.context.readtable
        stream = self.context.stream
        """:type : CharacterStream"""

        while True:
            # Stage 1 (Preparation)

            # emit a BEGIN_MACRO token, and remember it
            opening_delimiter_token = Tokens.BEGIN_MACRO(self.opening_delimiter,
                                                         self.opening_delimiter_position,
                                                         self.opening_delimiter_position_after)
            yield opening_delimiter_token

            node_type = None

            # Stage 2 (Parsing of the form)
            while True:

                # 2.1
                if stream.next_is_EOF():
                    raise TokenizingError(stream.copy_absolute_position(),
                                          "Expected `%s` closing sequence was not found." % self.closing_delimiter)
                else:
                    seq, properties = readtable.probe(stream)

                    assert 'type' in properties
                    seq_type = properties.type

                    # 2.1
                    if seq_type == RT.CLOSING:
                        if seq != self.closing_delimiter:
                            raise TokenizingError(stream.copy_absolute_position(),
                                                  "Expected '%s' closing sequence was not found, `%s` was found instead." % (
                                                  self.closing_delimiter, seq))
                        elif node_type is None:
                            raise TokenizingError(stream.copy_absolute_position(),
                                                  "Empty form/seq.")
                        else:
                            opening_delimiter_token.form_or_seq = node_type
                            # return the delimiter tokenizers to their usual selves
                            self.set_delimiter_tokenizers(readtable, "DelimiterTokenizer", "LispModeTokenizer")
                            yield Tokens.END_MACRO(opening_delimiter_token,
                                                   seq,
                                                   stream.absolute_position_of_unread_seq(seq),
                                                   stream.copy_absolute_position())
                            return
                    # 2.2
                    elif seq_type == RT.WHITESPACE:
                        pass
                    # 2.3
                    elif seq_type == RT.NEWLINE:
                        pass
                    # 2.5
                    elif seq_type == RT.PUNCTUATION:
                        raise TokenizingError(stream.copy_absolute_position(),
                                              "Unexpected punctuation '%s' inside lisp mode." % seq)

                        # yield Tokens.PUNCTUATION(self.last_begin_token, seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
                    # 2.6
                    elif seq_type == RT.MACRO:
                        assert 'tokenizer' in properties
                        abs_macro_seq_position = stream.absolute_position_of_unread_seq(seq)
                        abs_macro_seq_position_after = stream.copy_absolute_position()

                        TokenizerClass = self.context[properties.tokenizer]
                        assert issubclass(TokenizerClass, Tokenizer)
                        tokenizer = TokenizerClass(self.context, seq, abs_macro_seq_position, abs_macro_seq_position_after)
                        for token in tokenizer.run():
                            yield token
                    # 2.7
                    elif seq_type == RT.CONSTITUENT or seq_type == RT.ISOLATED_CONSTITUENT:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        concatenation = seq + util.read_and_concatenate_constituent_sequences_ignore_isolation(stream, readtable)
                        yield Tokens.CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())
                        if node_type is None:
                            if self.read_char(',', readtable, stream, force=False):
                                node_type = "seq"
                            else:
                                node_type = "form"
                        elif node_type is "seq":
                            self.read_char(',', readtable, stream)
                        elif node_type is "form":
                            pass
                        else:
                            raise NotImplementedError()

                    # 2.8
                    elif seq_type == RT.INVALID:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        error_message = properties.error_message if 'error_message' in properties else "Unspecified error."
                        raise TokenizingError(first_position, error_message)

    def read_char(self, char, readtable, stream, force=True):
        util.skip_white_lines(stream, readtable)

        if stream.next_is_EOF():
            raise TokenizingError(stream.copy_absolute_position(),
                                  "Expected `%s` closing sequence was not found." % self.closing_delimiter)
        else:
            seq, properties = readtable.probe(stream)

            if seq != char:
                if force:
                    if properties.type != RT.CLOSING:
                        raise TokenizingError(stream.copy_absolute_position(), "Expected `%s` in lisp-mode seq." % char)
                    else:
                        stream.unread_seq(seq)
                        return False
                else:
                    stream.unread_seq(seq)
                    return False

            return True

    def set_delimiter_tokenizers(self, readtable, normal, sharp):
        readtable.query('(')[0].tokenizer = normal
        readtable.query('#(')[0].tokenizer = sharp





