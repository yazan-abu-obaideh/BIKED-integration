import multiprocessing
import os.path
import unittest

from app import app
from requests import request as send_request
from time import sleep, time

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../resources/bikes/FullModel1.xml")


class AppTest(unittest.TestCase):
    APP_PROCESS = None

    def test_empty_request(self):
        response = send_request("GET", "http://localhost:5000/evaluate")
        self.assertEqual("Invalid BikeCAD file", response.json()["message"])
        self.assertEqual(400, response.status_code)

    def test_valid_evaluation_request(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            response = send_request("GET", "http://localhost:5000/evaluate", data=file)
        self.assertIsNotNone(response.json())
        self.assertIs(type(response.json()), dict)
        self.assertEqual(200, response.status_code)

    def test_valid_recommendation_request(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            response = send_request("GET", "http://localhost:5000/recommend", data=file)
        print(response.content)
        self.assertIsNotNone(response.text)

    @classmethod
    def setUpClass(cls) -> None:
        AppTest.APP_PROCESS = multiprocessing.Process(target=AppTest.run_app)
        AppTest.APP_PROCESS.start()
        start_time = time()
        while AppTest.site_not_up():
            if AppTest.has_timed_out(start_time):
                AppTest.APP_PROCESS.terminate()
                raise SystemError("Timed out waiting for app to start")
            sleep(0.5)

    @classmethod
    def tearDownClass(cls) -> None:
        AppTest.APP_PROCESS.terminate()

    @staticmethod
    def site_not_up():
        return send_request("GET", "http://localhost:5000/health").text != "UP"

    @staticmethod
    def run_app():
        app.run(port=5000)

    @staticmethod
    def has_timed_out(start_time):
        return (time() - start_time) > 5
