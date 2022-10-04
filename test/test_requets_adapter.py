import unittest
from production.xml_handler import XmlHandler
from production.request_adapter import RequestAdapter


class RequestAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.x = XmlHandler()
        self.bikeCad_file = self.get_BikeCad_file_as_raw_xml()
        self.adapter = RequestAdapter()

    def test_can_convert(self):
        result_dict = self.adapter.convert(self.bikeCad_file)
        stuff = {' ST Length': 570.0,
                 ' ST UX': 14.3,
                 ' ST OD': 29.0,
                 ' SS Z': 9.0,
                 ' HT UX': 23.3,
                 ' CSB Offset': 350.0,
                 ' HT Length': 157.3,
                 ' HT Angle': 73.49999999999999,
                 ' CSB_Include': 0,
                 ' ST Thickness': 0.9,
                 ' CS F': 15.0,
                 ' HT OD': 32.0,
                 ' CS Thickness': 1.2,
                 ' BB OD': 40.0,
                 ' Dropout Offset': 130.0,
                 ' Stack': 565.6,
                 ' ST Angle': 73.49999999999999,
                 ' CS Length': 440.0,
                 ' CSB OD': 18.0,
                 ' BB Length': 68.0,
                 ' SS E': 45.0,
                 ' BB Drop': 280.0,
                 ' SSB Offset': 330.0,
                 ' TT Thickness': 0.9,
                 ' SSB OD': 16.0,
                 ' SS Thickness': 1.0,
                 ' SSB_Include': 1,
                 ' DT Thickness': 0.9,
                 ' HT LX': 39.5,
                 ' Material=Steel': True,
                 ' Material=Aluminum': False,
                 ' Material=Titanium': False,
                 ' HT Thickness': 2,
                 ' BB Thickness': 2}
        assert result_dict == {key.strip(): value for key, value in stuff.items()}

    def get_BikeCad_file_as_raw_xml(self):
        with open("../resources/Model2.xml", "r") as file:
            return file.read()


