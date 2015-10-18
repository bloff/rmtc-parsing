from Common.Context import Context



class TokenizationContext(Context):
    """
    A ``Context`` to be used during tokenization.
    For readtable-macro parsing, it is expected that the ``context``
    field will include at least a ``stream`` (:ref:`CharacterStream`)
    and a ``readtable`` (:ref:`Readtable`).
    """
    pass