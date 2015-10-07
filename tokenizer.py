import sys

import msgpack

from Common.Errors import LycError, TokenizingError
from Common.SysArgsParser import SysArgsParser
from Streams.FileStream import FileStream
from Streams.StringStream import StringStream
from Syntax.Token import TOKEN
from Tokenization.Tokenizers.Standard import StandardTokenizer
from Tokenization.StandardReadtable import standard_readtable, RT_CLOSING
from Common.Record import Record


def unicode_encoder(obj):
    return (str(obj)+"\n").encode()

def parse_args(argv):
    options = Record({'verbose': False})
    args = SysArgsParser(argv)
    while args.next() is not None:
        arg = args()
        if arg == '--verbose':
            options.verbose = True
        elif arg == '--binary':
            options.binary = True
            options.encoder = msgpack.packb
        elif arg == '--lex':
            if 'encoder' not in options:
                options.binary = False
                options.encoder = unicode_encoder
            if args.peek() is None or args.peek().startswith("--"):
                options.output = sys.stdout.buffer
            else:
                output_name = args.next()
                if output_name == 'stdout': options.output = sys.stdout.buffer
                if output_name == 'stderr': options.output = sys.stderr.buffer
                else: options.output = open(output_name, "wb")
        elif arg.lower().endswith('.ly'):
            if 'filename' in options:
                print("Multiple filenames found!")
                exit(-1)
            options['filename'] = arg
        else:
            print("Unexpected option, '%s'" % arg)
            exit(-1)
    return options



def tokenize(options):
    try:
        filename = options.filename


        code = open(filename, encoding='utf-8').read()
        stream = StringStream(code)

        tokenizer = StandardTokenizer(stream)


        if 'output' in options:
            output = options.output
            encoder = options.encoder
            current_index = 0
            for token in tokenizer.run():
                token_first = token.range.first_position.index
                token_after = token.range.position_after.index
                if token_first > current_index:
                    token_type = TOKEN.WHITESPACE.value if options.binary else TOKEN.WHITESPACE.name
                    bytes_ = encoder((token_type, current_index, token_first))
                    output.write(bytes_)
                    current_index = token_first
                elif token_first < current_index:
                    raise TokenizingError(token_first, "Overlapping tokens (%s, %s)!!!" % (current_index, token_first))
                token_type = token.type.value if options.binary else token.type.name
                bytes_ = encoder((token_type, current_index, token_after))
                print([token_type, current_index, token_after])
                current_index = token_after
                output.write(bytes_)
        else:
            for token in tokenizer.run():
                print(str(token))

        if not stream.next_is_EOF():
            seq, properties = standard_readtable.probe(stream)
            if properties.type == RT_CLOSING:
                raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Uncaptured closing sequence “%s”." % seq)
            raise TokenizingError(stream.absolute_position_of_unread_seq(seq), "Failed to Tokenize all of the text!")
    except LycError as e:
        print(e.trace)

def main():
    options = parse_args(sys.argv)

    tokenize(options)



if __name__ == "__main__":
    main()
