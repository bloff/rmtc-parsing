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


.. note::
   You may jump to the full `Table of contents`_ below. Following is an overview of the source code.


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
read, while keeping track of offset, and line and column numbers.
This probably should be replaced with Python's own
*TextIOBase* class. But it was much simpler for me to just have a class
with exactly what I needed, instead of worrying about implementing
whatever Python needs. Will refactor this at some point.

-  :ref:`CharacterStream` - Is the base class.
-  :ref:`FileStream` - Implementation to read from a file.
-  :ref:`StringStream` - Implementation to read from a String.
-  :ref:`StreamPosition`, :ref:`StreamRange` - For describing a position in a
   stream, or a range of positions.
-  :ref:`IndentedCharacterStream` - This one allows for ``push`` and
   ``pop`` operations. This is how we parse indentation in
   a recursive descent parser.


:ref:`Syntax <syntax_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Syntax types.

-  :ref:`Code` - The base class for all syntax types.
-  :ref:`Identifier` - An identifier.
-  :ref:`Literal` - A Literal.
-  :ref:`Node` and :ref:`Element` - A *Node* is a doubly-linked list, where each *Element* in the list holds
   (a reference to) an instance of *Code*. Currently we define 6 types of nodes:

   - :ref:`Form` - A Form denotes a Node where the first element is singled out, and called the *head* of the form.
     It is usually understood that the first element is *applied* to the remaining elements, called *arguments* of the form.
     One may denote a Form by ``head( arg1, arg2, ...)`` or ``⦅head arg1 arg2 ...⦆``.
   - :ref:`Tuple` - A Tuple is a Node where no element is singled out. It usually represents a sequence of elements, taken
     together.
     One may denote a Tuple by ``(elm1, elm2, ...)``.
   - :ref:`PreForm` and :ref:`PreTuple` - A PreForm or a PreTuple denotes a Form or a Tuple, respectively, if it holds
     two or more elements appear, or, if there is a single element, denotes that very same single element.
     One may denote a PreForm by ``ₐ⟅elm1 ...⟆ₐ``, and a PreTuple by ``⟅elm1 ...⟆``.
   - :ref:`Punctuator` - A Node whose single element should be parsed for punctuation.
- :ref:`NodeIterator` - An iterator for iterating over the elements of a Node.
- :ref:`Token` - An Element representing a token. The outcome of tokenization should be a single Node instance whose
  elements are all Tokens.
- :ref:`LispPrinter` - A collection of functions for printing Code using S-Expressions (Lisp prefix notation).



:ref:`Tokenization <tokenization_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Readtable-macro parsing.

- :ref:`Readtable` - Readtables map sequence of characters to dictionaries of properties.
- :ref:`TokenizationContext`
- :ref:`Tokenizer` - A tokenizer generates tokens (:ref:`Token`) from a :ref:`CharacterStream`.
- :ref:`IndentationReadtableTokenizer` - A tokenizer that uses a readtable to read indented blocks of code.
- :ref:`DelimiterTokenizer` - Tokenizer for parsing blocks of code surrounded by delimiters.
- :ref:`StringTokenizer` - Tokenizer for strings with interpolated code.
- :ref:`CommentTokenizer` -  Tokenizer for comments with interpolated code.
- :ref:`RawCommentTokenizer` - Comments without interpolated code.
- :ref:`DelimitedIdentifierTokenizer` - Tokenizer for identifiers surrounded by delimiters.


:ref:`Transducers <transducers_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tree transducers.

- :ref:`Arrangement` - A transformation of a single node.
- :ref:`ArrangementRule` - A rule for when and how to transform a child of a node.
- :ref:`ReadDirection` - Left-to-right or right-to-left.
- :ref:`TreeTransducer` - A transformation of a tree (represented by nested nodes).
    - :ref:`TopDownTreeTransducer`
    - :ref:`BottomUpTreeTransducer`
    - :ref:`ConvertPreForms`
- The arrangement rules currently implemented are:
   - :ref:`ApplyToRest` - To process a form like ``return``, which, if appearing in isolation, actually means ``return()``.
   - :ref:`Block` - Indented blocks.
   - :ref:`Comments` - Comments.
   - :ref:`Constituents` - Constituents (identifiers, numerical literals, etc)
   - :ref:`DefaultPunctuation` - Parses ,-and-;-separated lists into nested tuples.


:ref:`Parsers <parsers_modules>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Parsers for specific languages (currently only ``lyc``).





.. comment
   Indices and tables
   ==================
   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`


Table of contents
=================

.. toctree::
   :maxdepth: 2

   API/common
   API/streams
   API/syntax
   API/tokenization
   API/transducers
   API/parsers

