import sys

import msgpack

from Common.Errors import LycError, TokenizingError
from Common.SysArgsParser import SysArgsParser
from Parsers.LycParser import LycParser
from Streams.FileStream import FileStream
from Streams.StringStream import StringStream
from Syntax.Token import TOKEN
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

        parser = LycParser()

        if 'output' in options:
            output = options.output
            encoder = options.encoder
            filler_token_value = TOKEN.WHITESPACE.value if options.binary else TOKEN.WHITESPACE.name
            for token, first_index, index_after in parser.tokenize_with_intervals(stream):
                if token is None:
                    bytes_ = encoder((filler_token_value, first_index, index_after))
                else:
                    token_value = token.type.value if options.binary else token.type.name
                    bytes_ = encoder((token_value, first_index, index_after))
                output.write(bytes_)
        else:
            for token in parser.tokenize(stream):
                print(str(token))

    except LycError as e:
        print(e.trace)

def main():
    options = parse_args(sys.argv)

    tokenize(options)



if __name__ == "__main__":
    main()
