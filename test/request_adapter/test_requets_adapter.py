import os.path
import unittest
from production.xml_handler import XmlHandler
from production.request_adapter.request_adapter import RequestAdapter

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "../../resources/SimpleModel1.xml")


class RequestAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.x = XmlHandler()
        self.bikeCad_file = self.get_BikeCad_file_as_raw_xml()
        self.adapter = RequestAdapter()
        self.result_dict = self.adapter.convert_xml(self.bikeCad_file)

    def test_can_transform(self):
        assert self.result_dict["TT Thickness"] == 5 != self.adapter.default_values['TT Thickness']

    def test_does_ignore(self):
        assert "irrelevant" not in self.result_dict.keys()

    def test_special_behavior(self):
        assert self.result_dict["Material=Steel"] == 1
        assert self.result_dict["CSB_Include"] == 0

    def test_ramifications(self):
        assert self.result_dict["CSB_OD"] == 0.017759

    def test_default(self):
        assert self.result_dict["HT Thickness"] == 2

    def get_BikeCad_file_as_raw_xml(self):
        with open(RESOURCE_PATH, "r") as file:
            return file.read()
