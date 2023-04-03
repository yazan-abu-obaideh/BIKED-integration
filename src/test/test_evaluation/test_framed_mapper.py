import os.path
import unittest

from processing.algebraic_parser import AlgebraicParser
from processing.bike_xml_handler import BikeXmlHandler
from src.main.evaluation.framed_mapper import FramedMapper
from src.test.test_evaluation.settings_for_test import Settings

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "../resources/SimpleModel1.xml")


class FramedMapperTest(unittest.TestCase):
    def setUp(self) -> None:
        bikeCad_file = self.get_BikeCad_file_as_raw_xml()
        self.mapper = FramedMapper(Settings())
        handler = BikeXmlHandler()
        handler.set_xml(bikeCad_file)
        bike_dict = handler.get_parsable_entries_(
            AlgebraicParser().attempt_parse,
            key_filter=lambda x: x in Settings().get_expected_xml_keys(),
            parsed_value_filter=lambda y: y is not None
        )
        self.result_dict = self.mapper.map_dict(bike_dict)

    def test_can_transform(self):
        actual = self.result_dict["TT Thickness"]
        self.assertEqual(5, actual)

    def test_does_ignore(self):
        self.assertTrue("irrelevant" not in self.result_dict)

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
