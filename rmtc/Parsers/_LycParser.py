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

    [RT.ISOLATED_CONSTITUENT, ['', '', '', '', '',
               '', '', '', '', '', '', ''],],

    [RT.PUNCTUATION, [':', ';', ',',]],

    [RT.ISOLATED_CONSTITUENT, ["+o", ".", "", "" "", "", "~", "*", "", "", "", "&", '', "\\", "$", "/", "⫽", # 1st priority

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

    #region Transducers
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

                       Block(),
                       ParenthesisWithHead(), #head( args ) => (head args)
                       ParenthesisNoHead(),

                       ApplyParenthesis(),
                       # ArgSeqArrangement(),
                       Delimiters({'[', '⟦', '{', '⦃'}),
                       #Quote('‘'),
                       Strings(),
                       ]))

    # tt_block = TopDownTreeTransducer("Block", Arrangement([Block()]))

    tt_punctuation = TopDownTreeTransducer("Punctuation", Arrangement([DefaultPunctuation()]))

    tt_infix_special_ops = TopDownTreeTransducer("Infix Gather-Alls",
                             Arrangement([
                             #TRF_AssignmentStyleOperator(assignment_symbols),
    #                                            TFR_MarkSpecialOperator(':=', False),
                                TransformationArrow({'', '', '', '', ''}),
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
                            RightLeftBinaryOperator({'', '', '', ''})
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
                            IfElifElse()
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
                tokenizer := tokenizers⫽delimiter

            closing::
                “\”” “)” “⦆” “]” “⟧”
                “}” “⦄” “◁” “’” “⟩”

            macro ““”:
                tokenizer := tokenizers⫽delimited-symbol
                preserve-leading-whitespace

            macro “‘”:
                tokenizer := tokenizers⫽quote

            macro ““”:
                tokenizer := tokenizers⫽string
                preserve-leading-whitespace

            macro “#”:
                tokenizer := tokenizers⫽comment
                preserve-leading-whitespace

            macro “##”:
                tokenizer := tokenizers⫽raw-comment
                preserve-leading-whitespace

            macro “literate▷\n”:
                tokenizer := tokenizers⫽literate
                
            isolated-constituent::
                “” “” “” “” “” “”
                “” “” “” “” “” “”
                “.” “” ““ “” “” “~”
                “*” “” “” “” “&” ““, “\\”
                “$” “/” “⫽”
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

