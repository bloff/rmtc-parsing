from sys import maxsize as MAX_INT

from Common.Errors import TokenizingError
from Streams.IndentedCharacterStream import IndentedCharacterStream
from Tokenization.Readtable import *
from Tokenization.Tokenizers import Util
from Tokenization.Tokenizers.Tokenizer import TokenizationContext
from .Tokenizer import Tokenizer
from Tokenization.StandardReadtable import RT_CLOSING
from Syntax.Token import token_BEGIN, token_END, token_INDENT, token_CONSTITUENT, token_PUNCTUATION


class IndentationReadtableTokenizer(Tokenizer):
    def __init__(self, context:TokenizationContext):
        assert isinstance(context.stream, IndentedCharacterStream)
        Tokenizer.__init__(self, context)

        self.last_begin_token = None


    def run(self):
        readtable = self.context.readtable
        stream = self.context.stream
        """:type : IndentedCharacterStream"""

        while True:
            # Stage 1
            # Step 1

            # Find first non-whitespace, non-newline sequence
            # make sure that it begins at the first column
            Util.skip_white_lines(stream, readtable)

            # If we find an EOF, we're done tokenizing the stream
            if stream.next_is_EOF(): return


            # emit a BEGIN token, and remember it
            self.last_begin_token = token_BEGIN(stream.copy_absolute_position())
            yield self.last_begin_token


            # Step 2
            while True:

                # If we find EOF, we're done; must emmit an END token.
                if stream.next_is_EOF():
                    yield token_END(self.last_begin_token, stream.copy_absolute_position())
                    return
                else:
                    seq, properties = readtable.probe(stream)

                    assert 'type' in properties
                    seq_type = properties.type

                    # Step 3
                    if seq_type == RT_WHITESPACE:
                        pass
                    # Step 4
                    elif seq_type == RT_NEWLINE:
                        break # goto Stage 2
                    # Step 5
                    elif seq_type == RT_TOKEN:
                        yield token_CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
                    # Step 6
                    elif seq_type == RT_PUNCTUATION:
                        yield token_PUNCTUATION(self.last_begin_token, seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
                    # Step 7
                    elif seq_type == RT_MACRO:
                        assert 'tokenizer' in properties
                        for token in Util.tokenize_macro(self.context, seq, properties):
                            yield token
                    # Step 8
                    elif seq_type == RT_CONSTITUENT:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        concatenation =  seq + Util.read_and_concatenate_constituent_sequences(stream, readtable)
                        yield token_CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())
                    # Step 9
                    elif seq_type == RT_CLOSING:
                        stream.unread_seq(seq)
                        yield token_END(self.last_begin_token, stream.copy_absolute_position())
                        return
                    # Step 10
                    elif seq_type == RT_INVALID:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        error_message = properties.error_message if 'error_message' in properties else "Unspecified error."
                        raise TokenizingError(first_position, error_message)

            # Stage 2
            W = MAX_INT
            while True:
                Util.skip_white_lines(stream, readtable)
                relative_column_number = stream.visual_column
                if stream.next_is_EOF():
                    yield token_END(self.last_begin_token, stream.copy_absolute_position())
                    return
                if relative_column_number > W:
                    seq, properties = readtable.probe(stream)

                    if properties.type == RT_CLOSING:
                        yield token_END(self.last_begin_token, stream.absolute_position_of_unread_seq(seq))
                        stream.unread_seq(seq)
                        return
                    else:
                        raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Unexpected indentation when parsing sub-blocks.")
                elif relative_column_number == 1:
                    yield token_END(self.last_begin_token, stream.copy_absolute_position())
                    break # goto Stage 1 again
                elif relative_column_number < W:
                    yield token_INDENT(self.last_begin_token, stream.copy_absolute_position())
                    W = relative_column_number
                elif relative_column_number == W: # finish if the first non-whitespace character is a closing seq
                    seq, properties = readtable.probe(stream)

                    if properties.type == RT_CLOSING:
                        yield token_END(self.last_begin_token, stream.absolute_position_of_unread_seq(seq))
                        stream.unread_seq(seq)
                        return
                    else:
                        stream.unread_seq(seq)


                self.context.stream.push()
                tokenizer = self.context.DefaultTokenizer(self.context)
                for token in tokenizer.run():
                    yield token
                self.context.stream.pop()





