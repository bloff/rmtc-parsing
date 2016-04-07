from typing import Union

from anoky.Parsers.RMTCParser import RMTCParser
from anoky.Streams.CharacterStream import CharacterStream
from anoky.Streams.IndentedCharacterStream import IndentedCharacterStream
from anoky.Tokenization.Readtable import make_readtable, RT
from anoky.Tokenization.Tokenizers.RawComment import RawCommentTokenizer
from anoky.Tokenization.Tokenizers.Comment import CommentTokenizer
from anoky.Tokenization.Tokenizers.DelimitedIdentifierTokenizer import DelimitedIdentifierTokenizer
from anoky.Tokenization.Tokenizers.Delimiter import DelimiterTokenizer
from anoky.Tokenization.Tokenizers.IndentationReadtable import IndentationReadtableTokenizer
from anoky.Tokenization.Tokenizers.String import StringTokenizer
from anoky.Tokenization.TokenizationContext import TokenizationContext
from anoky.transducers.arrangements.apply_to_rest import ApplyToRest
from anoky.transducers.arrangement import Arrangement
from anoky.transducers.arrangements.left_right_binary_operator import LeftRightBinaryOperator
from anoky.transducers.top_down_tree_transducer import TopDownTreeTransducer
from anoky.transducers.convert_preforms import ConvertPreforms
from anoky.transducers.read_direction import ReadDirection
from anoky.transducers.arrangements.segment import Segment
from anoky.transducers.arrangements.comments import Comment, RawComment
from anoky.transducers.arrangements.constituents import Constituent
from anoky.transducers.arrangements.default_punctuation import DefaultPunctuation
from anoky.transducers.arrangements.delimiters import ParenthesisWithHead, ParenthesisNoHead, \
    ApplyParenthesis, Delimiters
from anoky.transducers.arrangements.if_else import InfixIfElse, FormWithDirectives
from anoky.transducers.arrangements.left_right_binary_operator_reversed_args import LeftRightBinaryOperatorReversedArgs
from anoky.transducers.arrangements.left_right_binary_operator_two_symbols import LeftRightBinaryOperatorTwoSymbols
from anoky.transducers.arrangements.left_right_binary_token_capturing_operator import LeftRightBinaryTokenCapturingOperator
from anoky.transducers.arrangements.left_right_nary_operator import LeftRightNaryOperator
from anoky.transducers.arrangements.left_right_unary_postfix_nospace_operator import LeftRightUnaryPostfixNospaceOperator
from anoky.transducers.arrangements.left_right_unary_prefix_nospace_token_capturing_operator import \
    LeftRightUnaryPrefixNospaceTokenCapturingOperator
from anoky.transducers.arrangements.right_left_binary_operator import RightLeftBinaryOperator
from anoky.transducers.arrangements.right_left_unary_prefix_nospace_operator import RightLeftUnaryPrefixNospaceOperator
from anoky.transducers.arrangements.right_left_unary_prefix_operator import RightLeftUnaryPrefixOperator
from anoky.transducers.arrangements.strings import Strings
from anoky.transducers.arrangements.transformation_arrow import TransformationArrow




#region Default lyc readtable

