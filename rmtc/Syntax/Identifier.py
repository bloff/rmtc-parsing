from rmtc.Streams.StreamRange import StreamRange
from rmtc.Syntax.Code import *

class Identifier(Code):
    """
    An identifier with a syntactic name, and an extra (called *semantic*) name.

    :param full_name: The identifier's full name, which should have the syntactic
       name and semantic name separated by a hash character.
       As in :literal:`syntactic_name#semantic_name`.
       If there is no semantic name, the hash can be omitted. If there is no semantic
       name but the syntactic name has a hash, just append a hash to it.

    :param stream_range: The range where the identifier appears in.
    """

    def __init__(self, full_name:str, stream_range:StreamRange=None):
        super(Identifier, self).__init__()
        name, semantic_name = Identifier.split_name(full_name)
        self.name = name
        self.semantic_name = semantic_name
        self.range = stream_range if stream_range is not None else StreamRange()

    def __str__(self):
        if any(c in self.name for c in u'»“” ,;()[]{}') or self.semantic_name is not None:
            return '«' + self.full_name + '»'
        else:
            return self.name

    @property
    def full_name(self):
        """
        Returns the full name (syntactic name plus hash plus semantic name) if semantic name is non-empty, or else just the syntactic name.
        """
        if self.semantic_name is None:
            return self.name
        else:
            return self.name + '#' + self.semantic_name


    def __repr__(self):
        return '«' + repr(self.name)[1:-1] + '»'

    @staticmethod
    def split_name(name:str) -> (str, str):
        """
        Turns "a#b" into ("a", "b"), and "a#" or just "a" into ("a", None).
        """
        if '#' not in name:
            return name, None
        else:
            r = name.rsplit('#', 1)
            if r[1] == '':
                return r[0], None
            else:
                return r[0], r[1]


