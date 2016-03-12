from typing import Union

from rmtc.Parsers.RMTCParser import RMTCParser
from rmtc.Streams.CharacterStream import CharacterStream
from rmtc.Streams.IndentedCharacterStream import IndentedCharacterStream
from rmtc.Tokenization.Readtable import make_readtable, RT
from rmtc.Tokenization.TokenizationContext import TokenizationContext
from rmtc.Tokenization.Tokenizers.Delimiter import DelimiterTokenizer
from rmtc.Tokenization.Tokenizers.IndentationReadtable import IndentationReadtableTokenizer
from rmtc.Tokenization.Tokenizers.RawComment import RawCommentTokenizer
from rmtc.Tokenization.Tokenizers.String import StringTokenizer
from rmtc.Transducers.Arrangement import Arrangement
from rmtc.Transducers.Arrangements.LeftRightNaryOperatorMultipleHeads import LeftRightNaryOperatorMultipleHeads
from rmtc.Transducers.Arrangements.Comments import RawComment
from rmtc.Transducers.Arrangements.Constituents import Constituent
from rmtc.Transducers.Arrangements.DefaultPunctuation import DefaultPunctuation
from rmtc.Transducers.Arrangements.Delimiters import ParenthesisWithHead, ParenthesisNoHead, \
    Delimiters
from rmtc.Transducers.Arrangements.IfElse import InfixIfElse, IfElifElse
from rmtc.Transducers.Arrangements.LeftRightBinaryOperator import LeftRightBinaryOperator
from rmtc.Transducers.Arrangements.LeftRightBinaryOperatorTwoSymbols import LeftRightBinaryOperatorTwoSymbols
from rmtc.Transducers.Arrangements.LeftRightBinaryTokenCapturingOperator import LeftRightBinaryTokenCapturingOperator
from rmtc.Transducers.Arrangements.LeftRightNaryOperator import LeftRightNaryOperator
from rmtc.Transducers.Arrangements.LeftRightUnaryPrefixNospaceOperator import LeftRightUnaryPrefixNospaceOperator
from rmtc.Transducers.Arrangements.LeftRightUnaryPrefixNospaceTokenCapturingOperator import LeftRightUnaryPrefixNospaceTokenCapturingOperator
from rmtc.Transducers.Arrangements.RightLeftBinaryOperator import RightLeftBinaryOperator
from rmtc.Transducers.Arrangements.RightLeftUnaryPrefixOperator import RightLeftUnaryPrefixOperator
from rmtc.Transducers.Arrangements.Segment import Segment
from rmtc.Transducers.Arrangements.Strings import Strings
from rmtc.Transducers.ConvertPreForms import ConvertPreforms
from rmtc.Transducers.TopDownTreeTransducer import TopDownTreeTransducer

from rmtc.Expansion.ExpansionContext import ExpansionContext
from rmtc.Expansion.Expander import DefaultExpander

#from rmtc.Transducers.Arrangements.Delimiters import BracketsWithHead



## READTABLE ##

