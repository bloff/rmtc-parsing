import ast
import importlib
import importlib.abc as iabc
import importlib.machinery as imach
import os
import sys

# from importlib import _bootstrap._call_with_frames_removed
# from importlib._bootstrap_external import _validate_bytecode_header, _code_to_bytecode, _compile_bytecode
from importlib._bootstrap_external import _NamespacePath
from importlib.util import cache_from_source

import importlib.machinery

from anoky.common.record import Record
import anoky.common.options as Options
import compiler_anoky as akycomp


def import_debug(*args):
    print("anoky.importer --- ", *args)
    pass


class AnokyLoader(iabc.SourceLoader):
    def __init__(self, name, origin):
        self.name = name
        self.origin = origin

    def path_stats(self, path):
        # if not os.path.samefile(path, self.origin):
        #     raise ImportError("Requested stats for path '%s' with loader for module at path '%s'." % (path, self.origin))
        s = os.stat(path)
        ret = {'mtime': s.st_mtime, 'size': s.st_size}
        import_debug("mstats for path ", path, ": ", ret)
        return ret

    def get_data(self, path):
        # raise NotImplementedError()
        with open(path, "rb") as f:
            bdata = f.read()

        import_debug("get_data: ", path)

        return bdata

    def get_filename(self, fullname):
        import_debug("get_filename: ", fullname)
        # if fullname != self.name:
        #     raise ImportError("Requested module name '%s' with loader for module name '%s'." %(fullname, self.name))
        return self.origin

    def source_to_code(self, data, path, *, _optimize=-1):
        """Return the code object compiled from source.

        The 'data' argument can be any object type that compile() supports.
        """

        import_debug("source_to_code: path=", path)

        options = Record({'filename': path,
                          'verbose': True,
                          'execute': False}, )

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

        import_debug("set_data: path=", path)

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
                # _verbose_message('could not create {!r}: {!r}', parent, exc)
                return
        try:
            # _write_atomic(path, data, _mode)
            with open(path, "wb") as pycfile:
                pycfile.write(data)

                # _verbose_message('created {!r}', path)
        except OSError as exc:
            # Same as above: just don't write the bytecode.
            # _verbose_message('could not create {!r}: {!r}', path, exc)
            pass


class AnokyFinder(iabc.MetaPathFinder):

    def find_spec(self, full_module_name, search_path, target=None):

        import_debug("Finding module spec for module_name: ", full_module_name)

        if search_path is None:
            import_debug("Given searchpath is None, using sys.path")
            search_path = sys.path

        modulename = full_module_name.rsplit(".", 1)[-1]
        filename = modulename + ".aky"
        import_debug("using search path: ", search_path)
        for path in search_path:
            if path == '': path = os.getcwd()
            filepath = os.path.join(path, filename)

            if os.path.isfile(filepath):
                import_debug("Found .aky file: ", filepath)

                spec = imach.ModuleSpec(
                    # name
                    name=full_module_name,
                    # loader
                    loader=AnokyLoader(full_module_name, filepath),
                    origin=filepath,
                    # __cached__=pycpath,
                    # etc.
                )

                return spec

        import_debug("Failed to find any .aky file!")

        return None


# sys.meta_path.append(AnokyFinder())

# sys.meta_path = [AnokyFinder()] + sys.meta_path

# print(len(sys.meta_path))

# If the
if not any(isinstance(f, AnokyFinder) for f in sys.meta_path):
    sys.meta_path = [AnokyFinder()] + sys.meta_path




# print(sys.meta_path)


# import pyctest
