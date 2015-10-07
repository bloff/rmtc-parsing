from Common.Record import Record
from Streams.CharacterStream import CharacterStream

RT_WHITESPACE = 1
RT_NEWLINE = 2
RT_TOKEN = 3
RT_CONSTITUENT = 4
RT_MACRO = 5
RT_INVALID = 6
RT_CLOSING = 7
RT_PUNCTUATION = 8

class Readtable(object):
    def __init__(self):
        self.root_node = {}
        self.default_properties = Record({})

    def return_properties(self, properties):
        return properties if properties is not None else self.default_properties

    # associates a given string (sequence of characters) with the given properties dictionary,
    # or updates the associated properties dictionary, if one is already present
    def add_or_upd_seq(self, sequence, properties):
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


    # returns a pair (properties, continuation_possible), where
    # properties is the properties associated with the given sequence, or self.default_properties
    # if the sequence does not appear in the read-table, and
    # continuation_possible is True iff the sequence can be extended to some other (longer) sequence in the read-table
    def probe_seq(self, seq):
        node = self.root_node
        node_properties_pair = [{}, None]
        for char in seq:
            if char not in node:
                return self.default_properties, False
            else:
                node_properties_pair = node[char]
                node = node_properties_pair[0]
        properties = self.return_properties(node_properties_pair[1])
        continuation_possible = len(node_properties_pair[0]) > 0
        return properties, continuation_possible


    # reads the stream char by char as long as the read sequence of characters is an entry on the readtable
    # returns a pair with the largest possible such sequence and the associated properties
    # if the first character has no continuation in the readtable, returns ("", None)
    def probe_stream(self, stream:CharacterStream):
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
                    return seq, self.return_properties(node_properties_pair[1])
                else:
                    return char, self.return_properties(None)
        if seq != "":
            return seq, self.return_properties(node_properties_pair[1])
        assert False


    # behaves as probe_seq when given a str, and as probe_stream when given a stream
    def probe(self, sequence_or_stream):
        if isinstance(sequence_or_stream, str):
            return self.probe_seq(sequence_or_stream)
        else:
            return self.probe_stream(sequence_or_stream)

def make_read_table(definition:list):
    read_table = Readtable()
    for spec in definition:
        if spec[0] == 'DEFAULT':
            read_table.default_properties.update(spec[1])
        else:
            seqs = spec[1] if isinstance(spec[1], list) else [spec[1]]
            properties = spec[2] if len(spec) >= 3 else {}
            for seq in seqs:
                existing_properties, _ = read_table.probe_seq(seq)
                if existing_properties is not read_table.default_properties:
                    assert existing_properties['type'] == spec[0]
                    existing_properties.update(properties)
                else:
                    new_seq_properties = Record({'type': spec[0]})
                    new_seq_properties.update(properties)
                    read_table.add_or_upd_seq(seq, new_seq_properties)
    return read_table

