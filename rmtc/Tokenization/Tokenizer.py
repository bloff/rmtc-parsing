from rmtc.Tokenization import TokenizationContext


class Tokenizer(object):
    """
    A ``Tokenizer`` is an object for generating tokens (:ref:`Token`).
    """
    def __init__(self, context:TokenizationContext):
        self.context = context

    def run(self):
        """
        This method should be a generator that yields tokens.
        """
        raise NotImplementedError()

