
from typing import Union

from rmtc.Parsers.RMTCParser import RMTCParser
from rmtc.Streams.CharacterStream import CharacterStream
from rmtc.Streams.IndentedCharacterStream import IndentedCharacterStream
from rmtc.Tokenization.Readtable import make_readtable, RT
from rmtc.Tokenization.Tokenizers.RawComment import RawCommentTokenizer
from rmtc.Tokenization.Tokenizers.Comment import CommentTokenizer
from rmtc.Tokenization.Tokenizers.DelimitedIdentifierTokenizer import DelimitedIdentifierTokenizer
from rmtc.Tokenization.Tokenizers.Delimiter import DelimiterTokenizer
from rmtc.Tokenization.Tokenizers.IndentationReadtable import IndentationReadtableTokenizer
from rmtc.Tokenization.Tokenizers.String import StringTokenizer
from rmtc.Tokenization.TokenizationContext import TokenizationContext
from rmtc.Transducers.Arrangements.ApplyToRest import ApplyToRest
from rmtc.Transducers.Arrangement import Arrangement
from rmtc.Transducers.Arrangements.LeftRightBinaryOperator import LeftRightBinaryOperator
from rmtc.Transducers.TopDownTreeTransducer import TopDownTreeTransducer
from rmtc.Transducers.ConvertPreForms import ConvertPreforms
from rmtc.Transducers.ReadDirection import ReadDirection
from rmtc.Transducers.Arrangements.Block import Block
from rmtc.Transducers.Arrangements.Comments import Comment, RawComment
from rmtc.Transducers.Arrangements.Constituents import Constituent
from rmtc.Transducers.Arrangements.DefaultPunctuation import DefaultPunctuation
from rmtc.Transducers.Arrangements.Delimiters import ParenthesisWithHead, ParenthesisNoHead, \
    ApplyParenthesis, Delimiters
from rmtc.Transducers.Arrangements.IfElse import InfixIfElse, IfElifElse
from rmtc.Transducers.Arrangements.LeftRightBinaryOperatorReversedArgs import LeftRightBinaryOperatorReversedArgs
from rmtc.Transducers.Arrangements.LeftRightBinaryOperatorTwoSymbols import LeftRightBinaryOperatorTwoSymbols
from rmtc.Transducers.Arrangements.LeftRightBinaryTokenCapturingOperator import LeftRightBinaryTokenCapturingOperator
from rmtc.Transducers.Arrangements.LeftRightNaryOperator import LeftRightNaryOperator
from rmtc.Transducers.Arrangements.LeftRightUnaryPostfixNospaceOperator import LeftRightUnaryPostfixNospaceOperator
from rmtc.Transducers.Arrangements.LeftRightUnaryPrefixNospaceTokenCapturingOperator import \
    LeftRightUnaryPrefixNospaceTokenCapturingOperator
from rmtc.Transducers.Arrangements.RightLeftBinaryOperator import RightLeftBinaryOperator
from rmtc.Transducers.Arrangements.RightLeftUnaryPrefixNospaceOperator import RightLeftUnaryPrefixNospaceOperator
from rmtc.Transducers.Arrangements.RightLeftUnaryPrefixOperator import RightLeftUnaryPrefixOperator
from rmtc.Transducers.Arrangements.Strings import Strings
from rmtc.Transducers.Arrangements.TransformationArrow import TransformationArrow



## READTABLE ##

default_python_readtable = make_readtable( [

    [RT.MACRO, ['(', '[', '{' ],
     {'tokenizer': 'DelimiterTokenizer'}],


    

# """ strings
    [RT.MACRO, ['"', "'"],
     {'tokenizer': 'StringTokenizer',
      'preserve-leading-whitespace': True}],
    
    [RT.MACRO, '#',
     {'tokenizer': 'CommentTokenizer',
      'preserve-leading-whitespace': True}],


    [RT.CLOSING, ['"', "'",
                  ')', ']', '}'], ],



    [RT.PUNCTUATION, [',' ], ],

    
    
    [RT.ISOLATED_CONSTITUENT,
     ['.',
      '+', '-', '*', '/', '//', '%', '**', '@',
      '&', '^', '<<', '>>', '~',
      '==', '!=', '<', '>', '<=', '>=',
      ':', ';' ], ],

    # space, tab, "vertical tab", "formfeed"
    [RT.WHITESPACE, [' ', '\t', '\x0b', '\x0c' ], ],


    [RT.NEWLINE, ['\n', '\r\n', '\r' ], ],



    ['DEFAULT',
     {'type': RT.CONSTITUENT}],

    ])







## TOKENIZERS ##

class PythonDelimiterTokenizer(DelimiterTokenizer):
    DELIMITER_PAIRS = { '(' : ')',
                        '[' : ']',
                        '{' : '}'}




