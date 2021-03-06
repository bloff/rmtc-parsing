from typing import Union

from anoky.parsers.rmtc_parser import RMTCParser
from anoky.streams.character_stream import CharacterStream
from anoky.streams.indented_character_stream import IndentedCharacterStream
from anoky.tokenization.readtable import make_readtable, RT
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizers.delimited_identifier import DelimitedIdentifierTokenizer
from anoky.tokenization.tokenizers.delimiter import DelimiterTokenizer, SharpDelimiterTokenizer, SingleUseTokenizer
from anoky.tokenization.tokenizers.indentation_readtable import IndentationReadtableTokenizer
from anoky.tokenization.tokenizers.lispmode import LispModeTokenizer
from anoky.tokenization.tokenizers.meta_import import MetaImporter
from anoky.tokenization.tokenizers.raw_comment import RawCommentTokenizer
from anoky.tokenization.tokenizers.string import StringTokenizer, BlockStringTokenizer
from anoky.transducers.arrangement import Arrangement
from anoky.transducers.arrangements.apply_in_isolation import ApplyInIsolation
from anoky.transducers.arrangements.apply_to_rest import ApplyToRest
from anoky.transducers.arrangements.assignment_segment import AssignmentSegment
from anoky.transducers.arrangements.comments import RawComment
from anoky.transducers.arrangements.constituents import Constituent
from anoky.transducers.arrangements.default_punctuation import DefaultFormPunctuation, \
    DefaultSeqPunctuation, ForPunctuation, Skip2Punctuation
from anoky.transducers.arrangements.delimiters import ParenthesisWithHead, ParenthesisNoHead, \
    Delimiters, CodeQuote
from anoky.transducers.arrangements.if_else import InfixIfElse, FormWithDirectives
from anoky.transducers.arrangements.left_right_binary_operator import LeftRightBinaryOperator
from anoky.transducers.arrangements.left_right_binary_token_capturing_operator import LeftRightBinaryTokenCapturingOperator
from anoky.transducers.arrangements.left_right_nary_operator import LeftRightNaryOperator
from anoky.transducers.arrangements.left_right_nary_operator_multiple_heads import LeftRightNaryOperatorMultipleHeads
from anoky.transducers.arrangements.left_right_unary_prefix_nospace_operator import LeftRightUnaryPrefixNospaceOperator
from anoky.transducers.arrangements.lispmode import LispMode
from anoky.transducers.arrangements.multiple_assignment import MultipleAssignment
from anoky.transducers.arrangements.right_left_binary_operator import RightLeftBinaryOperator
from anoky.transducers.arrangements.right_left_unary_prefix_operator import RightLeftUnaryPrefixOperator
from anoky.transducers.arrangements.segment import Segment
from anoky.transducers.arrangements.strings import Strings
from anoky.transducers.bottom_up_tree_transducer import BottomUpTreeTransducer
from anoky.transducers.convert_preforms import ConvertPreforms
from anoky.transducers.top_down_tree_transducer import TopDownTreeTransducer

#from anoky.transducers.arrangements.Delimiters import BracketsWithHead



## READTABLE ##

