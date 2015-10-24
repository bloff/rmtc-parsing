from Common.Errors import TokenizingError
from Parsers.LycParser import LycParser
from unittest import TestCase

parser = LycParser()

class TestTokenizer(TestCase):
    def test_no_token(self):
        self.assertRaises(TokenizingError, parser.tokenize_into_node, "")

    def test_closing(self):
        self.assertRaises(TokenizingError, parser.tokenize_into_node, ")")

    def test_open_no_close(self):
        self.assertRaises(TokenizingError, parser.tokenize_into_node, "(")

    def test_open_close(self):
        parser.tokenize("()")


