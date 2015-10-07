from Tokenization.Tokenizers.IndentationReadtable import IndentationReadtableTokenizer
from .TokenizerRegistry import def_tokenizer_class
from Tokenization.StandardReadtable import standard_readtable

class StandardTokenizer(IndentationReadtableTokenizer):
    def __init__(self, stream):
        IndentationReadtableTokenizer.__init__(self, stream, standard_readtable)

def_tokenizer_class('Standard', StandardTokenizer)