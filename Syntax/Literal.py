from Streams import StreamRange
from .Code import *

class Literal(Code):
    def __init__(self, type, value, range:StreamRange=None):
        super(Literal, self).__init__()
        self.type = type
        self.value = value
        self.range = range if range is not None else StreamRange()

    def __str__(self):
        if isinstance(self.value, int):
            return str(self.value)
        elif isinstance(self.value, str):
            return "“%s”" % repr(self.value)[1:-1]
        else:
            # FIXME?
            return str(self.value)

