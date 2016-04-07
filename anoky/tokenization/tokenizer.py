from anoky.tokenization import tokenization_context


class Tokenizer(object):
    """
    A ``Tokenizer`` is an object for generating tokens (:ref:`Token`).
    """
    def __init__(self, context:tokenization_context):
        self.context = context

    def run(self):
        """
        This method should be a generator that yields tokens.
        """
        raise NotImplementedError()

