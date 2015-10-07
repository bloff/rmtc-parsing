from Streams.CharacterStream import CharacterStream
from Streams.StringStream import StringStream
from Syntax.Node import Node
from Transducers.DefaultTransducerChain import apply_transducer_chain, default_transducer_chain
from Tokenization.DefaultTokenizer import tokenize


def arrange(code_or_stream) -> Node:
    code_node = tokenize(code_or_stream)
    apply_transducer_chain(default_transducer_chain, code_node)
    return code_node

