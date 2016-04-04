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
from rmtc.Streams.StringStream import StringStream
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import prompt
import argparse
import ast
import astpp
import sys
import traceback
parser = AnokyParser()
code_generator = DefaultGenerator()
code_expander = DefaultExpander()
def anoky_tokenize(stream,options):
    tokenized_node = parser.tokenize_into_node(stream)
    if options.print_tokens:
        print('\n——›–  Tokenized source  –‹——', end='')
        for token in tokenized_node:
            print(str(token))
    return tokenized_node
def anoky_transduce(node,options):
    parser.transduce(node)
    if options.print_parse:
        print('\n——›–  Parsed source before macro expansion  –‹——', end='')
        print(indented_lisp_printer(node))
def anoky_expand(parsed_node,options):
    code_expander.expand_unit(parsed_node)
    if options.print_macro_expanded_code:
        print('\n——›–  Parsed source after macro expansion  –‹——', end='')
        print(indented_lisp_printer(parsed_node))
def anoky_generate(parsed_node,options,CG):
    py_ast = code_generator.generate_elements(parsed_node, CG)
    if options.print_python_ast:
        print('\n——›–  Generated Python AST  –‹——')
        astpp.parseprint(ast.Module(body=py_ast))
    if options.print_python_code:
        try:
            python_source = ASTFormatter().format(ast.Module(body=py_ast))
        except Exception:
            print('\n!–›–  Failed to generate Python Source Code!  –‹–!')
            traceback.print_exc()
        else:
            print('\n——›–  Generated Python Source Code  –‹——')
            print(python_source)
    return py_ast
def interactive_anoky(options):
    (CG, init_code) = code_generator.begin(interactive=True)
    interactive_history = InMemoryHistory()
    try:
        while True:
            written_code = prompt('>>> ', history=interactive_history, multiline=True)
            stream = StringStream(written_code, '<interactive>')
            node = anoky_tokenize(stream, options)
            if not options.arrange:
                continue
            anoky_transduce(node, options)
            anoky_expand(node, options)
            py_ast = anoky_generate(node, options, CG)
            py_ast = code_generator.end(py_ast, CG)
            ast.fix_missing_locations(py_ast)
            compiled_ast = compile(py_ast, filename='<ast>', mode='single')
            if options.execute:
                try:
                    exec(compiled_ast)
                except Exception as e:
                    traceback.print_exc()
    except EOFError:
        return
    except KeyboardInterrupt:
        return
def non_interactive_anoky(options):
    (CG, init_code) = code_generator.begin(interactive=False)
    try:
        filename = options.filename
        stream = FileStream(filename)
        node = anoky_tokenize(stream, options)
        if not options.arrange:
            return
        anoky_transduce(node, options)
        anoky_expand(node, options)
        py_ast = anoky_generate(node, options, CG)
        py_ast = code_generator.end(py_ast, CG)
    except CompilerError as e:
        print(e.trace)
    if options.execute:
        ast.fix_missing_locations(py_ast)
        compiled_module = compile(py_ast, filename='<ast>', mode='exec')
        exec(compiled_module)
def main():
    parser = argparse.ArgumentParser(prefix_chars='-')
    parser.add_argument('--print-tokens', action='store_true', help='Prints the tokenizer output.')
    parser.add_argument('--print-tree-transducer-outputs', action='store_true', help='Prints the output of each transducer in the chain.')
    parser.add_argument('--print-arrangement-outputs', action='store_true', help='Prints the output of each arrangement within each arrangement-based transducer in the chain.')
    parser.add_argument('--print-parse', action='store_true', help='Prints the outcome of parsing the written code (the forms, seqs, etc).')
    parser.add_argument('--print-macro-expanded-code', action='store_true', help='Prints the code after macro-expansion.')
    parser.add_argument('--print-python-ast', action='store_true', help='Prints the generated Python AST.')
    parser.add_argument('--print-python-code', action='store_true', help='Prints the generated Python source.')
    parser.add_argument('--skip-arrangement', action='store_true', help='Stops the compiler immediately after tokenization.')
    parser.add_argument('--skip-macroexpansion', action='store_true', help='Stops the compiler immediately after parsing.')
    parser.add_argument('--skip-codegen', action='store_true', help='Stops the compiler immediately after macro-expansion.')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('-I', '--include', help='A colon-separated list of source paths where to search for imported modules.')
    parser.add_argument('-E', '--exec', action='store_true', help='Executes the compiled code.')
    parser.add_argument('--version', action='version', version='Anoky α.1')
    parser.add_argument('file', nargs='*')
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
    elif len(parse.file) == 0:
        options.interactive = True
    else:
        options.interactive = False
        options.filename = parse.file[0]
    options.arrange = not parse.skip_arrangement
    if not options.arrange:
        options.print_tokens = True
    options.macroexpand = not parse.skip_macroexpansion and not parse.skip_arrangement
    options.codegen = not parse.skip_macroexpansion and not parse.skip_arrangement and not parse.skip_codegen
    options.print_python_code = parse.print_python_code
    options.print_python_ast = parse.print_python_ast
    options.execute = parse.exec
    if parse.stdout:
        options.output = '<stdout>'
    else:
        options.output = '.'
    if options.interactive:
        interactive_anoky(options)
    else:
        non_interactive_anoky(options)
if __name__ == '__main__':
    main()
