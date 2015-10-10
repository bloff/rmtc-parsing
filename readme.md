#Readtable-Macro Transducer-Chain Parsing

This repository contains an implementation of a framework for using the readtable-macro transducer-chain (RMTS) parsing method.

This is described in the following three blog posts:

 * [Lexing I: the off-side rule](https://bloff.github.io/lyc/2015/08/02/lexer.html)
 * [Lexing II: readtable–macro parsing](https://bloff.github.io/lyc/lexing,/syntax/2015/08/30/lexer-2.html)
 * *[Parsing via chains of tree-transducers](http://bloff.github.io/lyc/blog/drafts.html)* (yet to be written)
 

##Structure of the source code

###Common
Several utilities used throughout the project.
* **Context** - A python class to simulate variables with dynamic scope (Lisp's *special variables*).
* **Errors** - A collection of exceptions.
* **Record** - A python dict accessible via __getattr__/__setattr__ (so one can write `record.item` instead of `record["item"]`).
* **StringStuff** - Some functions to manipulate strings, and information about characters with non-single-space width.
* **SysArgsParser** - A utility to parse command line arguments.
* **Util** - General utility functions.
* Unused by this project, needs to be refactored/moved:
    * **Hierarchy**
    * **Instance**
    * **Memoize**

###Streams
Self-contained implementation of an object from which characters can be read or written. This probably should be replaced with Python's own *TextIOBase* class. But it was much simpler for me to just have a class with exactly what I needed, instead of worrying about implementing whatever Python needs. Will refactor this at some point.

* **CharacterStream** - Is the base class.
* **FileStream** - Implementation to read from a file.
* **StringStream** - Implementation to read from a String.
* **StreamPosition**, **StreamRange** - For describing a position in a stream, or a range of positions.
* **IndentedCharacterStream** - This one allows for `push` and `pop` operations. Supose one was reading the following sequence of characters, and did a `push` operation on the `u` character (meaning, at the point where the next `read` instruction would return the `u` character):
```
a b u
    v w
      x y
    z
c d
```
Then what happens is that any subsequent call to read will skip all the whitespace characters before the column number of the `u` character (column 5 in this case). The stream will return all remaining characters (at column 5 or after) up to (but excluding) the newline character that precedes a line having a non-whitespace character before column 5. At that point the stream returns EOF. 
So in this case, subsequent calls to read would return `'v'`, `' '`, `'w'`, `'\n'`, `' '`. `' '`, `'x'`, `' '`, `'y'`, `'\n'`, `'z'`, `EOF`. At that point, a subsequent call to read would produce an error.
Reading can only continue, then, after the `pop` instruction. This would now produce `'\n'`, `'c'`, `' '`, `'d'`.
If one were to call push again on the `'w'` character, the sequences would be
```
'a', ' ', 'b', ' ',
(PUSH) 'u', '\n', 'v', ' ',
(PUSH) 'w', '\n', 'x', ' ', 'y'
(POP)  '\n', 'z'
(POP)  '\n', 'c', ' ', 'd'
```
    
###Syntax

* **