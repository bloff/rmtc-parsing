
def is_not_none(*args):
    assert len(args) % 2 == 0
    try:
        j = iter(args)
        while True:
            base = next(j)
            if base is None: return False
            path = next(j)
            items = path.split('.')
            for key in items[1:]:
                if not hasattr(base, key): return False
                base = getattr(base, key)
                if base is None: return False
    except StopIteration:
        pass

    return True