default_readtable = make_readtable( [

    [RT.MACRO, ['(', '[', '{' ],
     {'tokenizer': 'DelimiterTokenizer'}],


    
# """ strings
    
    [RT.MACRO, "'",
     {'tokenizer': 'SingleQuoteStringTokenizer',
      'preserve-leading-whitespace': True}],

    [RT.MACRO, '"',
     {'tokenizer': 'DoubleQuoteStringTokenizer',
      'preserve-leading-whitespace': True}],

    #
    # [RT.MACRO, "'''",
    #  {'tokenizer': 'TripleSingleQuoteStringTokenizer',
    #   'preserve-leading-whitespace': True}],
    #
    # [RT.MACRO, '"""',
    #  {'tokenizer': 'TripleDoubleQuoteStringTokenizer',
    #   'preserve-leading-whitespace': True}],

    

    
    [RT.MACRO, '#',
     {'tokenizer': 'CommentTokenizer',
      'preserve-leading-whitespace': True}],


    [RT.CLOSING, ['"', "'",
                  # "'''", '"""',
                  ')', ']', '}'], ],



    [RT.PUNCTUATION, [',', ':' ], ],
    # [RT.ISOLATED_CONSTITUENT, ','],

    
    
    [RT.ISOLATED_CONSTITUENT,
     ['.',
      '+', '-', '*', '/', '//', '%', '**', '@',
      '&', '^', '<<', '>>', '~',
      '=',
      '==', '!=', '<', '>', '<=', '>=',
      '+=', '-=', '*=', '/=', '//=', '%=',
      '**=', '@=', '|=', '^=', '&=', '<<=', '>>=',
      '->' ], ],

    

    # space, tab, "vertical tab", "formfeed"
    [RT.WHITESPACE, [' ', '\t', '\x0b', '\x0c' ], ],


    [RT.NEWLINE, ['\n', '\r\n', '\r' ], ],



    ['DEFAULT',
     {'type': RT.CONSTITUENT}],

    ])







## TOKENIZERS ##

class AnokyDelimiterTokenizer(DelimiterTokenizer):
    DELIMITER_PAIRS = { '(' : ')',
                        '[' : ']',
                        '{' : '}'}




class AnokySingleQuoteStringTokenizer(StringTokenizer):
    MY_OPENING_DELIMITER = "'"
    MY_CLOSING_DELIMITER = "'"

class AnokyDoubleQuoteStringTokenizer(StringTokenizer):
    MY_OPENING_DELIMITER = '"'
    MY_CLOSING_DELIMITER = '"'


# class PythonTripleSingleQuoteStringTokenizer(StringTokenizer):
#     MY_OPENING_DELIMITER = "'''"
#     MY_CLOSING_DELIMITER = "'''"

# class PythonTripleDoubleQuoteStringTokenizer(StringTokenizer):
#     MY_OPENING_DELIMITER = '"""'
#     MY_CLOSING_DELIMITER = '"""'



class AnokyCommentTokenizer(RawCommentTokenizer):
    OPENING_DELIMITER = '#'








## TRANSDUCER CHAIN ##

default_python_transducer_chain = None