default_lyc_readtable = make_readtable([
    [RT.MACRO,
        ['(', '⦅', '[', '⟦', '{', '⦃', '‘', '⟨'],
        {'tokenizer': 'DelimiterTokenizer'}],

    [RT.CLOSING, ["”", ")", "⦆", "]", "⟧", "}", "⦄", "◁", "’", '⟩'],],

    [RT.MACRO, '«', {'tokenizer': 'DelimitedSymbolTokenizer', 'preserve-leading-whitespace': True}],

#    [RT.MACRO, '‘', {'tokenizer': 'Quote'}],

    [RT.MACRO, '“', {'tokenizer': 'StringTokenizer', 'preserve-leading-whitespace': True}],

    [RT.MACRO, '#', {'tokenizer': 'CommentTokenizer', 'preserve-leading-whitespace': True}],

    [RT.MACRO, '##', {'tokenizer': 'RawCommentTokenizer', 'preserve-leading-whitespace': True}],

    # [RT.MACRO, 'literate▷\n', {'tokenizer': 'Literate'}],

    [RT.ISOLATED_CONSTITUENT, ['<-', '', '', '', '',
               '->', '', '', '', '', '', ''],],

    [RT.PUNCTUATION, [':', ';', ',',]],

    [RT.ISOLATED_CONSTITUENT, ["+o", ".", "", "" "", "", "~", "*", "", "", "", "&", '', "\\", "$", "/", "//", # 1st priority

               "'", '', '!', '&', '\\@', '~@',
               '', '', '%',
               '', '',
               '<<', '>>',
               '<', '>', '≤', '≥', '∈', '∉',
               '=', '≠',
               '^',
               '|', '', # second | is meta-|
               '', # meta-&
               ':=', '+=', '-=', '×=', '÷=', '%=', '>>=', '<<=', '&=', '^=', '|=', '≤ₜ', 'and=', 'or=']],


    [RT.INVALID, ["\t"], {'error-message': "Tabs are not allowed as whitespace."}],

    [RT.WHITESPACE, ' '],
    [RT.NEWLINE, [chr(0x0A), chr(0x0D), chr(0x0A) + chr(0x0D), chr(0x0D) + chr(0x0A)],],

    ['DEFAULT',
        {'type': RT.CONSTITUENT}],
])
#endregion


#region lyc tokenizers
class LycDelimiterTokenizer(DelimiterTokenizer):
    DELIMITER_PAIRS = {
        '(' : ')',
        '⦅' : '⦆',
        '[' : ']',
        '⟦' : '⟧',
        '{' : '}',
        '⦃' : '⦄',
        '‘' : '’',
        '⟨' : '⟩',
        }

class LycStringTokenizer(StringTokenizer):
    """
    Reads “strings” with interpolated code.

    See `<https://bloff.github.io/lyc/2015/10/04/lexer-3.html>`_.
    """
    MY_OPENING_DELIMITER = '“'
    MY_CLOSING_DELIMITER = '”'

#endregion

#region Lyc Transducer Chain
default_lyc_transducer_chain = None

