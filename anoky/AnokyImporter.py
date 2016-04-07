
import ast
import importlib
import importlib.abc as iabc
import importlib.machinery as imach
import os
import sys

#from importlib import _bootstrap._call_with_frames_removed
#from importlib._bootstrap_external import _validate_bytecode_header, _code_to_bytecode, _compile_bytecode
from importlib.util import cache_from_source

from anoky.common.record import Record
import anoky.common.options as Options
import compiler_anoky as akycomp



class AnokyLoader(iabc.SourceLoader):


    def path_stats(self, path):
        s = os.stat(path)
        return {'mtime':s.st_mtime, 'size':s.st_size}

    def get_data(self, path):
        #raise NotImplementedError()
        with open(path, "rb") as f:
            bdata = f.read()

        print("read binary data at",path)


        return bdata


    def get_filename(self, fullname):

        #print("sys.meta_path length is",len(sys.meta_path))

        fullpath = os.getcwd() + os.sep + fullname + ".aky"
        return fullpath



    def source_to_code(self, data, path, *, _optimize=-1):
        """Return the code object compiled from source.

        The 'data' argument can be any object type that compile() supports.
        """

        print("compiling module at",path,"from source")

        options = Record({'filename': path,
                          'verbose': True,
                          'execute': False},)

        aky_ast = akycomp.generate(options)

        ast.fix_missing_locations(aky_ast)


        # return _bootstrap._call_with_frames_removed(compile, data, path, 'exec',
        #                                 dont_inherit=True, optimize=_optimize)
        aky_codeobj = super().source_to_code(aky_ast, path)

        return aky_codeobj



    def set_data(self, path, data):
        # data is a bytearray ready to be written to pyc
        #   i.e. it already has a magic/mtime/size header
        #   followed by marshalled code object
        # path is the full path of the pyc file to write

        # The following is taken directly from the set_data
        #   implementation in importlib.abc.SourceFileLoader,
        #   replacing internal functions with their
        #   os or os.path versions

        parent, filename = os.path.split(path)
        path_parts = []
        # Figure out what directories are missing.
        while parent and not os.path.isdir(parent):
            parent, part = os.path.split(parent)
            path_parts.append(part)
        # Create needed directories.
        for part in reversed(path_parts):
            parent = os.path.join(parent, part)
            try:
                os.mkdir(parent)
            except FileExistsError:
                # Probably another Python process already created the dir.
                continue
            except OSError as exc:
                # Could be a permission error, read-only filesystem: just forget
                # about writing the data.
                #_verbose_message('could not create {!r}: {!r}', parent, exc)
                return
        try:
            #_write_atomic(path, data, _mode)
            with open(path, "wb") as pycfile:
                pycfile.write(data)

            #_verbose_message('created {!r}', path)
        except OSError as exc:
            # Same as above: just don't write the bytecode.
            #_verbose_message('could not create {!r}: {!r}', path, exc)
            pass







class AnokyFinder(iabc.MetaPathFinder):


    def find_spec(self, fullname, path, target=None):

        #print("finding spec for ",fullname)

        if path is not None:

            #print("path is ",path)

            if isinstance(path, list):
                #os.chdir(path[0])
                pass
            else:
                # "namespace path" ??
                return None

        cwd = os.getcwd()
        filename = fullname + ".aky"
        fullpath = cwd + os.sep + filename

        if os.path.isfile(filename):
            print(filename," found")

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

            print("found aky module",filename)

            return spec

        return None


#sys.meta_path.append(AnokyFinder())

sys.meta_path = [AnokyFinder()] + sys.meta_path

#print(len(sys.meta_path))

# if all([not isinstance(f, AnokyFinder) for f in sys.meta_path]):
#     sys.meta_path = [AnokyFinder()] + sys.meta_path




#print(sys.meta_path)


#import pyctest




