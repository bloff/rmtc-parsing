import rmtc.AnokyImporter as __akyimp__
import rmtc.Module as __aky__
__macros__ = {}
__id_macros__ = {}
__special_forms__ = {}
from astformatter import ASTFormatter
from rmtc.Common.Globals import G
from rmtc.Common.Record import Record
from rmtc.Expansion.Expander import DefaultExpander
from rmtc.Generation.Generator import DefaultGenerator
from rmtc.Parsers.AnokyParser import AnokyParser
from rmtc.Streams.FileStream import FileStream
from rmtc.Syntax.LispPrinter import indented_lisp_printer
from rmtc.Common.Errors import CompilerError
import argparse
import ast
import astpp
def compile_anoky(options):
    parser = AnokyParser()
    try:
        filename = options.filename
        stream = FileStream(filename)
        node_with_tokens = parser.tokenize_into_node(stream)
        if options.print_tokens:
            print('\n——›–  Tokenized source  –‹——\n')
            for token in node_with_tokens:
                print(str(token))
        if not options.arrange:
            return()
        file_node = parser.transduce(node_with_tokens)
        if options.print_parse:
            print('\n——›–  Parsed source before macro expansion  –‹——\n')
            print(indented_lisp_printer(file_node))
        expander = DefaultExpander()
        ec = expander.expand_unit(file_node)
        if options.print_macro_expanded_code:
            print('\n——›–  Parsed source macro expansion  –‹——\n')
            print(indented_lisp_printer(file_node))
        generator = DefaultGenerator()
        py_module = generator.generate_unit(file_node, EC=ec)
        if options.print_python_ast:
            print('\n——›–  Generated Python AST  –‹——\n')
            astpp.parseprint(py_module)
        if options.print_python_code:
            try:
                python_source = ASTFormatter().format(py_module)
            except Exception:
                print('\nFailed to generate Python Source Code!!!\n')
            else:
                print('\n——›–  Generated Python Source Code  –‹——\n')
                print(python_source)
        if options.execute:
            ast.fix_missing_locations(py_module)
            compiled_module = compile(py_module, filename='<ast>', mode='exec')
            exec(compiled_module)
    except CompilerError as e:
        print(e.trace)
def main():
    parser = argparse.ArgumentParser(prefix_chars='-')
    parser.add_argument('--print-tokens', action='store_true')
    parser.add_argument('--print-tree-transducer-outputs', action='store_true')
    parser.add_argument('--print-arrangement-outputs', action='store_true')
    parser.add_argument('--print-parse', action='store_true')
    parser.add_argument('--print-macro-expanded-code', action='store_true')
    parser.add_argument('--print-python-ast', action='store_true')
    parser.add_argument('--print-python-code', action='store_true')
    parser.add_argument('--skip-arrangement', action='store_true')
    parser.add_argument('--skip-macroexpansion', action='store_true')
    parser.add_argument('--skip-codegen', action='store_true')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('-I', '--include')
    parser.add_argument('-E', '--execute', action='store_true')
    parser.add_argument('--version', action='version', version='Anoky α.1')
    parser.add_argument('file', nargs='+')
    parse = parser.parse_args()
    options = Record()
    options.print_tokens = parse.print_tokens
    if parse.print_tree_transducer_outputs:
        G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS = True
    if parse.print_arrangement_outputs:
        G.Options.PRINT_ARRANGEMENT_OUTPUTS = True
    options.print_parse = parse.print_parse
    options.print_macro_expanded_code = parse.print_macro_expanded_code
    options.include_dirs = parse.include.split(':') if parse.include else ['.']
    if len(parse.file) > 1:
        raise NotImplementedError()
    options.filename = parse.file[0]
    options.arrange = not parse.skip_arrangement
    if not options.arrange:
        options.print_tokens = True
    options.macroexpand = not parse.skip_macroexpansion and not parse.skip_arrangement
    options.codegen = not parse.skip_macroexpansion and not parse.skip_arrangement and not parse.skip_codegen
    options.print_python_code = parse.print_python_code
    options.print_python_ast = parse.print_python_ast
    options.execute = parse.execute
    if parse.stdout:
        options.output = '<stdout>'
    else:
        options.output = '.'
    compile_anoky(options)
if __name__ == '__main__':
    main()
