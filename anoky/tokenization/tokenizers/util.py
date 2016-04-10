from anoky.streams.character_stream import CharacterStream
from anoky.tokenization.readtable import RT, Readtable



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

        if properties.type == RT.CONSTITUENT:
            concatenation += seq
        elif properties.type == RT.ISOLATED_CONSTITUENT and hasattr(properties, "dont_isolate_infix"):
            concatenation += seq
        else:
            stream.unread_seq(seq)
            return concatenation

    return concatenation

def read_and_concatenate_constituent_sequences_ignore_isolation(stream:CharacterStream, readtable:Readtable):
    concatenation = ""
    while not stream.next_is_EOF():
        seq, properties = readtable.probe(stream)

        if properties.type == RT.CONSTITUENT or properties.type == RT.ISOLATED_CONSTITUENT:
            concatenation += seq
        else:
            stream.unread_seq(seq)
            return concatenation

    return concatenation


def print_tokens(node_with_tokens):
    for token in node_with_tokens:
        print(str(token))