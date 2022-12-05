import multiprocessing
import os.path
import unittest

from app import app
from requests import request as send_request
from time import sleep

class AppTest(unittest.TestCase):

    APP_PROCESS = None

    @staticmethod
    def run_app():
        app.run(port=5000)

    def test_empty_request(self):
        response = send_request("GET", "http://localhost:5000/evaluate")
        self.assertEqual("Invalid BikeCAD file", response.json()["message"])
        self.assertEqual(400, response.status_code)

    def test_valid_request(self):
        with open(os.path.join(os.path.dirname(__file__), "../../resources/FullModel1.xml")) as file:
            response = send_request("GET", "http://localhost:5000/evaluate", data=file)
        self.assertIsNotNone(response.json())
        self.assertEqual(200, response.status_code)


    @classmethod
    def setUpClass(cls) -> None:
        AppTest.APP_PROCESS = multiprocessing.Process(target=AppTest.run_app)
        AppTest.APP_PROCESS.start()
        while send_request("GET", "http://127.0.0.1:5000/health").text != "UP":
            sleep(0.5)
    @classmethod
    def tearDownClass(cls) -> None:
        AppTest.APP_PROCESS.terminate()
