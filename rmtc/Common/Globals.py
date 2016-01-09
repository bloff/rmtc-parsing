import builtins
from rmtc.Common.Record import Record

class _Globals(object):
    def __getattr__(self, name:str):
        key = "GLOBALS::" + name
        if not hasattr(builtins, key):
            setattr(builtins, key, Record())
        return getattr(builtins, key)

    def __setattr__(self, key, value):
        raise AttributeError()


G = _Globals()