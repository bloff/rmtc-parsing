#Readtable-Macro Transducer-Chain Parsing

This repository contains an implementation of a framework for using the readtable-macro transducer-chain (RMTS) parsing method.

This is described in the following three blog posts:

 * [Lexing I: the off-side rule](https://bloff.github.io/lyc/2015/08/02/lexer.html).
 * [Lexing II: readtable–macro parsing](https://bloff.github.io/lyc/lexing,/syntax/2015/08/30/lexer-2.html).
 * *[Parsing via chains of tree-transducers](http://bloff.github.io/lyc/blog/drafts.html)* (yet to be written).
 

[Read the docs here!](https://rmtc-parsing.readthedocs.org/en/master/)

##Dependencies

* Python 3
* `setuptools` (should come with distribution)
* `pip` (to install dependencies). To install pip, do
```
sudo easy_install3 pip
```
* Sphinx (for documentation)
```
sudo pip3 install Sphinx sphinx-rtd-theme sphinxcontrib-inlinesyntaxhighlight sphinx-autobuild
```

##To test
run:
```
python3 tokenize.py 0.Input/_compile.ly
```
or
```
python3 arranger.py --verbose 0.Input/_compile.ly
```