import os.path
import unittest
from production.autogluon.autogluon_service import AutogluonService
import pandas as pd


class TestAutogluonService(unittest.TestCase):
    def setUp(self) -> None:
        self.auto_service = AutogluonService()
        self.xml_request = self.get_xml()

    def test_can_turn_xml_into_pd_row(self):
        expected_row = pd.DataFrame.from_dict({'Material=Steel': {0: '-1.2089779626768866'}, 'Material=Aluminum': {0: '-0.46507861303022335'}, 'Material=Titanium': {0: '1.8379997074342262'}, 'SSB_Include': {0: '1.0581845284004865'}, 'CSB_Include': {0: '-0.9323228669601348'}, 'CS Length': {0: '-0.4947762070020683'}, 'BB Drop': {0: '0.19327064177679704'}, 'Stack': {0: '-0.036955840782382385'}, 'SS E': {0: '-0.4348758585162575'}, 'ST Angle': {0: '1.203226228166099'}, 'BB OD': {0: '-0.14197615979296274'}, 'TT OD': {0: '-0.5711431568166616'}, 'HT OD': {0: '-0.879229453202825'}, 'DT OD': {0: '-0.8924125880651749'}, 'CS OD': {0: '-0.6971543225296617'}, 'SS OD': {0: '-0.7226114906751929'}, 'ST OD': {0: '-0.8962254490159303'}, 'CS F': {0: '0.1664798679079193'}, 'HT LX': {0: '-0.5559202673887266'}, 'ST UX': {0: '-0.5875970924732736'}, 'HT UX': {0: '-0.1666775498399638'}, 'HT Angle': {0: '1.5120924379123033'}, 'HT Length': {0: '0.7032710935570091'}, 'ST Length': {0: '0.980667290296069'}, 'BB Length': {0: '-0.25473226064604454'}, 'Dropout Offset': {0: '-0.0325700226355687'}, 'SSB OD': {0: '-2.1985552817712657'}, 'CSB OD': {0: '-0.279547847307574'}, 'SSB Offset': {0: '-0.09050848378506038'}, 'CSB Offset': {0: '0.5823537937924539'}, 'SS Z': {0: '-0.06959536571235439'}, 'SS Thickness': {0: '0.5180142556590571'}, 'CS Thickness': {0: '1.7994950500929077'}, 'TT Thickness': {0: '0.2855204217004274'}, 'BB Thickness': {0: '-0.11934492802927218'}, 'HT Thickness': {0: '-0.7465363724789722'}, 'ST Thickness': {0: '-0.5700521782698762'}, 'DT Thickness': {0: '-1.0553146425778421'}, 'DT Length': {0: '0.10253602811555089'}})
        assert self.auto_service.get_row(self.xml_request).equals(expected_row)

    def get_xml(self):
        with open(os.path.join(os.path.dirname(__file__), "../../resources/BikeCADXmlRequest.xml"), "r") as file:
            return file.read()
