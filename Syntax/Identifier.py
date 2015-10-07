from Streams.StreamRange import StreamRange
from .Code import *

class Identifier(Code):
    def __init__(self, full_name:str, stream_range:StreamRange=None):
        super(Identifier, self).__init__()
        name, semantic_extra = Identifier.split_name(full_name)
        self.name = name
        self.semantic_extra = semantic_extra
        self.range = stream_range if stream_range is not None else StreamRange()

    def __str__(self):
        if any(c in self.name for c in u'»“” ,;()[]{}') or self.semantic_extra is not None:
            return '«' + self.full_name + '»'
        else:
            return self.name

    @property
    def full_name(self):
        if self.semantic_extra is None:
            return self.name
        else:
            return self.name + '#' + self.semantic_extra


    def __repr__(self):
        return '«' + repr(self.name)[1:-1] + '»'

    @staticmethod
    def split_name(name:str) -> (str, str, str):
        if '#' not in name:
            return name, None
        else:
            r = name.split('#', 1)
            if r[1] == '':
                return r[0], None
            else:
                return r[0], r[1]


