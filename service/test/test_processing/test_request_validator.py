import unittest

from service.main.processing.request_validator import RequestValidator


class RequestValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = RequestValidator()

    def test_throw_if_empty(self):
        message = "Invalid BikeCAD file"
        with self.assertRaises(ValueError) as context:
            self.validator.raise_if_empty({}, message)
        self.assertEqual(message, context.exception.args[0])

    def test_does_not_throw_if_not_empty(self):
        self.validator.raise_if_empty({"1": 1}, "should_not_raise")

    def test_validate_scheme(self):
        message = "Required parameters ['y', 'z'] missing"
        with self.assertRaises(ValueError) as context:
            self.validator.raise_if_does_not_contain({"x": 5}, ["y", "z"])
        self.assertEqual(message, context.exception.args[0])

    def test_valid_scheme_does_not_raise(self):
        self.validator.raise_if_does_not_contain({"x": 5, "y": 3}, ["x", "y"])
