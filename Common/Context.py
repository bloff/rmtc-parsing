class _ContextBlock(object):
    def __init__(self, stack, kwargs):
        self._stack = stack
        self.kwargs = kwargs
    def __enter__(self):
        self._stack.append(self.kwargs)
    def __exit__(self, t, v, tb):
        self._stack.pop()

class Context(object):
    def __init__(self, name, **root_bindings):
        self._name = name
        self._root = root_bindings
        self._stack = [root_bindings]


    def __getattr__(self, name):
        """:type name unicode"""
        if name.startswith(u'_'):
            return self.__dict__[name]
        for scope in reversed(self._stack):
            if name in scope:
                return scope[name]
        raise AttributeError("No such variable %s in context %s"%(name, self._name))

    def let(self, **kwargs):
        return _ContextBlock(self._stack, kwargs)

    def set(self, **kwargs):
        for key in kwargs:
            self._root[key] = kwargs[key]

    def __setattr__(self, name, value):
        if name.startswith(u'_'):
            self.__dict__[name] = value
        else:
            raise AttributeError("Context variables can only be set using `with env.let()`")

    def __getitem__(self, item):
        return self.__getattr__(item)
