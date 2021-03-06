from anoky.common.globals import G
import anoky.common.options
from anoky.common.string_stuff import indent_string


class CompilerError(Exception):
    name = "Generic Error"
    def __init__(self, range_or_pos, message:str):
        self.message = message
        self.range_or_pos = range_or_pos
        if G.Options.PRINT_ERRORS_ON_CREATION:
            print(self.trace)

    @property
    def trace(self):
        trace = self.__class__.name + ":\n"
        message = "\n" + indent_string(self.message) if "\n" in self.message else self.message
        if self.range_or_pos is not None:
            trace += "    %s: %s" %(str(self.range_or_pos), message)
        else:
            trace += message
        return trace

class TokenizingError(CompilerError):
    name = "Tokenization Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class SyntaxError(CompilerError):
    name = "Syntax Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class ArrangementError(CompilerError):
    name = "Arrangement Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class SemanticAnalysisError(CompilerError):
    name = "Semantic Analysis Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class DispatchError(CompilerError):
    name = "Dispatch Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class MacroExpansionError(CompilerError):
    name = "Macro Generation Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class CodeGenerationError(CompilerError):
    name = "Code Generation Error"

    def __init__(self, range_or_pos, message: str):
        CompilerError.__init__(self, range_or_pos, message)



class MetaError(CompilerError):
    name = "Meta Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)