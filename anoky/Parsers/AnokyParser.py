from typing import Union

from anoky.Parsers.RMTCParser import RMTCParser
from anoky.Streams.CharacterStream import CharacterStream
from anoky.Streams.IndentedCharacterStream import IndentedCharacterStream
from anoky.tokenization.readtable import make_readtable, RT
from anoky.tokenization.string_tokenizer import StringTokenizer
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizers.delimiter_tokenizer import DelimiterTokenizer
from anoky.tokenization.tokenizers.raw_comment_tokenizer import RawCommentTokenizer
from anoky.tokenization.tokenizers.readtable_tokenizer import IndentationReadtableTokenizer
from anoky.transducers.arrangement import Arrangement
from anoky.transducers.arrangements.apply_in_isolation import ApplyInIsolation
from anoky.transducers.arrangements.apply_to_rest import ApplyToRest
from anoky.transducers.arrangements.assignment_segment import AssignmentSegment
from anoky.transducers.arrangements.comments import RawComment
from anoky.transducers.arrangements.constituents import Constituent
from anoky.transducers.arrangements.default_punctuation import DefaultFormPunctuation, \
    DefaultSeqPunctuation, ForPunctuation, Skip2Punctuation
from anoky.transducers.arrangements.delimiters import ParenthesisWithHead, ParenthesisNoHead, \
    Delimiters
from anoky.transducers.arrangements.if_else import InfixIfElse, FormWithDirectives
from anoky.transducers.arrangements.left_right_binary_operator import LeftRightBinaryOperator
from anoky.transducers.arrangements.left_right_binary_operator_two_symbols import LeftRightBinaryOperatorTwoSymbols
from anoky.transducers.arrangements.left_right_binary_token_capturing_operator import LeftRightBinaryTokenCapturingOperator
from anoky.transducers.arrangements.left_right_nary_operator import LeftRightNaryOperator
from anoky.transducers.arrangements.left_right_nary_operator_multiple_heads import LeftRightNaryOperatorMultipleHeads
from anoky.transducers.arrangements.left_right_unary_prefix_nospace_operator import LeftRightUnaryPrefixNospaceOperator
from anoky.transducers.arrangements.left_right_unary_prefix_nospace_token_capturing_operator import LeftRightUnaryPrefixNospaceTokenCapturingOperator
from anoky.transducers.arrangements.multiple_assignment import MultipleAssignment
from anoky.transducers.arrangements.right_left_binary_operator import RightLeftBinaryOperator
from anoky.transducers.arrangements.right_left_unary_prefix_operator import RightLeftUnaryPrefixOperator
from anoky.transducers.arrangements.segment import Segment
from anoky.transducers.arrangements.strings import Strings
from anoky.transducers.convert_preforms import ConvertPreforms
from anoky.transducers.top_down_tree_transducer import TopDownTreeTransducer

#from anoky.transducers.arrangements.Delimiters import BracketsWithHead



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
     ['.', '..', '...',
      '+', '-', '*', '/', '//', '%', '**', '@',
      '&', '^', '<<', '>>', '~',
      '=', ':=',
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
                                           Arrangement([Constituent(int, float)]))

    # comments, \, indentation, strings
    tt_primary = TopDownTreeTransducer("Primary",
                                       Arrangement([
                                           #Comment(),
                                           RawComment(),

                                           AssignmentSegment(),
                                           Segment(),
                                           
                                           ParenthesisWithHead(),
                                           ParenthesisNoHead(),
                                           
                                           #BracketsWithHead({'['}),
                                           
                                           Delimiters({'[','{'}),
                                           
                                           Strings({"'",'"'}, str), # "'''",'"""'}),

                                           LeftRightBinaryTokenCapturingOperator({'.'}),
                                           
                                           ]))

    
    
    
    tt_infix_special_ops = TopDownTreeTransducer("Infix Gather-Alls",
                             Arrangement([
                                MultipleAssignment({':='}),
                                ApplyInIsolation({'del', 'pass', 'break', 'continue', 'import', 'global', 'nonlocal', 'assert'}),
                                ApplyToRest({ 'return', 'raise', 'yield',}),]))

    tt_punctuation = TopDownTreeTransducer("Punctuation",
                                           Arrangement([Skip2Punctuation({'@[]', '@{}'}), ForPunctuation(), DefaultSeqPunctuation(), DefaultFormPunctuation()]))

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
                                                      '*', '@', '/', '%'})]))

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
                                               FormWithDirectives('if', {'elif', 'else'}),
                                               FormWithDirectives('try', {'except', 'else', 'finally'})]))
    

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
                                        tt_infix_special_ops,
                                        tt_punctuation,

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




