default_readtable = make_readtable( [

    [RT.MACRO, ['(', '[', '{' ],
     {'tokenizer': 'DelimiterTokenizer'}],

    [RT.MACRO, '«',
     {'tokenizer':'DelimitedIdentifier'}],

    [RT.MACRO, '#(',
    {'tokenizer': 'LispModeTokenizer'}],

    [RT.MACRO, ['#meta-import', '#meta_import'],
        {'tokenizer': 'MetaImporter'}],

    
# """ strings

    [RT.MACRO, "'",
     {'tokenizer': 'SingleQuoteStringTokenizer'}],

    [RT.MACRO, '"',
     {'tokenizer': 'DoubleQuoteStringTokenizer'}],

    [RT.MACRO, ["`", "```"],
     {'tokenizer': 'CodeQuoteTokenizer'}],


    [RT.MACRO, "'''",
     {'tokenizer': 'TripleSingleQuoteStringTokenizer',
      'preserve-leading-whitespace': True}],

    [RT.MACRO, '"""',
     {'tokenizer': 'TripleDoubleQuoteStringTokenizer',
      'preserve-leading-whitespace': True}],

    

    
    [RT.MACRO, '#',
     {'tokenizer': 'CommentTokenizer',
      'preserve-leading-whitespace': True}],


    [RT.CLOSING, [')', ']', '}'], ],



    [RT.PUNCTUATION, [',', ':' ], ],
    # [RT.ISOLATED_CONSTITUENT, ','],

    

    [RT.ISOLATED_CONSTITUENT,
     ['.', '..', '...',
      '+', '/', '%', '*', '**', '@',
      '&', '^', '<<', '>>', '~',
      '=', ':=',
      '==', '!=', '<', '>', '<=', '>=',
      '+=', '-=', '*=', '/=', '%=',
      '**=', '@=', '|=', '^=', '&=', '<<=', '>>=',
      '->' ], ],

    [RT.ISOLATED_CONSTITUENT, '-',
     {"dont_isolate_infix": True}],

    

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

class AnokySharpDelimiterTokenizer(SharpDelimiterTokenizer):
    DELIMITER_PAIRS = { '#(' : ')',
                        '#[' : ']',
                        '#{' : '}'}


class AnokySingleQuoteStringTokenizer(StringTokenizer):
    MY_OPENING_DELIMITER = "'"
    MY_CLOSING_DELIMITER = "'"

class AnokyDoubleQuoteStringTokenizer(StringTokenizer):
    MY_OPENING_DELIMITER = '"'
    MY_CLOSING_DELIMITER = '"'


class AnokyTripleSingleQuoteStringTokenizer(BlockStringTokenizer):
    MY_OPENING_DELIMITER = "'''"
    MY_CLOSING_DELIMITER = "'''"
    MY_CLOSING_DELIMITER_LENGTH = 3


class AnokyTripleDoubleQuoteStringTokenizer(BlockStringTokenizer):
    MY_OPENING_DELIMITER = '"""'
    MY_CLOSING_DELIMITER = '"""'
    MY_CLOSING_DELIMITER_LENGTH = 3



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

                                           LispMode(),
                                           
                                           #BracketsWithHead({'['}),
                                           
                                           Delimiters({'[','{'}),

                                           CodeQuote({'`','```'}),
                                           
                                           Strings({"'",'"', "'''", '"""'}, str), # "'''",'"""'}),

                                           LeftRightBinaryTokenCapturingOperator({'.'}),
                                           
                                           ]))

    
    
    
    tt_infix_special_ops = TopDownTreeTransducer("Infix Gather-Alls",
                             Arrangement([
                                MultipleAssignment(),
                                ApplyInIsolation({'del', 'pass', 'break', 'continue', 'import', 'global', 'nonlocal', 'assert'}),
                                ApplyToRest({ 'return', 'raise', 'yield',}),]))

    tt_punctuation = TopDownTreeTransducer("Punctuation",
                                           Arrangement([Skip2Punctuation({'@[]', '@{}'}), ForPunctuation(), DefaultSeqPunctuation(), DefaultFormPunctuation()]))

    # tt_commaoperator = TopDownTreeTransducer("Comma as binary operator",
    #                                          Arrangement([RightLeftBinaryOperator({','})]))


    tt_unary_minus = TopDownTreeTransducer("Additive inverse",
                                        Arrangement([
                                            LeftRightUnaryPrefixNospaceOperator({'-'})]))

    tt_exponentiation = TopDownTreeTransducer("Exponentiation",
                                              Arrangement([
                                                  LeftRightBinaryOperator({'**'})]))

    tt_tilde = TopDownTreeTransducer("Bitwise NOT",
                    Arrangement([LeftRightUnaryPrefixNospaceOperator({'~'})]))


    tt_multiplication = TopDownTreeTransducer("Multiplication",
                                              Arrangement([
                                                  LeftRightBinaryOperator({
                                                      '*', '@', '/', '%'})]))

    tt_addition = TopDownTreeTransducer("Addition",
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



    # tt_join_isnt_notin = TopDownTreeTransducer("Comparisons, Membership/Identity Tests",
    #                                            Arrangement([
    #                                                     ]))
    tt_comparisons = TopDownTreeTransducer("Compare",
                                           Arrangement([
                                               LeftRightNaryOperatorMultipleHeads('compare',
                                                   {'==', '!=', '<', '>', '<=', '>=', 'in', 'notin', 'is', 'isnot'}),
                                               ]))


    

    tt_not = TopDownTreeTransducer("Not",
                                   Arrangement([RightLeftUnaryPrefixOperator({'not'})]))
    

    tt_and = TopDownTreeTransducer("And",
                                   Arrangement([LeftRightNaryOperator({'and'})]))

    tt_or = TopDownTreeTransducer("Or",
                                   Arrangement([LeftRightNaryOperator({'or'})]))



    



    tt_conditional = BottomUpTreeTransducer("Conditionals",
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



    tt_as = TopDownTreeTransducer("infix as",
                                  Arrangement([
                                      LeftRightBinaryOperator({'as'})]))




    default_python_transducer_chain = [ tt_constituent,
                                        tt_primary,
                                        tt_infix_special_ops,
                                        tt_punctuation,

                                        tt_unary_minus,
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
        RMTCParser.__init__(self, TokenizationContext("Anoky Tokenization Context"),
                            default_readtable,
                            IndentationReadtableTokenizer,
                            default_python_transducer_chain)
        self.tokenization_context.set(
            # ..
            DelimiterTokenizer = AnokyDelimiterTokenizer,
            SharpDelimiterTokenizer = AnokySharpDelimiterTokenizer,
            SingleQuoteStringTokenizer = AnokySingleQuoteStringTokenizer,
            DoubleQuoteStringTokenizer = AnokyDoubleQuoteStringTokenizer,
            TripleSingleQuoteStringTokenizer = AnokyTripleSingleQuoteStringTokenizer,
            TripleDoubleQuoteStringTokenizer = AnokyTripleDoubleQuoteStringTokenizer,
            CommentTokenizer = AnokyCommentTokenizer,
            LispModeTokenizer = LispModeTokenizer,
            CodeQuoteTokenizer = SingleUseTokenizer,
            DelimitedIdentifier = DelimitedIdentifierTokenizer,
            MetaImporter = MetaImporter
            )

        # For Anoky we do not make use of DelimitedIdentifiers or non-raw Comments.

        


    def _get_stream(self, code_or_stream:Union[str, CharacterStream]):
        stream = RMTCParser._get_stream(self, code_or_stream)
        if not isinstance(stream, IndentedCharacterStream):
            stream = IndentedCharacterStream(stream)
        return stream

