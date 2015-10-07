class Record(dict):
    def __init__(self, _dict=None, **kwargs):
        if _dict is not None:
            assert isinstance(_dict, dict)
            super(Record, self).__init__(_dict)
        else:
            super(Record, self).__init__()

        self.__dict__ = self
        self.update(kwargs)

