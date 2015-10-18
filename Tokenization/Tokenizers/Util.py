from Common.Errors import TokenizingError
from Streams import CharacterStream
from Tokenization.Readtable import Readtable, RT
from Tokenization.TokenizationContext import TokenizationContext
from Tokenization.Tokenizer import Tokenizer


def tokenize_macro(context:TokenizationContext, seq, properties):
    stream = context.stream
    readtable = context.readtable
    abs_macro_seq_position = stream.absolute_position_of_unread_seq(seq)
    abs_macro_seq_position_after = stream.copy_absolute_position()

    macro_seq_position_after = stream.copy_position()
    if 'preserve-leading-whitespace' not in properties:
        col_after_macro_seq = macro_seq_position_after.visual_column
        skip_white_lines(stream, readtable)
        col_of_first_non_whitespace = stream.visual_column
        if stream.next_is_EOF():
            raise TokenizingError(stream.copy_absolute_position(), "No characters found after opening macro sequence '%s'." % seq)
        if col_of_first_non_whitespace < col_after_macro_seq:
            raise TokenizingError(stream.copy_absolute_position(), "Indentation too small after opening macro sequence '%s'." % seq)

    stream.push()
    TokenizerClass = context[properties.tokenizer]
    assert issubclass(TokenizerClass, Tokenizer)
    tokenizer = TokenizerClass(context, seq, abs_macro_seq_position, abs_macro_seq_position_after)
    for token in tokenizer.run():
        yield token
    stream.pop()


# Skips all white lines until it finds the first non-whitspace, non-newline sequence
# The stream will be positioned on the first character of said sequence
def skip_white_lines(stream:CharacterStream, readtable:Readtable):
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)
        seq_type = properties.type
        if seq_type == RT.NEWLINE:
            continue
        if seq_type != RT.WHITESPACE:
            stream.unread_seq(seq)
            return

def read_and_concatenate_constituent_sequences(stream:CharacterStream, readtable:Readtable):
    concatenation = ""
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)

        if properties.type != RT.CONSTITUENT:
            stream.unread_seq(seq)
            return concatenation
        else:
            concatenation += seq
    return concatenation
