from unittest import TestCase

from rmtc.Common.Errors import ArrangementError
from rmtc.Parsers._LycParser import LycParser
from rmtc.Syntax.Code import Code
from rmtc.Syntax.Identifier import Identifier
from rmtc.Syntax.Literal import Literal
from rmtc.Syntax.Node import Node

lyc_parser = LycParser()
arrange = lyc_parser.parse


class TestArrangement(TestCase):

    def _code_equals(self, code1:Code, code2:Code) -> bool:
        if isinstance(code1, Identifier):
            if not isinstance(code2, Identifier): return False
            elif not code1.name == code2.name: return False
            elif not code1.semantic_name == code2.semantic_name: return False
            else: return True
        elif isinstance(code1, Literal):
            if not isinstance(code2, Literal): return False
            elif not code1.value == code2.value: return False
            else: return True
        elif isinstance(code1, Node):
            if not code1.__class__ is code2.__class__: return False
            elif len(code1) != len(code2): return False
            else:
                e1 = code1.first
                e2 = code2.first
                while e1 is not None:
                    if not self._code_equals(e1.code, e2.code): return False
                    e1 = e1.next
                    e2 = e2.next
                return True


    def _test_arrangement_equals(self, code:str, lisp_form:str):
        code1 = lyc_parser.parse(code)
        code2 = lyc_parser.parse(lisp_form)
        self.assertTrue(self._code_equals(code1, code2))

    def test_bad_punct_1(self):
        self.assertRaises(ArrangementError, arrange, ", a")

    def test_bad_punct_2(self):
        self.assertRaises(ArrangementError, arrange, "a b, c,; d")

    def test_bad_punct_3(self):
        self.assertRaises(ArrangementError, arrange, "a b; d;: c")

    def test_bad_punct_4(self):
        self.assertRaises(ArrangementError, arrange, "a b, c; d:: c")





    def test_arrangement_equals_1(self):
        self._test_arrangement_equals("a b, c; d", "⦅a (b c) d⦆")

    def test_arrangement_equals_2(self):
        self._test_arrangement_equals(
            r"""
            (a, b, c,
             d, e, f)
            """,
            r"""
            (a b c
             d e f)
            """)


    def test_arrangement_apply_parenthesis(self):
        self._test_arrangement_equals(
            r"""
            a ⦅elif ⦆
            """,
            r"""
            ⦅a ⦅ ⦅elif ⦆⦆⦆
            """)

