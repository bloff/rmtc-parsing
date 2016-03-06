from rmtc.Common.Globals import G

class ErrorInPosition(Exception):
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

class TokenizingError(ErrorInPosition):
    name = "Tokenization Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)

class SyntaxError(ErrorInPosition):
    name = "Syntax Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)

class ArrangementError(ErrorInPosition):
    name = "Arrangement Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)

class SemanticAnalysisError(ErrorInPosition):
    name = "Semantic Analysis Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)

class DispatchError(ErrorInPosition):
    name = "Dispatch Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)

class CodeGenerationError(ErrorInPosition):
    name = "Code Generation Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)

class MetaError(ErrorInPosition):
    name = "Meta Error"
    def __init__(self, range_or_pos, message:str):
        ErrorInPosition.__init__(self, range_or_pos, message)