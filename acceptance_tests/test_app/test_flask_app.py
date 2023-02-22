import multiprocessing
import os.path
import unittest

from app import app
from requests import request as send_request
from time import sleep, time

GET = "GET"

OK = 200
BAD_REQUEST = 400

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../test/resources/bikes/FullModel1.xml")


# TODO: find out why running these tests in debug mode causes failures
#  (debug debug bug LMAO)
class AppTest(unittest.TestCase):
    APP_PROCESS = None

    def test_empty_request(self):
        response = send_request(GET, self.get_feature_url('evaluate'))
        self.assertEqual("Invalid BikeCAD file", response.json()["message"])
        self.assertEqual(BAD_REQUEST, response.status_code)

    def test_valid_evaluation_request(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            response = send_request(GET, self.get_feature_url('evaluate'), data=file)
        self.assertIsNotNone(response.json())
        self.assertIs(type(response.json()), dict)
        self.assertEqual(OK, response.status_code)

    def test_valid_recommendation_request(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            response = send_request(GET, self.get_feature_url('recommend'), data=file)
        self.assertIsNotNone(response.text)
        self.assertEqual(OK, response.status_code)

    def get_feature_url(self, feature):
        return f"http://localhost:5000/{feature}"

    @classmethod
    def setUpClass(cls) -> None:
        AppTest.APP_PROCESS = multiprocessing.Process(target=AppTest.run_app)
        AppTest.APP_PROCESS.start()
        start_time = time()
        while AppTest.site_not_up():
            cls.handle_time_out(start_time)
            sleep(0.5)

    @classmethod
    def handle_time_out(cls, start_time):
        if AppTest.more_than_x_seconds_since(start_time, x=5):
            AppTest.APP_PROCESS.terminate()
            raise SystemError("Timed out waiting for app to start")

    @classmethod
    def tearDownClass(cls) -> None:
        AppTest.APP_PROCESS.terminate()

    @staticmethod
    def site_not_up():
        return send_request(GET, "http://localhost:5000/health").json()["health"] != "UP"

    @staticmethod
    def run_app():
        app.run(port=5000)

    @staticmethod
    def more_than_x_seconds_since(start_time, x):
        return (time() - start_time) > x