def define_default_lyc_transducer_chain():
    global default_lyc_transducer_chain

    #region transducers
    tt_constituent = \
        TopDownTreeTransducer("Constituent",
            Arrangement([Constituent()]))


    tt_primary = TopDownTreeTransducer("Primary",
                   Arrangement([
                       Comment(),
                       RawComment(),
                       LeftRightUnaryPrefixNospaceTokenCapturingOperator(
                           {'\\', '~', '$',
                            '', ''}),
                       # etc
                       LeftRightBinaryTokenCapturingOperator({'.', '/'}),
                       LeftRightUnaryPostfixNospaceOperator({'+o', '', '', '', '*', '', '', ''}),

                       Segment(),
                       ParenthesisWithHead(), #head( args ) => (head args)
                       ParenthesisNoHead(),

                       ApplyParenthesis(),
                       # ArgSeqArrangement(),
                       Delimiters({'[', '⟦', '{', '⦃'}),
                       #Quote('‘'),
                       #Strings(),
                       ]))

    # tt_block = TopDownTreeTransducer("Block", Arrangement([Block()]))

    tt_punctuation = TopDownTreeTransducer("Punctuation", Arrangement([DefaultPunctuation()]))

    tt_infix_special_ops = TopDownTreeTransducer("Infix Gather-Alls",
                             Arrangement([
                             #TRF_AssignmentStyleOperator(assignment_symbols),
    #                                            TFR_MarkSpecialOperator(':=', False),
                                TransformationArrow({'<-', '', '', '', ''}),
                                ApplyToRest({'return'}),]))


    tt_prefix = TopDownTreeTransducer("Prefix Operators",
                  Arrangement([
                        RightLeftUnaryPrefixNospaceOperator({"'", '', '!', '', '*', '&', '\\@', '~@' }),
                    # TFR_RightLeftUnaryPrefixOperator({'make'})
                    ], ReadDirection.RIGHT_TO_LEFT))

    tt_product = TopDownTreeTransducer("Product and Division",
                   Arrangement([
                       LeftRightNaryOperator({'', '', '%'})
                       ]))

    tt_addition = TopDownTreeTransducer("Addition and Subtraction",
                   Arrangement([
                       LeftRightNaryOperator({'', ''})
                       ]))

    tt_shift = TopDownTreeTransducer("Left and Right Shift",
                   Arrangement([
                       LeftRightNaryOperator({'<<', '>>'})
                       ]))
    #
    # tt_dots = TopDownTreeTransducer("Two-dots",
    #                 Arrangement([
    #                     LeftRightBinaryNospaceOperator({'‥'}),
    #                     LeftRightUnaryPostfixOperator({'‥'}),
    #                     ]))

    tt_casting = TopDownTreeTransducer("Casting",
                    Arrangement([
                        LeftRightBinaryOperator({'as', 'to', 'of', 'cast-as'})
                        ]))

    tt_arrow = TopDownTreeTransducer("Arrows",
                        Arrangement([
                            RightLeftBinaryOperator({'->', '', '', ''})
                        ], ReadDirection.RIGHT_TO_LEFT))

    tt_comparison = TopDownTreeTransducer("Comparisons",
                        Arrangement([
                            LeftRightNaryOperator({'<', '>', '≤', '≥'}),
                            LeftRightBinaryOperatorTwoSymbols({('not', 'in')}),
                            LeftRightBinaryOperator({'in', '∈', '∉'}),

                        ]))


    tt_equality = TopDownTreeTransducer("Equality",
                        Arrangement([
                            LeftRightNaryOperator({'=', '≠'})
                        ]))

    tt_bit_and = TopDownTreeTransducer("Bitwise AND",
                        Arrangement([
                            LeftRightNaryOperator({'&'})
                        ]))

    tt_bit_xor = TopDownTreeTransducer("Bitwise XOR",
                        Arrangement([
                            LeftRightNaryOperator({'^'})
                        ]))

    tt_bit_or = TopDownTreeTransducer("Bitwise OR",
                        Arrangement([
                            LeftRightNaryOperator({'|'})
                        ]))


    tt_prefix_not = TopDownTreeTransducer("Bitwise OR",
                        Arrangement([
                            RightLeftUnaryPrefixOperator({'not'})
                        ], ReadDirection.RIGHT_TO_LEFT))


    tt_bool_and = TopDownTreeTransducer("Boolean AND",
                        Arrangement([
                            LeftRightNaryOperator({'and'})
                        ]))

    tt_bool_or = TopDownTreeTransducer("Boolean OR",
                        Arrangement([
                            LeftRightNaryOperator({'or'})
                        ]))

    tt_if_else = TopDownTreeTransducer("If-Elif-Else and Infix If-Else",
                        Arrangement([
                            InfixIfElse({('if', 'else')}),
                            FormWithDirectives()
                        ]))

    tt_infix_for = TopDownTreeTransducer("Infix For",
                        Arrangement([
                            LeftRightBinaryOperatorReversedArgs({'for'})
                        ]))

    _assignment_symbols = {':=', '+=', '−=', '×=', '÷=', '%=', '>>=', '<<=', '&=', '^=', '|=', '≤_t', 'and=', 'or='}
    tt_assignments = TopDownTreeTransducer("Assignments",
                        Arrangement([
                            RightLeftBinaryOperator(_assignment_symbols)
                        ], ReadDirection.RIGHT_TO_LEFT))

    tt_meta_and = TopDownTreeTransducer("Meta AND",
                        Arrangement([
                            LeftRightNaryOperator({''}),
                        ]))

    tt_meta_or = TopDownTreeTransducer("Meta OR",
                        Arrangement([
                            LeftRightNaryOperator({''}),
                        ]))

    #endregion

    default_lyc_transducer_chain = [tt_constituent,
                                tt_primary,
                                # tt_block,
                                tt_infix_special_ops,
                                tt_prefix,
                                tt_punctuation,
                                tt_product,
                                tt_addition,
                                tt_shift,
                                # tt_dots,
                                tt_casting,
                                tt_arrow,
                                tt_comparison,
                                tt_equality,
                                tt_bit_and,
                                tt_bit_xor,
                                tt_bit_or,
                                tt_prefix_not,
                                tt_bool_and,
                                tt_bool_or,
                                tt_if_else,
                                tt_infix_for,
                                tt_assignments,
                                tt_meta_and,
                                tt_meta_or,
                                ConvertPreforms()
                               ]

