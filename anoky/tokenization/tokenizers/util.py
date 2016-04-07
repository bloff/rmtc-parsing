from anoky.common.errors import TokenizingError
from anoky.Streams.CharacterStream import CharacterStream
from anoky.tokenization.readtable import RT
from anoky.tokenization import tokenization_context, readtable
from anoky.tokenization.tokenizer import Tokenizer



# Skips all white lines until it finds the first non-whitspace, non-newline sequence
# The stream will be positioned on the first character of said sequence
def skip_white_lines(stream:CharacterStream, readtable:readtable):
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)
        seq_type = properties.type
        if seq_type == RT.NEWLINE:
            continue
        if seq_type != RT.WHITESPACE:
            stream.unread_seq(seq)
            return

def read_and_concatenate_constituent_sequences(stream:CharacterStream, readtable:readtable):
    concatenation = ""
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)

        if properties.type != RT.CONSTITUENT:
            stream.unread_seq(seq)
            return concatenation
        else:
            concatenation += seq
    return concatenation


def print_tokens(node_with_tokens):
    for token in node_with_tokens:
        print(str(token))