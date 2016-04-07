from unittest import TestCase

from anoky.common.errors import TokenizingError
from anoky.parsers._LycParser import LycParser

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