class PythonSingleQuoteStringTokenizer(StringTokenizer):
    MY_OPENING_DELIMITER = "'"
    MY_CLOSING_DELIMITER = "'"

class PythonDoubleQuoteStringTokenizer(StringTokenizer):
    MY_OPENING_DELIMITER = '"'
    MY_CLOSING_DELIMITER = '"'











## TRANSDUCER CHAIN ##

default_python_transducer_chain = None


def define_default_python_transducer_chain():
    global default_python_transducer_chain


    tt_constituent = TopDownTreeTransducer("Constituent",
                                           Arrangement([Constituent()]))

    # comments, \, indentation, strings
    tt_primary = TopDownTreeTransducer("Primary",
                                       Arrangement([
                                           Comment(),
                                           
                                           Block(),
                                           
                                           ParenthesisWithHead(),
                                           ParenthesisNoHead(),
                                           Delimiters({'[','{'}),
                                           
                                           Strings(),
                                           ]))

    
    
    
    # "binding or tuple display, list display, dictionary display, set display"
    #tt_secondary


    # "subscription, slicing, call, attribute reference"
    #tt_tertiary


    #tt_await??
    

    tt_exponentiation = TopDownTreeTransducer("Exponentiation",
                                              Arrangement([
                                                  LeftRightBinaryOperator({'**'})]))
    


    tt_multiplication = TopDownTreeTransducer("Multiplication, Division, etc.",
                                              Arrangement([
                                                  LeftRightBinaryOperator({
                                                      '*', '@', '/', '//', '%'})]))

    tt_addition = TopDownTreeTransducer("Addition, Subtraction",
                                        Arrangement([
                                            LeftRightBinaryOperator({'+', '-'})]))

    

    tt_bit_shift = TopDownTreeTransducer("Bit Shifts",
                                       Arrangement([LeftRightBinaryOperator({'<<', '>>'})]))

    tt_bit_and = TopDownTreeTransducer("Bitwise AND",
                                       Arrangement([LeftRightBinaryOperator({'&'})]))

    tt_bit_xor = TopDownTreeTransducer("Bitwise XOR",
                                       Arrangement([LeftRightBinaryOperator({'^'})]))

    tt_bit_or = TopDownTreeTransducer("Bitwise OR",
                                       Arrangement([LeftRightBinaryOperator({'|'})]))



    
    tt_comparisons = TopDownTreeTransducer("Comparisons, Membership/Identity Tests",
                                           Arrangement([
                                               LeftRightBinaryOperator({
                                                   'in', 'is', '==', '!=',
                                                   '<', '>', '<=', '>='}),
                                               LeftRightBinaryOperatorTwoSymbols({
                                                   ('not', 'in'), ('is', 'not')})]))


    

    tt_not = TopDownTreeTransducer("Not",
                                   Arrangement([RightLeftUnaryPrefixOperator({'not'})]))
    

    tt_and = TopDownTreeTransducer("And",
                                   Arrangement([LeftRightBinaryOperator({'and'})]))

    tt_or = TopDownTreeTransducer("Or",
                                   Arrangement([LeftRightBinaryOperator({'or'})]))



    



    tt_conditional = TopDownTreeTransducer("Conditionals",
                                           Arrangement([
                                               InfixIfElse({('if', 'else')}),
                                               IfElifElse()]))
    

    #tt_lambda = TopDownTreeTransducer("Lambdas", Arrangement([ ]))
    


    default_python_transducer_chain = [ tt_constituent,
                                        tt_primary,
                                        #tt_,
                                        tt_exponentiation,
                                        tt_multiplication,
                                        tt_addition,
                                        tt_bit_shift,
                                        tt_bit_and,
                                        tt_bit_xor,
                                        tt_bit_or,
                                        tt_comparisons,
                                        tt_not,
                                        tt_and,
                                        tt_or,
                                        tt_conditional, ]
                                        #tt_lambda,
                                        #ConvertPreforms() ]



define_default_python_transducer_chain()













class PythonParser(RMTCParser):

    def __init__(self):
        RMTCParser.__init__(self, TokenizationContext("PTC"),
                            default_python_readtable,
                            IndentationReadtableTokenizer,
                            default_python_transducer_chain)
        self.tokenization_context.set(
            # ..
            DelimiterTokenizer = PythonDelimiterTokenizer,
            SingleQuoteStringTokenizer = PythonSingleQuoteStringTokenizer,
            DoubleQuoteStringTokenizer = PythonDoubleQuoteStringTokenizer,
            CommentTokenizer = RawCommentTokenizer,
            )

        # For Python we do not make use of DelimitedIdentifiers or non-raw Comments.

        


    def _get_stream(self, code_or_stream:Union[str, CharacterStream]):
        stream = RMTCParser._get_stream(self, code_or_stream)
        if not isinstance(stream, IndentedCharacterStream):
            stream = IndentedCharacterStream(stream)
        return stream




















