.. _streams_modules:

Streams
=======

.. _CharacterStream:

CharacterStream
---------------

.. automodule:: Streams.CharacterStream
   :members:

.. _FileStream:

FileStream
----------

.. automodule:: Streams.FileStream
   :members:

.. _StringStream:

StringStream
------------

.. automodule:: Streams.StringStream
   :members:


.. _StreamPosition:

StreamPosition
--------------
.. automodule:: Streams.StreamPosition
   :members:

.. _StreamRange:

StreamRange
-----------
.. automodule:: Streams.StreamRange
   :members:


.. _IndentedCharacterStream:

IndentedCharacterStream
-----------------------

Supose one was reading the following sequence of
characters, and did a ``push`` operation on the ``u`` character
(meaning, at the point where the next ``read`` instruction would
return the ``u`` character):

::

    a b u
        v w
          x y
        z
    c d

Then what happens is that any subsequent call to read will skip all
the whitespace characters before the column number of the ``u``
character (column 5 in this case). The stream will return all
remaining characters (at column 5 or after) up to (but excluding) the
newline character that precedes a line having a non-whitespace
character before column 5. At that point the stream returns EOF.

So in this case, subsequent calls to read would return ``'v'``,
``' '``, ``'w'``, ``'\n'``, ``' '``. ``' '``, ``'x'``, ``' '``,
``'y'``, ``'\n'``, ``'z'``, ``EOF``. At that point, a subsequent call
to read would produce an error.

Reading can only continue, then, after the ``pop`` instruction.
This would now produce ``'\n'``, ``'c'``, ``' '``, ``'d'``.

If one were to call push again on the ``'w'`` character, the
sequences would be

::

    'a', ' ', 'b', ' ',
    (PUSH) 'u', '\n', 'v', ' ',
    (PUSH) 'w', '\n', 'x', ' ', 'y'
    (POP)  '\n', 'z'
    (POP)  '\n', 'c', ' ', 'd'


.. automodule:: Streams.IndentedCharacterStream
   :members:
