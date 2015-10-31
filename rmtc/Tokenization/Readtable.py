from enum import Enum

from rmtc.Common.Record import Record
from rmtc.Streams.CharacterStream import CharacterStream


class RT(Enum):
    """
    Enum of readtable entry types.
    """
    WHITESPACE = 1
    """A whitespace character sequence."""
    NEWLINE = 2
    """A newline character sequence."""
    ISOLATED_CONSTITUENT = 3
    """A constituent character sequence that should *not* be concatenated with other adjacent constituent sequences."""
    CONSTITUENT = 4
    """A constituent character sequence that *should* be concatenated with other adjacent constituent sequences."""
    MACRO = 5
    """A character sequence that begins a reader macro."""
    INVALID = 6
    """A character sequence that should not appear."""
    CLOSING = 7
    """A character sequence that signals the end of a reader macro."""
    PUNCTUATION = 8
    """A punctuation character sequence."""

class Readtable(object):
    """
    A readtable. It associates certain characters or sequences of characters with a dictionary of so-called *properties* (which could be anything).
    For instance, lyc's readtable associates the sequence :literal:`“` with the properties ``{'type': RT.MACRO, 'tokenizer': 'StringTokenizer'}``,
    which should mean that if a :literal:`“` character is found, it signals a reader macro which is to be processed by the tokenizer called
    'StringTokenizer'.

    The table is organized as a prefix tree. Each path in the tree is a sequence in the table. Each node in the tree is
    encoded as a dictionary mapping characters to pairs ``[child_node, properties]``. So, for instance, the default lyc readtable
    has in its root node a mapping from ``'#'`` to ``[subnode, {'type': 'macro', 'tokenizer': 'CommentTokenizer'}]``, where subnode
    has a mapping from ``'#'`` to ``[None, {'type': 'macro', 'tokenizer':'RawCommentTokenizer'}]``. This means that the ``'#'``
    sequence has properties ``{'type': 'macro', 'tokenizer': 'CommentTokenizer'}``, and the '##' sequence has properties
    ``{'type': 'macro', 'tokenizer':'RawCommentTokenizer'}``; it also means that there is no way of extending '##' into a larger
    entry of the readtable.
    """
    def __init__(self):
        self.root_node = {}
        """The root of the prefix tree."""
        self.default_properties = Record({})
        """This is the property list of sequences of characters that are not entries in the readtable."""

    def _return_properties(self, properties):
        return properties if properties is not None else self.default_properties


    def add_or_upd_seq(self, sequence:str, properties:dict):
        """
        Associates a given sequence of characters with the given properties dictionary,
        or updates the associated properties dictionary, if one is already present
        :param sequence: The sequence of characters to be entered/updated in the readtable.
        :param properties: The associated dictionary of properties.
        """
        node = self.root_node
        node_properties_pair = None
        for char in sequence:
            if char not in node:
                node_properties_pair = [{}, None]
                node[char] = node_properties_pair
            else:
                node_properties_pair = node[char]
            node = node_properties_pair[0]
        assert node_properties_pair is not None
        assert node_properties_pair[1] is None
        node_properties_pair[1] = properties


    def query(self, seq:str):
        """
        Queries an entry in the readtable.
        :param seq: The sequence of characters to be queried.
        :return: a pair ``(properties, continuation_possible)``, where ``properties`` is the properties associated with
        the given sequence (which could be the ``default_properties``), and ``continuation_possible`` is ``True`` iff the
        sequence can be extended to some other (longer) sequence in the read-table.
        """
        node = self.root_node
        node_properties_pair = [{}, None]
        for char in seq:
            if char not in node:
                return self.default_properties, False
            else:
                node_properties_pair = node[char]
                node = node_properties_pair[0]
        properties = self._return_properties(node_properties_pair[1])
        continuation_possible = len(node_properties_pair[0]) > 0
        return properties, continuation_possible



    def probe(self, stream:CharacterStream):
        """
        Reads a stream one character at a time, as long as the read sequence of characters is an entry of the readtable.

        :param stream: The stream to be probed.
        :return: A pair with the largest possible such sequence and the associated properties.
        """
        node = self.root_node
        node_properties_pair = [{}, None]
        seq = ""
        while not stream.next_is_EOF():
            char = stream.read()
            if char in node:
                seq += char
                node_properties_pair = node[char]
                node = node_properties_pair[0]
            else:
                if seq != "":
                    stream.unread()
                    return seq, self._return_properties(node_properties_pair[1])
                else:
                    return char, self._return_properties(None)
        if seq != "":
            return seq, self._return_properties(node_properties_pair[1])
        assert False


def make_readtable(definition:list):
    """
    Creates a new readtable.

    The parameter ``definition`` should respect the following format::

        definition := [ entries*, default_entry ]

        entries := [ type_property_value, seq_or_seqs, other_properties? ]

        default_entry := ['DEFAULT', default_properties]

    ``type_property_value`` is the value associated with the type_property

    ``seq_or_seqs`` is a string or a list of strings.

    ``other_properties`` and ``default_properties`` are dictionaries.
    """
    read_table = Readtable()
    for spec in definition:
        if spec[0] == 'DEFAULT':
            read_table.default_properties.update(spec[1])
        else:
            seqs = spec[1] if isinstance(spec[1], list) else [spec[1]]
            properties = spec[2] if len(spec) >= 3 else {}
            for seq in seqs:
                existing_properties, _ = read_table.query(seq)
                if existing_properties is not read_table.default_properties:
                    assert existing_properties['type'] == spec[0]
                    existing_properties.update(properties)
                else:
                    new_seq_properties = Record({'type': spec[0]})
                    new_seq_properties.update(properties)
                    read_table.add_or_upd_seq(seq, new_seq_properties)
    return read_table

