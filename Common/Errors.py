from .Options import PRINT_ERRORS_ON_CREATION

class LycError(Exception):
    name = "Generic Error"
    def __init__(self, range_or_pos, message:str):
        self.message = message
        self.range_or_pos = range_or_pos
        if PRINT_ERRORS_ON_CREATION:
            print(self.trace)

    @property
    def trace(self):
        trace = self.__class__.name + ":\n"
        trace += "    %s: %s" %(str(self.range_or_pos), self.message)
        return trace

class TokenizingError(LycError):
    name = "Tokenization Error"
    def __init__(self, range_or_pos, message:str):
        LycError.__init__(self, range_or_pos, message)

class SyntaxError(LycError):
    name = "Syntax Error"
    def __init__(self, range_or_pos, message:str):
        LycError.__init__(self, range_or_pos, message)

class ArrangementError(LycError):
    name = "Arrangement Error"
    def __init__(self, range_or_pos, message:str):
        LycError.__init__(self, range_or_pos, message)

class SemanticAnalysisError(LycError):
    name = "Semantic Analysis Error"
    def __init__(self, range_or_pos, message:str):
        LycError.__init__(self, range_or_pos, message)

class DispatchError(LycError):
    name = "Dispatch Error"
    def __init__(self, range_or_pos, message:str):
        LycError.__init__(self, range_or_pos, message)

class CodeGenerationError(LycError):
    name = "Code Generation Error"
    def __init__(self, range_or_pos, message:str):
        LycError.__init__(self, range_or_pos, message)