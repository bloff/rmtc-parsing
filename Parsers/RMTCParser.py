from typing import Union

from Common.Errors import TokenizingError
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Streams.StringStream import StringStream
from Syntax.Node import Node
from Tokenization.Readtable import RT
from Transducers.TreeTransducer import apply_transducer_chain


class RMTCParser(object):

    def __init__(self, tokenization_context, default_readtable, DefaultTokenizer, transducer_chain):
        self.tokenization_context = tokenization_context
        self.tokenization_context.set(
            default_readtable = default_readtable,
            readtable = default_readtable,
            # Tokenizer classes
            DefaultTokenizer = DefaultTokenizer,
        )
        self.transducer_chain = transducer_chain


    # returns a stream appropriate for parsing
    def _get_stream(self, code_or_stream:Union[str, CharacterStream]):
        if isinstance(code_or_stream, str):
            stream = StringStream(code_or_stream)
        else:
            assert isinstance(code_or_stream, CharacterStream)
            stream = code_or_stream

        return stream

    def tokenize(self, code_or_stream:Union[str, CharacterStream]):

        # Set the stream of the tokenization context
        stream = self._get_stream(code_or_stream)
        self.tokenization_context.set(stream=stream)

        # Make instance of default tokenizer
        tokenizer = self.tokenization_context.DefaultTokenizer(self.tokenization_context)

        # yield every token emitted by the default tokenizer
        token = None
        for token in tokenizer.run():
            yield token

        # Raise an exception if we failed to emit any token, or fail to parse the entire file

        if token is None:
            raise TokenizingError(StreamPosition(stream.name), "Failed to produce any token.")

        if not self.tokenization_context.stream.next_is_EOF():
            seq, properties = self.tokenization_context.readtable.probe(stream)
            if properties.type == RT.CLOSING:
                raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Uncaptured closing sequence “%s”." % seq)
            raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Failed to Tokenize all of the text!")





    def tokenize_into_node(self, stream:CharacterStream) -> Node:
        node = Node()
        for token in self.tokenize(stream):
            node.append(token)
        return node

    def tokenize_with_intervals(self, code_or_stream:Union[str, CharacterStream], filler=None):
        for token in self.tokenize(code_or_stream):
            current_index = 0
            token_first = token.range.first_position.index
            token_after = token.range.position_after.index

            if token_first > current_index:
                yield (filler, current_index, token_first)
                current_index = token_first
            elif token_first < current_index:
                raise TokenizingError(token_first, "Overlapping tokens (%s, %s)!!!" % (current_index, token_first))

            yield (token, current_index, token_after)

    def arrange(self, code_or_stream:Union[str, CharacterStream]) -> Node:
        code_node = self.tokenize_into_node(code_or_stream)
        apply_transducer_chain(self.transducer_chain, code_node)
        return code_node
