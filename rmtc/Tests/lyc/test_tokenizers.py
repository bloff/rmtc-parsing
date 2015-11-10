from unittest import TestCase

from rmtc.Common.Errors import TokenizingError
from rmtc.Parsers import _LycParser

parser = _LycParser()

class TestTokenizer(TestCase):
    def test_no_token(self):
        self.assertRaises(TokenizingError, parser.tokenize_into_node, "")

    def test_closing(self):
        self.assertRaises(TokenizingError, parser.tokenize_into_node, ")")

    def test_open_no_close(self):
        self.assertRaises(TokenizingError, parser.tokenize_into_node, "(")

    def test_open_close(self):
        parser.tokenize("()")


