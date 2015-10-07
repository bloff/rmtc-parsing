from Tokenization.Readtable import *

standard_readtable = make_read_table([
    [RT_MACRO,
        ['(', '⦅', '[', '⟦', '{', '⦃', '‘', '⟨'],
        {'tokenizer': 'Delimiter'}],

    [RT_CLOSING, ["”", ")", "⦆", "]", "⟧", "}", "⦄", "◁", "’", '⟩'],],
        # {'error-message': "Closing delimiter without corresponding opening delimiter."}],
    
    [RT_MACRO, '«', {'tokenizer': 'Delimited Symbol', 'preserve-leading-whitespace': True}],

#    [RT_MACRO, '‘', {'tokenizer': 'Quote'}],

    [RT_MACRO, '“', {'tokenizer': 'String', 'preserve-leading-whitespace': True}],

    [RT_MACRO, '#', {'tokenizer': 'Comment', 'preserve-leading-whitespace': True}],

    [RT_MACRO, '##', {'tokenizer': 'Raw Comment', 'preserve-leading-whitespace': True}],

    # [RT_MACRO, '“', {'tokenizer': 'Quote'}],
    
    # [RT_MACRO, 'literate▷\n', {'tokenizer': 'Literate'}],

    [RT_TOKEN, ['', '', '', '', '',
               '', '', '', '', '', '', ''],],
        # {'width': 2}],

    [RT_PUNCTUATION, [':', ';', ',',]],

    [RT_TOKEN, [".", "", "" "", "", "~", "*", "", "", "", "&", '', "\\", "$", "/", "⫽", # 1st priority

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


    [RT_INVALID, ["\t"], {'error-message': "Tabs are not allowed as whitespace."}],

    [RT_WHITESPACE, ' '],
    [RT_NEWLINE, [chr(0x0A), chr(0x0D), chr(0x0A) + chr(0x0D), chr(0x0D) + chr(0x0A)],],

    ['DEFAULT',
        {'type': RT_CONSTITUENT}],
])
