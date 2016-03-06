from rmtc.Common.Globals import G

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
        trace += "    %s: %s" %(str(self.range_or_pos), self.message)
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

class CodeGenerationError(CompilerError):
    name = "Code Generation Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)

class MetaError(CompilerError):
    name = "Meta Error"
    def __init__(self, range_or_pos, message:str):
        CompilerError.__init__(self, range_or_pos, message)