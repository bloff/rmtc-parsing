from Common.StringStuff import indent_string
from Transducers.Arrangements.ApplyToRest import ApplyToRest
from Transducers.Arrangements.Arrangement import Arrangement
from Transducers.Arrangements.LeftRightBinaryOperator import LeftRightBinaryOperator
from Transducers.TopDownTreeTransducer import TopDownTreeTransducer
from .ConvertPreForms import ConvertPreforms
from .ReadDirection import ReadDirection
from Common import Options
from Syntax.__exports__ import Node, indented_lisp_printer
from Transducers.Arrangements.Block import Block
from Transducers.Arrangements.Comments import Comment, RawComment
from Transducers.Arrangements.Constituents import Constituent
from Transducers.Arrangements.DefaultPunctuation import DefaultPunctuation
from Transducers.Arrangements.Delimiters import ParenthesisWithHead, ParenthesisNoHead, \
    ApplyParenthesis, Delimiters
from Transducers.Arrangements.IfElse import InfixIfElse, IfElifElse
from Transducers.Arrangements.LeftRightBinaryOperatorReversedArgs import LeftRightBinaryOperatorReversedArgs
from Transducers.Arrangements.LeftRightBinaryOperatorTwoSymbols import LeftRightBinaryOperatorTwoSymbols
from Transducers.Arrangements.LeftRightBinaryTokenCapturingOperator import LeftRightBinaryTokenCapturingOperator
from Transducers.Arrangements.LeftRightNaryOperator import LeftRightNaryOperator
from Transducers.Arrangements.LeftRightUnaryPostfixNospaceOperator import LeftRightUnaryPostfixNospaceOperator
from Transducers.Arrangements.LeftRightUnaryPrefixNospaceTokenCapturingOperator import \
    LeftRightUnaryPrefixNospaceTokenCapturingOperator
from Transducers.Arrangements.RightLeftBinaryOperator import RightLeftBinaryOperator
from Transducers.Arrangements.RightLeftUnaryPrefixNospaceOperator import RightLeftUnaryPrefixNospaceOperator
from Transducers.Arrangements.RightLeftUnaryPrefixOperator import RightLeftUnaryPrefixOperator
from Transducers.Arrangements.Strings import Strings
from Transducers.Arrangements.TransformationArrow import TransformationArrow


tt_constituent = TopDownTreeTransducer("Constituent", Arrangement([Constituent()]))


tt_primary = TopDownTreeTransducer("Primary",
               Arrangement([
                   Comment(),
                   RawComment(),
                   LeftRightUnaryPrefixNospaceTokenCapturingOperator({'\\', '~', '$', '', ''}),
                   LeftRightBinaryTokenCapturingOperator({'.', '/'}),
                   LeftRightUnaryPostfixNospaceOperator({'', '', '', '', '', ''}),

                   Block(),
                   ParenthesisWithHead(),
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

default_transducer_chain = [tt_constituent,
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


def apply_transducer_chain(transducer_chain, form):
    """
    :type transducer_chain: list(TopDownTreeTransducer)
    :type form: Code
    """
    for tt in transducer_chain:
        if isinstance(form, Node) and len(form) > 0:
            tt.transduce(form)
            if Options.PRINT_TREE_TRANSDUCER_OUTPUTS is True:
                if Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST is None or tt.name in Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST:
                    print(indent_string("After transducer: " + tt.name + "\n" +indented_lisp_printer(form), 4))