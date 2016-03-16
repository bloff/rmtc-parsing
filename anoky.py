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
import rmtc.Common.Options as Options


def compile_anoky(options):
    parser = AnokyParser()
    try:
        filename = options.filename
        stream = FileStream(filename)
        if not options.arrange:
            raise NotImplementedError()
        file_node = parser.parse(stream)
        print(indented_lisp_printer(file_node))
        expander = DefaultExpander()
        ec = expander.expand_unit(file_node)
        print('\n〰〰〰〰〰〰 After macro expansion 〰〰〰〰〰〰')
        print(indented_lisp_printer(file_node))
        generator = DefaultGenerator()
        py_module = generator.generate_unit(file_node, EC=ec)
        print('\n〰〰〰〰〰〰 Generated Python code 〰〰〰〰〰〰\n')
        astpp.parseprint(py_module)
        print('\n〰〰〰〰〰〰 Python retrosource 〰〰〰〰〰〰\n')
        print(ASTFormatter().format(py_module))
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
    parser.add_argument('--print-semantic-analysis-history', action='store_true')
    parser.add_argument('--print-code-generation-history', action='store_true')
    parser.add_argument('--skip-arrangement', action='store_true')
    parser.add_argument('--skip-macroexpansion', action='store_true')
    parser.add_argument('--skip-codegen', action='store_true')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('-I', '--include')
    parser.add_argument('--version', action='version', version='⚑ bootstrap α.1')
    parser.add_argument('file', nargs='+')
    parse = parser.parse_args()
    if parse.print_tokens:
        G.Options.PRINT_TOKENS = True
    if parse.print_tree_transducer_outputs:
        G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS = True
    if parse.print_arrangement_outputs:
        G.Options.PRINT_ARRANGEMENT_OUTPUTS = True
    options = Record()
    options.print_sa_history = parse.print_semantic_analysis_history
    options.print_cg_history = parse.print_code_generation_history
    options.include_dirs = parse.include.split(':') if parse.include else ['.']
    if len(parse.file) > 1:
        raise NotImplementedError()
    options.filename = parse.file[0]
    options.arrange = not parse.skip_arrangement
    options.macroexpand = not parse.skip_macroexpansion and not parse.skip_arrangement
    options.codegen = not parse.skip_macroexpansion and not parse.skip_arrangement and not parse.skip_codegen
    if parse.stdout:
        options.output = '<stdout>'
    else:
        options.output = '.'
    compile_anoky(options)
if __name__ == '__main__':
    main()
