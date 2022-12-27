import os.path
import unittest

from main.request_processing.request_processor import RequestProcessor
from test.test_request_processing.settings_for_test import Settings

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "../resources/SimpleModel1.xml")


class RequestProcessorTest(unittest.TestCase):
    def setUp(self) -> None:
        bikeCad_file = self.get_BikeCad_file_as_raw_xml()
        self.processor = RequestProcessor(Settings())
        self.result_dict = self.processor.convert_xml(bikeCad_file)

    def test_can_transform(self):
        actual = self.result_dict["TT Thickness"]
        self.assertEqual(5, actual)

    def test_does_ignore(self):
        self.assertTrue("irrelevant" not in self.result_dict.keys())

    def test_special_behavior(self):
        self.assertEqual(self.result_dict["Material=Steel"], 1)
        self.assertEqual(self.result_dict["CSB_Include"], 0)

    def test_units_converted(self):
        self.assertEqual(self.result_dict["CS F"], 0.05)

    def test_ramifications(self):
        self.assertEqual(self.result_dict["CSB OD"], 17.759)

    def test_calculates_composite_values(self):
        self.assertEqual(self.result_dict['DT OD'], 12.5)

    def get_BikeCad_file_as_raw_xml(self):
        with open(RESOURCE_PATH, "r") as file:
            return file.read()
