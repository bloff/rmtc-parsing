from Common.Errors import TokenizingError
from Streams import IndentedCharacterStream, CharacterStream
from Tokenization.Readtable import RT_NEWLINE, RT_CONSTITUENT, Readtable
from Tokenization.Readtable import RT_WHITESPACE
from Tokenization.Tokenizers.TokenizerRegistry import get_tokenizer_class


def tokenize_macro(stream:IndentedCharacterStream, readtable:Readtable, seq, properties):
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
    tokenizer = get_tokenizer_class(properties.tokenizer)(stream, seq, abs_macro_seq_position, abs_macro_seq_position_after, readtable)
    for token in tokenizer.run():
        yield token
    stream.pop()


# Skips all white lines until it finds the first non-whitspace, non-newline sequence
# The stream will be positioned on the first character of said sequence
def skip_white_lines(stream:CharacterStream, readtable:Readtable):
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)
        seq_type = properties.type
        if seq_type == RT_NEWLINE:
            continue
        if seq_type != RT_WHITESPACE:
            stream.unread_seq(seq)
            return

def read_and_concatenate_constituent_sequences(stream:CharacterStream, readtable:Readtable):
    concatenation = ""
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)

        if properties.type != RT_CONSTITUENT:
            stream.unread_seq(seq)
            return concatenation
        else:
            concatenation += seq
    return concatenation
