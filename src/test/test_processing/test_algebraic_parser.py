import unittest

from src.main.processing.algebraic_parser import AlgebraicParser


class AlgebraicParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = AlgebraicParser()

    def test_parse_valid_booleans(self):
        parsed = self.parser.parse("tRue")
        self.assertEqual(1, parsed)
        self.assertIs(float, type(parsed))
        self.assertEqual(0, self.parser.parse("fAlsE"))

    def test_parse_valid_floats(self):
        parsed = self.parser.parse("5000")
        self.assertEqual(5000, parsed)
        self.assertIs(float, type(parsed))
        self.assertEqual(2500.15, self.parser.parse("2500.15"))

    def test_parse_very_large_float(self):
        self.assertEqual(float("inf"), self.parser.parse("1e100000"))
        self.assertEqual(float("inf"), self.parser.parse("1e100000"))

    def test_parse_invalid_booleans(self):
        self.assertEqual(None, self.parser.parse("NOT_ALGEBRAIC"))
