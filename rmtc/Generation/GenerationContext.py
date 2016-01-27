from rmtc.Common.Context import Context





class GenerationContext(Context):

    def __init__(self, **kwargs):

        Context.__init__(self, "Code Generation Context")

        self.set(**kwargs)




    def generate(self, element):

        return self.generator.generate(element, self)

