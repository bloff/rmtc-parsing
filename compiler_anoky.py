import sys

import ast

import msgpack
from rmtc.Common.Errors import ErrorInPosition

from rmtc.Common.Record import Record
from rmtc.Common.SysArgsParser import SysArgsParser
#from rmtc.Parsers.LycParser import LycParser
from rmtc.Expansion.Expander import DefaultExpander
from rmtc.Generation.Generator import DefaultGenerator
from rmtc.Parsers.AnokyParser import AnokyParser
from rmtc.Streams.FileStream import FileStream
from rmtc.Syntax.LispPrinter import indented_lisp_printer
import rmtc.Common.Options as Options

import astpp

from importlib.util import MAGIC_NUMBER
import marshal
from os import listdir, stat
from os.path import isfile
#from time import gmtime
#from calendar import timegm
from struct import pack, unpack
#from sys import getsizeof

from importlib.util import cache_from_source, source_from_cache

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



def generate(options):
    parser = AnokyParser()
    try:
        if "filename" not in options:
            print("No filename specified.")
            return
        filename = options.filename

        stream = FileStream(filename)

        file_node = parser.parse(stream)
        print(indented_lisp_printer(file_node))

        expander = DefaultExpander()
        ec = expander.expand_unit(file_node)
        print("\n〰〰〰〰〰〰 After macro expansion 〰〰〰〰〰〰")
        print(indented_lisp_printer(file_node))

        generator = DefaultGenerator()
        py_module = generator.generate_unit(file_node,
        # provide expansion context to generation context
                                            EC=ec)

        print("\n〰〰〰〰〰〰 Generated Python code 〰〰〰〰〰〰\n")
        astpp.parseprint(py_module)

        print("\n〰〰〰〰〰〰 Python retrosource 〰〰〰〰〰〰\n")
        print(ASTFormatter().format(py_module))


        return py_module



    except ErrorInPosition as e:
        print(e.trace)



def check_for_apyc(filename):

    apyc_filename = cache_from_source(filename)

    if isfile(apyc_filename):

        with open(apyc_filename, "rb") as pyc:
            pycmagic = pyc.read(4)
            pycmodtime = unpack('=L', pyc.read(4))[0]
            pycsrcsize = unpack('=L', pyc.read(4))[0]

        srcstats = stat(filename)

        # check magic number?

        print(int(srcstats.st_mtime), pycmodtime, srcstats.st_size, pycsrcsize, sep="\n")


        return int(srcstats.st_mtime) == pycmodtime \
            and srcstats.st_size == pycsrcsize


    return False


def load_from_apyc(filename):

    apyc_filename = cache_from_source(filename)

    with open(apyc_filename, "rb") as pyc:
        pycmagic = pyc.read(4)
        pycmodtime = unpack('=L', pyc.read(4))[0]
        pycsrcsize = unpack('=L', pyc.read(4))[0]

        codeobj = marshal.load(pyc)

    return codeobj


def write_apyc(filename, codeobj):

    apyc_filename = cache_from_source(filename)

    srcstats = stat(filename)

    with open(apyc_filename, "wb") as pyc:

        pyc.write(MAGIC_NUMBER)

        # write last mod time
        srcmtime = int(srcstats.st_mtime)
        bsrcmtime = pack('=L', srcmtime)
        pyc.write(bsrcmtime)

        # write size
        srcsize = srcstats.st_size
        bsrcsize = pack('=L', srcsize)
        pyc.write(bsrcsize)

        # write bytecode
        marshal.dump(codeobj, pyc)




def main():
    options = parse_args(sys.argv)

    filename = options.filename
    apyc_exists = check_for_apyc(filename)

    if apyc_exists:

        codeobj = load_from_apyc(filename)
        print("loaded code object from pyc")

    else:

        py_module = generate(options)

        ast.fix_missing_locations(py_module)

        codeobj = compile(py_module,
                          filename=filename,
                          mode="exec")

        print("compiled code object from source")

    if options.execute:
        exec(codeobj)

    if not apyc_exists:
        write_apyc(filename, codeobj)



if __name__ == "__main__":
    main()
