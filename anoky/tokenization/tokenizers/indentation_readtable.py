from sys import maxsize as MAX_INT

from anoky.common.errors import TokenizingError
from anoky.streams.indented_character_stream import IndentedCharacterStream
from anoky.tokenization.readtable import RT
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer
import anoky.syntax.tokens as Tokens
from anoky.tokenization.tokenizers import util


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
        expected_closing_seqs = self.context.expected_closing_seqs

        emmit_restart_tokens = self.context.emmit_restart_tokens
        restart_token_count = 0


        # Numbers #.#.# refer to the list in the blog post
        # https://bloff.github.io/lyc/lexing,/syntax/2015/08/30/lexer-2.html
        while True:
            # Stage 1 (Preparation)

            # Find first non-whitespace, non-newline sequence
            # make sure that it begins at the first column
            util.skip_white_lines(stream, readtable)

            # If we find an EOF, we're done tokenizing the stream
            if stream.next_is_EOF():
                # emmit_hanging_restart_tokens()
                for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(stream.copy_absolute_position())
                return

            #                [  Handling closing sequences  ]
            #
            #  If we find an (expected) closing sequence, we're also done
            # if the sequence was not expected, an error token is emmited
            seq, properties = readtable.probe(stream)
            if properties.type == RT.CLOSING:
                if expected_closing_seqs > 0:
                    stream.unread_seq(seq)
                    # emmit_hanging_restart_tokens()
                    for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(stream.copy_absolute_position())
                    return
                else:
                    yield Tokens.ERROR(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position(),
                                       "Unexpected closing sequence `%s`." % seq)
            # Any other sequence is unread
            stream.unread_seq(seq)


            #                           [  Signaling restart positions  ]
            #
            # If we are asked to emmit restart-position tokens, which serve to pinpoint locations where the
            # default tokenizer can safely restart, then  we do so, and we keep track of how many such tokens
            # must be terminated
            if emmit_restart_tokens and stream.current_relative_position.column == 1 and expected_closing_seqs <= 0:
                restart_token_count += 1
                yield Tokens.VALID_RESTART_FROM(stream.copy_absolute_position())


            #        [ The first BEGIN token ]
            # emit a BEGIN token, and remember it
            self.last_begin_token = Tokens.BEGIN(stream.copy_absolute_position())
            yield self.last_begin_token


            #         [  Stage 2 - Parsing of segment's first line  ]
            while True:
                # 2.1
                if stream.next_is_EOF():
                    yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                    # emmit_hanging_restart_tokens()
                    for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(stream.copy_absolute_position())
                    return
                else:
                    seq, properties = readtable.probe(stream)

                    assert 'type' in properties
                    seq_type = properties.type

                    # 2.1
                    if seq_type == RT.CLOSING:
                        if expected_closing_seqs <= 0:
                            yield Tokens.ERROR(seq, stream.absolute_position_of_unread_seq(seq),
                                               stream.copy_absolute_position(),
                                               "Unexpected closing sequence `%s`." % seq)
                        else:
                            stream.unread_seq(seq)
                            yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                            # emmit_hanging_restart_tokens()
                            for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(
                                stream.copy_absolute_position())
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
                        for token in util.tokenize_macro(self.context, seq, properties):
                            yield token
                    # 2.7
                    elif seq_type == RT.CONSTITUENT:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        concatenation = seq + util.read_and_concatenate_constituent_sequences(stream, readtable)
                        yield Tokens.CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())
                    # 2.8
                    elif seq_type == RT.INVALID:
                        first_position = stream.absolute_position_of_unread_seq(seq)
                        error_message = properties.error_message if 'error_message' in properties else "Invalid character found in stream."
                        yield Tokens.ERROR(seq, first_position, stream.copy_absolute_position(), error_message)

            # Stage 3 (Parsing of sub-blocks)
            W = MAX_INT
            while True:
                util.skip_white_lines(stream, readtable)
                relative_column_number = stream.visual_column
                # 3.2
                if stream.next_is_EOF():
                    yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                    # emmit_hanging_restart_tokens()
                    for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(stream.copy_absolute_position())
                    return
                # 3.2.1
                if relative_column_number == 1:
                    yield Tokens.END(self.last_begin_token, stream.copy_absolute_position())
                    # DON'T # emmit_hanging_restart_tokens()
                    break # goto Stage 1 again
                # 3.2.2
                elif relative_column_number > W:
                    seq, properties = readtable.probe(stream)

                    if properties.type == RT.CLOSING:
                        if expected_closing_seqs <= 0:
                            yield Tokens.ERROR(seq, stream.absolute_position_of_unread_seq(seq),
                                               stream.copy_absolute_position(),
                                               "Unexpected closing sequence `%s`." % seq)
                        else:
                            yield Tokens.END(self.last_begin_token, stream.absolute_position_of_unread_seq(seq))
                            # emmit_hanging_restart_tokens()
                            for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(
                                stream.copy_absolute_position())
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
                        if expected_closing_seqs <= 0:
                            yield Tokens.ERROR(seq, stream.absolute_position_of_unread_seq(seq),
                                               stream.copy_absolute_position(),
                                               "Unexpected closing sequence `%s`." % seq)
                        else:
                            yield Tokens.END(self.last_begin_token, stream.absolute_position_of_unread_seq(seq))
                            # emmit_hanging_restart_tokens()
                            for _ in range(restart_token_count): yield Tokens.VALID_RESTART_TO(
                                stream.copy_absolute_position())
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