def define_default_anoky_transducer_chain():
    global default_python_transducer_chain


    tt_constituent = TopDownTreeTransducer("Constituent",
                                           Arrangement([Constituent()]))

    # comments, \, indentation, strings
    tt_primary = TopDownTreeTransducer("Primary",
                                       Arrangement([
                                           #Comment(),
                                           RawComment(),
                                           
                                           Segment(),
                                           
                                           ParenthesisWithHead(),
                                           ParenthesisNoHead(),
                                           
                                           #BracketsWithHead({'['}),
                                           
                                           Delimiters({'[','{'}),
                                           
                                           Strings({"'",'"'}), # "'''",'"""'}),

                                           LeftRightBinaryTokenCapturingOperator({'.'}),
                                           
                                           ]))

    
    
    
    # "binding or tuple display, list display, dictionary display, set display"
    #tt_secondary


    # "subscription, slicing, call, attribute reference"
    # tt_tertiary = TopDownTreeTransducer("Tertiary",
    #                                     Arrangement([
    #                                         )
                                            # BracketsWithHead({'['}),
                                            # Delimiters({'[','{'})]))


    #tt_await??

    tt_punctuation = TopDownTreeTransducer("Punctuation",
                                           Arrangement([DefaultPunctuation()]))

    # tt_commaoperator = TopDownTreeTransducer("Comma as binary operator",
    #                                          Arrangement([RightLeftBinaryOperator({','})]))
    

    tt_exponentiation = TopDownTreeTransducer("Exponentiation",
                                              Arrangement([
                                                  LeftRightBinaryOperator({'**'})]))

    tt_tilde = TopDownTreeTransducer("Bitwise NOT",
                    Arrangement([LeftRightUnaryPrefixNospaceTokenCapturingOperator({'~'})]))


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
                                                   'in', 'is',}),
                                               LeftRightNaryOperatorMultipleHeads('compare',
                                                   {'==', '!=', '<', '>', '<=', '>='}),
                                               LeftRightBinaryOperatorTwoSymbols({
                                                   ('not', 'in'), ('is', 'not')})]))


    

    tt_not = TopDownTreeTransducer("Not",
                                   Arrangement([RightLeftUnaryPrefixOperator({'not'})]))
    

    tt_and = TopDownTreeTransducer("And",
                                   Arrangement([LeftRightNaryOperator({'and'})]))

    tt_or = TopDownTreeTransducer("Or",
                                   Arrangement([LeftRightNaryOperator({'or'})]))



    



    tt_conditional = TopDownTreeTransducer("Conditionals",
                                           Arrangement([
                                               InfixIfElse({('if', 'else')}),
                                               IfElifElse()]))
    

    #tt_lambda = TopDownTreeTransducer("Lambdas", Arrangement([ ]))


    tt_assignment = TopDownTreeTransducer("Assignments",
                                          Arrangement([
                                              RightLeftBinaryOperator({'=',
                                                                       '+=', '-=', '*=', '/=',
                                                                       '//=', '%=', '@=',
                                                                       '<<=', '>>=',
                                                                       '&=', '^=', '|=' })]))
                                              

    # add to transducer chain
    tt_starguments = TopDownTreeTransducer("Prefixed Stars/Doublestars",
                                           Arrangement([
                                               LeftRightUnaryPrefixNospaceOperator({'*', '**'})
                                           ]))


    # tt_unaryadd = TopDownTreeTransducer("Unary Plus/Minus",
    #                                     Arrangement([LeftRightUnaryPrefixNospaceTokenCapturingOperator({'+', '-'})
    #                                     ]))


    tt_as = TopDownTreeTransducer("infix as",
                                  Arrangement([
                                      LeftRightBinaryOperator({'as'})]))




    default_python_transducer_chain = [ tt_constituent,
                                        tt_primary,
                                        #tt_,
                                        #tt_tertiary,


                                        
                                        tt_punctuation,
                                        # tt_commaoperator,


                                        
                                        tt_exponentiation,

                                        tt_tilde,

                                        tt_multiplication,
                                        tt_addition,

                                        tt_starguments,

                                        tt_bit_shift,
                                        tt_bit_and,
                                        tt_bit_xor,
                                        tt_bit_or,

                                        tt_as,
                                        
                                        tt_comparisons,
                                        tt_not,
                                        tt_and,
                                        tt_or,
                                        tt_conditional,
                                        
                                        #tt_lambda,

                                        tt_assignment,
                                        
                                        ConvertPreforms() ]



define_default_anoky_transducer_chain()













class AnokyParser(RMTCParser):

    def __init__(self):
        RMTCParser.__init__(self, TokenizationContext("PTC"),
                            default_readtable,
                            IndentationReadtableTokenizer,
                            default_python_transducer_chain)
        self.tokenization_context.set(
            # ..
            DelimiterTokenizer = AnokyDelimiterTokenizer,
            SingleQuoteStringTokenizer = AnokySingleQuoteStringTokenizer,
            DoubleQuoteStringTokenizer = AnokyDoubleQuoteStringTokenizer,
            # TripleSingleQuoteStringTokenizer = PythonTripleSingleQuoteStringTokenizer,
            # TripleDoubleQuoteStringTokenizer = PythonTripleDoubleQuoteStringTokenizer,
            CommentTokenizer = AnokyCommentTokenizer,
            )

        # For Anoky we do not make use of DelimitedIdentifiers or non-raw Comments.

        


    def _get_stream(self, code_or_stream:Union[str, CharacterStream]):
        stream = RMTCParser._get_stream(self, code_or_stream)
        if not isinstance(stream, IndentedCharacterStream):
            stream = IndentedCharacterStream(stream)
        return stream




















