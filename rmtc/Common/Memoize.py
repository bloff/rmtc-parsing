def _get_id_tuple(f, args, kwargs, mark=object()):
    """ 
    Some quick'n'dirty way to generate a unique key for an specific call.
    """
    l = [id(f)]
    for arg in args:
        l.append(id(arg))
    l.append(id(mark))
    for k, v in kwargs:
        l.append(k)
        l.append(id(v))
    return tuple(l)

def memoize(f):
    """ 
    A basic memoizer.
    """
    _memoized = {}
    def memoized(*args, **kwargs):
        key = _get_id_tuple(f, args, kwargs)
        if key not in _memoized:
            _memoized[key] = f(*args, **kwargs)
        return _memoized[key]
    return memoized