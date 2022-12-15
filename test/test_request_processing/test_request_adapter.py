import os.path
import unittest
from main.xml_handler import XmlHandler
from main.request_processing.request_adapter import RequestAdapter
from test.test_request_processing.settings_for_test import Settings

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "../../resources/test-assets/SimpleModel1.xml")


class RequestAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.x = XmlHandler()
        self.bikeCad_file = self.get_BikeCad_file_as_raw_xml()
        self.adapter = RequestAdapter(Settings())
        self.x.set_xml(self.bikeCad_file)
        self.result_dict = self.adapter.convert_dict(self.x.get_entries_dict())

    def test_can_transform(self):
        self.assertTrue(self.result_dict["TT Thickness"] == 5 != self.adapter.settings.default_values()['TT Thickness'])

    def test_does_ignore(self):
        self.assertTrue("irrelevant" not in self.result_dict.keys())

    def test_special_behavior(self):
        self.assertEqual(self.result_dict["Material=Steel"], 1)
        self.assertEqual(self.result_dict["CSB_Include"], 0)

    def test_scaled(self):
        self.assertEqual(self.result_dict["CS F"], 0.5)

    def test_ramifications(self):
        self.assertEqual(self.result_dict["CSB OD"], 17.759)

    def test_calculates_composite_values(self):
        self.assertEqual(self.result_dict['DT OD'], 12.5)

    def get_BikeCad_file_as_raw_xml(self):
        with open(RESOURCE_PATH, "r") as file:
            return file.read()
