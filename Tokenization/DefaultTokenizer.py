from Common.Errors import TokenizingError
from Streams.CharacterStream import CharacterStream
from Streams.StreamPosition import StreamPosition
from Streams.StringStream import StringStream
from Syntax.Node import Node
from Tokenization.StandardReadtable import standard_readtable, RT_CLOSING
from Tokenization.Tokenizers import StandardTokenizer


def tokenize(code_or_stream) -> Node:
    stream = code_or_stream if isinstance(code_or_stream, CharacterStream) else StringStream(code_or_stream)
    tokenizer = StandardTokenizer(stream)
    code_node = Node()
    last_token = None
    for token in tokenizer.run():
        if last_token is None:
            code_node.first = token
        else:
            last_token.next = token
        token.prev = last_token
        token.parent = code_node
        last_token = token
    if last_token is None:
        raise TokenizingError(StreamPosition("<code>"), "Failed to produce any token.")
    else:
        code_node.last = last_token
        last_token.next = None

    if not stream.next_is_EOF():
        seq, properties = standard_readtable.probe(stream)
        if properties.type == RT_CLOSING:
            raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Uncaptured closing sequence “%s”." % seq)
        raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Failed to Tokenize all of the text!")

    return code_node