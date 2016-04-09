import sys

import ast

import msgpack
from anoky.common.errors import CompilerError

from anoky.common.record import Record
from anoky.common.old_args_parser import SysArgsParser
#from anoky.parsers.LycParser import LycParser
from anoky.expansion.expander import DefaultExpander
from anoky.generation.generator import DefaultGenerator
from anoky.parsers.anoky_parser import AnokyParser
from anoky.streams.file_stream import FileStream
from anoky.syntax.lisp_printer import indented_lisp_printer
import anoky.common.options as Options

import astpp

from astformatter import ASTFormatter

def unicode_encoder(obj):
    return (str(obj)+"\n").encode()

def parse_args(argv):
    options = Record({'verbose': False,
                      'execute': False},)
    args = SysArgsParser(argv)
    while args.next() is not None:
        arg = args()
        if arg == '--verbose':
            options.verbose = True
            Options.PRINT_TREE_TRANSDUCER_OUTPUTS = True
            Options.PRINT_ARRANGEMENT_OUTPUTS = True
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
        elif arg.lower().endswith('.aky'):
            if 'filename' in options:
                print("Multiple filenames found!")
                exit(-1)
            options['filename'] = arg

        elif arg == '--execute':
            options.execute = True

        else:
            print("Unexpected option, '%s'" % arg)
            exit(-1)
    return options



def expand(options):
    parser = AnokyParser()
    try:
        if "filename" not in options:
            print("No filename specified.")
            return
        filename = options.filename

        stream = FileStream(filename)

        file_node = parser.parse(stream)
        # print(indented_lisp_printer(file_node))

        expander = DefaultExpander()
        ec = expander.expand_unit(file_node)
        # print("\n〰〰〰〰〰〰 After macro expansion 〰〰〰〰〰〰")
        # print(indented_lisp_printer(file_node))

        generator = DefaultGenerator()
        py_module = generator.generate_unit(file_node,
        # provide expansion context to generation context
                                            EC=ec)

        # print("\n〰〰〰〰〰〰 Generated Python code 〰〰〰〰〰〰\n")
        # astpp.parseprint(py_module)

        # print("\n〰〰〰〰〰〰 Python retrosource 〰〰〰〰〰〰\n")
        print(ASTFormatter().format(py_module))

        if options.execute:

            ast.fix_missing_locations(py_module)

            compiled_module = compile(py_module,
                                      filename="<ast>",
                                      mode="exec")

            exec(compiled_module)




    except CompilerError as e:
        print(e.trace)




def main():
    options = parse_args(sys.argv)


    expand(options)

#    node = Form(Identifier("bla bla"), Identifier("arg"))
#    print(lisp_printer(node))



if __name__ == "__main__":
    main()
