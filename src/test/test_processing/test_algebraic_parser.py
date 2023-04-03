import unittest

from src.main.processing.algebraic_parser import AlgebraicParser


class AlgebraicParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = AlgebraicParser()

    def test_parse_valid_booleans(self):
        parsed = self.parser.attempt_parse("tRue")
        self.assertEqual(1, parsed)
        self.assertIs(float, type(parsed))
        self.assertEqual(0, self.parser.attempt_parse("fAlsE"))

    def test_parse_valid_floats(self):
        parsed = self.parser.attempt_parse("5000")
        self.assertEqual(5000, parsed)
        self.assertIs(float, type(parsed))
        self.assertEqual(2500.15, self.parser.attempt_parse("2500.15"))

    def test_parse_very_large_float(self):
        self.assertEqual(float("inf"), self.parser.attempt_parse("1e100000"))
        self.assertEqual(float("inf"), self.parser.attempt_parse("1e100000"))

    def test_parse_non_algebraic_value(self):
        self.assertEqual("VALUE", self.parser.attempt_parse("   VALUE   "))
