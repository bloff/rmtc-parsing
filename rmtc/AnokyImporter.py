
import ast
import importlib
import importlib.abc as iabc
import importlib.machinery as imach
import os
import sys

#from importlib import _bootstrap._call_with_frames_removed
#from importlib._bootstrap_external import _validate_bytecode_header, _code_to_bytecode, _compile_bytecode
from importlib.util import cache_from_source

from rmtc.Common.Record import Record
import rmtc.Common.Options as Options
import compiler_anoky as akycomp






class AnokyLoader(iabc.SourceLoader):


    def path_stats(self, path):
        s = os.stat(path)
        return {'mtime':s.st_mtime, 'size':s.st_size}

    def get_data(self, path):
        #raise NotImplementedError()
        with open(path, "rb") as f:
            bdata = f.read()

        return bdata


    def get_filename(self, fullname):

        fullpath = os.getcwd() + os.sep + fullname + ".aky"
        return fullpath



    def source_to_code(self, data, path, *, _optimize=-1):
        """Return the code object compiled from source.

        The 'data' argument can be any object type that compile() supports.
        """

        options = Record({'filename': path,
                          'verbose': False,
                          'execute': False},)

        aky_ast = akycomp.generate(options)

        ast.fix_missing_locations(aky_ast)


        # return _bootstrap._call_with_frames_removed(compile, data, path, 'exec',
        #                                 dont_inherit=True, optimize=_optimize)
        return super().source_to_code(aky_ast, path)






class AnokyFinder(iabc.MetaPathFinder):


    def find_spec(self, fullname, path, target=None):

        if path is not None:
            raise NotImplementedError()

        cwd = os.getcwd()
        filename = fullname + ".aky"
        fullpath = cwd + os.sep + filename

        if os.path.isfile(filename):

            #pycpath = cache_from_source(fullpath)

            spec = imach.ModuleSpec(
                #name
                name=fullname,
                #loader
                loader=AnokyLoader(),
                origin=fullpath,
                #__cached__=pycpath,
                # etc.
            )

            return spec

        return None


sys.meta_path.append(AnokyFinder())

print(sys.meta_path)


import pyctest

















##=================================================

# def decode_source(source_bytes):
#     """Decode bytes representing source code and return the string.
#
#     Universal newline support is used in the decoding.
#     """
#     import tokenize  # To avoid bootstrap issues.
#     source_bytes_readline = _io.BytesIO(source_bytes).readline
#     encoding = tokenize.detect_encoding(source_bytes_readline)
#     newline_decoder = _io.IncrementalNewlineDecoder(None, True)
#     return newline_decoder.decode(source_bytes.decode(encoding[0]))