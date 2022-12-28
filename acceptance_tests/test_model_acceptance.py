import unittest

from main.evaluation.evaluation_service import DefaultAdapterSettings, EvaluationService


class ModelAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EvaluationService()