define_default_lyc_transducer_chain()

#endregion




class LycParser(RMTCParser):
    r"""
    The parser for lyc. 
    
    ::
    
        readtable default-readtable:
            macro “(” “⦅” “[” “⟦” “{” “⦃” “‘” “⟨”:
                tokenizer := tokenizers//delimiter

            closing::
                “\”” “)” “⦆” “]” “⟧”
                “}” “⦄” “◁” “’” “⟩”

            macro ““”:
                tokenizer := tokenizers//delimited-symbol
                preserve-leading-whitespace

            macro “‘”:
                tokenizer := tokenizers//quote

            macro ““”:
                tokenizer := tokenizers//string
                preserve-leading-whitespace

            macro “#”:
                tokenizer := tokenizers//comment
                preserve-leading-whitespace

            macro “##”:
                tokenizer := tokenizers//raw-comment
                preserve-leading-whitespace

            macro “literate▷\n”:
                tokenizer := tokenizers//literate
                
            isolated-constituent::
                “<-” “” “” “” “” “->”
                “” “” “” “” “” “”
                “.” “” ““ “” “” “~”
                “*” “” “” “” “&” ““, “\\”
                “$” “/” “//”
                ““” “” “!” “&” “\\@” “~@”
                “” “” “%”
                “” “”
                “<<” “>>”
                “<” “>” “≤” “≥” “∈” “∉”
                “=” “≠”
                “^”
                “|” “” # second | is meta-|
                “”     # meta-&
                “:=” “+=” “-=” “×=” “÷=” “%=” “>>=”
                “<<=” “&=” “^=” “|=” “≤ₜ” “and=” “or=“

            punctuation:: “:” “;” “,”

            invalid “\t”:
                error-message := “Tabs are not allowed as whitespace.”

            whitespace “ ”

            newline “\n”

            default-properties:
                type := 'constituent

        transducer-chain default-transducer-chain:
            primary:
                «Comment»
                «Raw Comment»
                «Left-Right Unary Prefix No-space Operator» “\\”
                «Left-Right Unary Prefix No-space Operator» “~”
                «Left-Right Unary Prefix No-space Operator» “$”
                «Left-Right Unary Prefix No-space Operator» “”
                «Left-Right Unary Prefix No-space Operator» “”
                
                etc
    """

    def __init__(self):
        RMTCParser.__init__(self, TokenizationContext("Lyc Tokenization Context"),
                            default_lyc_readtable,
                            IndentationReadtableTokenizer,
                            default_lyc_transducer_chain)
        self.tokenization_context.set(
            # Tokenizer classes
            DelimiterTokenizer = LycDelimiterTokenizer,
            StringTokenizer = LycStringTokenizer,
            DelimitedSymbolTokenizer = DelimitedIdentifierTokenizer,
            CommentTokenizer = CommentTokenizer,
            RawCommentTokenizer = RawCommentTokenizer,
            )


    def _get_stream(self, code_or_stream:Union[str, CharacterStream]):
        stream = RMTCParser._get_stream(self, code_or_stream)
        if not isinstance(stream, IndentedCharacterStream):
            stream = IndentedCharacterStream(stream)
        return stream

