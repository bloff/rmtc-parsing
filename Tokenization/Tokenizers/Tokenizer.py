from Common.Context import Context
from Common.Record import Record
from Streams.CharacterStream import *

class TokenizationContext(Context):
    pass

class Tokenizer(object):
    def __init__(self, context:TokenizationContext):
        self.context = context

    def run(self):
        raise NotImplementedError()

