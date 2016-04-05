from rmtc.Common.Context import Context





class GenerationContext(Context):

    def __init__(self, **kwargs):

        Context.__init__(self, "Code Generation Context")

        self.set(**kwargs)




    def generate(self, element):

        ast =  self.generator.generate(element, self)

        # copy line and column number info from the generated element
        range = element.range
        if range is not None:
            lineno = range.first_position.line
            col_offset = range.first_position.column
            if isinstance(ast, list):
                for node in ast:
                    node.lineno = lineno
                    node.col_offset = col_offset
            else:
                ast.lineno = lineno
                ast.col_offset = col_offset

        return ast


