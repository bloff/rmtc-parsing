class TreeTransducer(object):
    def __init__(self, name:str):
        self.name = name

    def transduce(self, tree):
        raise NotImplementedError()

