from Streams.CharacterStream import *

class Tokenizer(object):
    def __init__(self, stream: CharacterStream):
        self.stream = stream

    def run(self):
        raise NotImplementedError()

