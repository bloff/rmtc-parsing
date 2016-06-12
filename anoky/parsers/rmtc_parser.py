from typing import Union

import anoky.syntax.tokens as Tokens
from anoky.common.errors import TokenizingError
from anoky.common.record import Record
from anoky.streams.character_stream import CharacterStream
from anoky.streams.stream_position import StreamPosition
from anoky.streams.string_stream import StringStream
from anoky.syntax.node import Node
from anoky.tokenization.readtable import RT
from anoky.transducers.tree_transducer import apply_transducer_chain

class RMTCParser(object):

    def __init__(self, tokenization_context, default_readtable, DefaultTokenizer, transducer_chain):
        self.tokenization_context = tokenization_context
        self.tokenization_context.set(
            default_readtable = default_readtable,
            readtable = default_readtable,
            # Tokenizer classes
            DefaultTokenizer = DefaultTokenizer,
            expected_closing_seqs=0,
        )
        self.transducer_chain = transducer_chain

    @property
    def readtable(self):
        return self.tokenization_context.readtable

    def add_reader_macro(self, macro_seq, tokenizer_class):
        tokenizer_name = tokenizer_class.__name__
        self.tokenization_context.set(**{tokenizer_name: tokenizer_class})

        self.readtable.add_or_upd_seq(macro_seq, Record(type=RT.MACRO, tokenizer=tokenizer_name))

    def set_readtable_entry(self, seq, **properties):
        self.readtable.add_or_upd_seq("=~", Record(**properties))

    # returns a stream appropriate for parsing
    def _get_stream(self, code_or_stream:Union[str, CharacterStream]):
        if isinstance(code_or_stream, str):
            stream = StringStream(code_or_stream)
        else:
            assert isinstance(code_or_stream, CharacterStream)
            stream = code_or_stream

        return stream

    def tokenize(self, code_or_stream:Union[str, CharacterStream], **context_kwargs):

        # Set the stream of the tokenization context
        stream = self._get_stream(code_or_stream)
        if "emmit_restart_tokens" not in context_kwargs: context_kwargs["emmit_restart_tokens"] = False
        self.tokenization_context.set(stream=stream, **context_kwargs)

        # Make instance of default tokenizer
        tokenizer = self.tokenization_context.DefaultTokenizer(self.tokenization_context)

        self.tokenization_context.set(error = True)
        # yield every token emitted by the default tokenizer
        token = None
        for token in tokenizer.run():
            if isinstance(token, Tokens.ERROR): self.tokenization_context.set(error = True)
            yield token

        # Raise an exception if we failed to emit any token, or fail to parse the entire file

        if token is None:
            raise TokenizingError(StreamPosition(stream.name), "Failed to produce any token.")

        if not self.tokenization_context.stream.next_is_EOF():
            seq, properties = self.tokenization_context.readtable.probe(stream)
            if properties.type == RT.CLOSING:
                raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Uncaptured closing sequence “%s”." % seq)
            raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Failed to Tokenize all of the text!")





    def tokenize_into_node(self, code_or_stream:Union[str, CharacterStream], **context_kwargs) -> Node:
        node = Node()
        for token in self.tokenize(code_or_stream, **context_kwargs):
            node.append(token)
        return node

    # def each_segment(self, stream: CharacterStream) -> Node:
    #     while not stream.next_is_EOF():
    #         node = Node()
    #         first_begin = None
    #         for token in self.tokenize(stream):
    #             if first_begin is None:
    #                 first_begin = token
    #                 if not is_token(token, Tokens.BEGIN):
    #                     raise TokenizingError(first_begin.range,
    #                                           "Expected a `BEGIN` token, found `%s`." % token.__class__.__name__)
    #             node.append(token)
    #             if is_token(token, Tokens.END) and token.begin is first_begin:
    #                 break
    #
    #         yield node

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

    def parse(self, code_or_stream:Union[str, CharacterStream]) -> Node:
        code_node = self.tokenize_into_node(code_or_stream)
        return self.transduce(code_node)



    def transduce(self, code_node:Node):
        apply_transducer_chain(self.transducer_chain, code_node)
        return code_node

    def get_transducer(self, name):
        for transducer in self.transducer_chain:
            if hasattr(transducer, "name") and transducer.name == name:
                return transducer
        return None

    def insert_transducer(self, after_transducer_with_name, transducer):
        i = 0
        while i < len(self.transducer_chain):
            if hasattr(self.transducer_chain[i], "name") and self.transducer_chain[i].name == after_transducer_with_name:
                self.transducer_chain.insert(i+1, transducer)
                return
            i += 1
        raise IndexError("No transducer with name '%s'" % after_transducer_with_name)

    def insert_transducer_before(self, after_transducer_with_name, transducer):
        i = 0
        while i < len(self.transducer_chain):
            if hasattr(self.transducer_chain[i], "name") and self.transducer_chain[
                i].name == after_transducer_with_name:
                self.transducer_chain.insert(i, transducer)
                return
            i += 1
        raise IndexError("No transducer with name '%s'" % after_transducer_with_name)