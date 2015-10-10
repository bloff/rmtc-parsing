

class Code(object):
    """
    The base class for all syntax types.
    """
    def __init__(self):
        # reflexive

        self.range = None
        """
        The StreamRange_ (starting and ending position) of the Code instance in the source code.
        """
        #
        # # Syntactic Information:
        # #    range - filename, starting and ending position
        # self.syni = Record()
        #
        # # Semantic Information
        # #    Current environment
        # #    Imports
        # #    Inferred Type
        # #    Whether or not the code has already been semantically analysed
        # #    Other, form specific data:
        # #        Macro functions
        # #        Lval macros
        # #        etc...
        # self.semi = Record()