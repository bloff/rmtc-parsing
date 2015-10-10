.. rmtc-parsing documentation master file, created by
   sphinx-quickstart on Sat Oct 10 19:53:00 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Readtable-Macro Transducer-Chain Parsing
========================================

This repository contains an implementation of a framework for using the
readtable-macro transducer-chain (RMTS) parsing method.

This is described in the following three blog posts:

-  `Lexing I: the off-side
   rule <https://bloff.github.io/lyc/2015/08/02/lexer.html>`__
-  `Lexing II: readtable–macro
   parsing <https://bloff.github.io/lyc/lexing,/syntax/2015/08/30/lexer-2.html>`__
-  `Parsing via chains of tree-transducers <http://bloff.github.io/lyc/blog/drafts.html>`__
   (yet to be written)

Structure of the source code
============================



:ref:`Common <common_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several utilities used throughout the project.

-  **Context** - A python class to simulate variables with dynamic scope
   (Lisp's *special variables*).
-  **Errors** - A collection of exceptions.
-  **Record** - A python dict accessible via **getattr**/**setattr** (so
   one can write ``record.item`` instead of ``record["item"]``).
-  **StringStuff** - Some functions to manipulate strings, and
   information about characters with non-single-space width.
-  **SysArgsParser** - A utility to parse command line arguments.
-  **Util** - General utility functions.
-  Unused by this project, needs to be refactored/moved:

   -  **Hierarchy**
   -  **Instance**
   -  **Memoize**

:ref:`Streams <streams_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Self-contained implementation of an object from which characters can be
read or written. This probably should be replaced with Python's own
*TextIOBase* class. But it was much simpler for me to just have a class
with exactly what I needed, instead of worrying about implementing
whatever Python needs. Will refactor this at some point.

-  **CharacterStream** - Is the base class.
-  **FileStream** - Implementation to read from a file.
-  **StringStream** - Implementation to read from a String.
-  **StreamPosition**, **StreamRange** - For describing a position in a
   stream, or a range of positions.
-  **IndentedCharacterStream** - This one allows for ``push`` and
   ``pop`` operations.


:ref:`Syntax <syntax_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~






.. comment
   Indices and tables
   ==================
   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`

