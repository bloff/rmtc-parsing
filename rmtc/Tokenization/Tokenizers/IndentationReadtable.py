from sys import maxsize as MAX_INT

from rmtc.Common.Errors import TokenizingError
from rmtc.Streams.IndentedCharacterStream import IndentedCharacterStream
from rmtc.Tokenization.Readtable import RT
from rmtc.Tokenization.TokenizationContext import TokenizationContext
from rmtc.Tokenization.Tokenizer import Tokenizer
import rmtc.Syntax.Tokens as Tokens
from rmtc.Tokenization.Tokenizers import Util


class IndentationReadtableTokenizer(Tokenizer):
    """
    This implements the readtable-macro parsing algorithm (with indentation), described in

    `<https://bloff.github.io/lyc/lexing,/syntax/2015/08/30/lexer-2.html>`_
    """
    def __init__(self, context:TokenizationContext):
        assert isinstance(context.stream, IndentedCharacterStream)
        Tokenizer.__init__(self, context)

        self.last_begin_token = None


    def run(self):
        readtable = self.context.readtable
        stream = self.context.stream
        """:type : IndentedCharacterStream"""

        # Numbers #.#.# refer to the list in the blog post
        # https://bloff.github.io/lyc/lexing,/syntax/2015/08/30/lexer-2.html
        while True:
            # Stage 1 (Preparation)

            # Find first non-whitespace, non-newline sequence
            # make sure that it begins at the first column
            Util.skip_white_lines(stream, readtable)

            # If we find an EOF or a closing sequence, we're done tokenizing the stream
            if stream.next_is_EOF(): return
            seq, properties = readtable.probe(stream)
            stream.unread_seq(seq)
            if properties.type == RT.CLOSING: return


            # emit a BEGIN token, and remember it
            self.last_begin_token = Tokens.BEGIN(stream.copy_absolute_position())
            yield self.last_begin_token


            # Stage 2 (Parsing of segment's first line)
            while True:

                # 2.1
                if stream.next_is_EOF():
                    yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                    return
                else:
                    seq, properties = readtable.probe(stream)

                    assert 'type' in properties
                    seq_type = properties.type

                    # 2.1
                    if seq_type == RT.CLOSING:
                        stream.unread_seq(seq)
                        yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                        return
                    # 2.2
                    elif seq_type == RT.WHITESPACE:
                        pass
                    # 2.3
                    elif seq_type == RT.NEWLINE:
                        break # goto Stage 2
                    # 2.4
                    elif seq_type == RT.ISOLATED_CONSTITUENT:
                        yield Tokens.CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
                    # 2.5
                    elif seq_type == RT.PUNCTUATION:
                        yield Tokens.PUNCTUATION(self.last_begin_token, seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
                    # 2.6
                    elif seq_type == RT.MACRO:
                        assert 'tokenizer' in properties
                        for token in Util.tokenize_macro(self.context, seq, properties):
                            yield token
                    # 2.7
                    elif seq_type == RT.CONSTITUENT:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        concatenation =  seq + Util.read_and_concatenate_constituent_sequences(stream, readtable)
                        yield Tokens.CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())
                    # 2.8
                    elif seq_type == RT.INVALID:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        error_message = properties.error_message if 'error_message' in properties else "Unspecified error."
                        raise TokenizingError(first_position, error_message)

            # Stage 3 (Parsing of sub-blocks)
            W = MAX_INT
            while True:
                Util.skip_white_lines(stream, readtable)
                relative_column_number = stream.visual_column
                # 3.2
                if stream.next_is_EOF():
                    yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                    return
                # 3.2.1
                if relative_column_number == 1:
                    yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                    break # goto Stage 1 again
                # 3.2.2
                elif relative_column_number > W:
                    seq, properties = readtable.probe(stream)

                    if properties.type == RT.CLOSING:
                        yield Tokens.END(self.last_begin_token, stream.absolute_position_of_unread_seq(seq))
                        stream.unread_seq(seq)
                        return
                    else:
                        raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Unexpected indentation when parsing sub-blocks.")
                # 3.2.3
                elif relative_column_number < W:
                    yield Tokens.INDENT(self.last_begin_token, stream.copy_absolute_position())
                    W = relative_column_number
                # 3.2.4
                else:
                    # when relative_column_number == W, finish if the first non-whitespace character is a closing seq
                    seq, properties = readtable.probe(stream)

                    if properties.type == RT.CLOSING:
                        yield Tokens.END(self.last_begin_token, stream.absolute_position_of_unread_seq(seq))
                        stream.unread_seq(seq)
                        return
                    else:
                        stream.unread_seq(seq)

                # 3.3
                self.context.stream.push()
                tokenizer = self.context.DefaultTokenizer(self.context)
                for token in tokenizer.run():
                    yield token
                self.context.stream.pop()





