import os.path
import unittest
from production.autogluon.autogluon_service import AutogluonService
import pandas as pd


class TestAutogluonService(unittest.TestCase):
    def setUp(self) -> None:
        self.auto_service = AutogluonService()
        self.xml_request = self.get_xml()

    def get_xml(self):
        with open(os.path.join(os.path.dirname(__file__), "../../resources/BikeCADXmlRequest.xml"), "r") as file:
            return file.read()
