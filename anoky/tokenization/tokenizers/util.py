from anoky.streams.character_stream import CharacterStream
from anoky.tokenization.readtable import RT, Readtable
import anoky.syntax.tokens as Tokens



# Skips all white lines until it finds the first non-whitspace, non-newline sequence
# The stream will be positioned on the first character of said sequence
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer


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


def tokenize_macro(context:TokenizationContext, seq, properties):
    stream = context.stream
    assert 'tokenizer' in properties
    abs_macro_seq_position = stream.absolute_position_of_unread_seq(seq)
    abs_macro_seq_position_after = stream.copy_absolute_position()

    TokenizerClass = context[properties.tokenizer]
    assert issubclass(TokenizerClass, Tokenizer)
    tokenizer = TokenizerClass(context, seq, abs_macro_seq_position, abs_macro_seq_position_after)
    for token in tokenizer.run():
        yield token


def interpolation(context):
    stream = context.stream
    readtable = context.readtable

    if stream.next_is_EOF():
        return
    else:
        seq, properties = readtable.probe(stream)

        assert 'type' in properties
        seq_type = properties.type

        if seq_type == RT.ISOLATED_CONSTITUENT:
            yield Tokens.CONSTITUENT(seq, stream.absolute_position_of_unread_seq(seq), stream.copy_absolute_position())
        elif seq_type == RT.MACRO:
            for token in tokenize_macro(context, seq, properties):
                yield token
        elif seq_type == RT.CONSTITUENT:
            first_position = stream.absolute_position_of_unread_seq(seq)
            concatenation = seq + read_and_concatenate_constituent_sequences(stream, readtable)
            yield Tokens.CONSTITUENT(concatenation, first_position, stream.copy_absolute_position())

        # Step 3
        else:
            context.error = True
            first_position = stream.absolute_position_of_unread_seq(seq)
            error_message = properties.error_message if 'error_message' in properties else "Unexpected character '%s' in interpolation." % seq
            yield Tokens.ERROR(seq, first_position, stream.copy_absolute_position(), error_message)

