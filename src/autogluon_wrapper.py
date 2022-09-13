from MultilabelPredictor import MultilabelPredictor
import os
from predictor import Predictor

FILE_PATH = os.path.dirname(__file__)


class AutogluonPredictorWrapper(Predictor):

    def __init__(self):
        relative_path = os.path.join(FILE_PATH, "../resources/AutogluonModels/ag-20220911_073209")
        self.multi_predictor = MultilabelPredictor.load(relative_path)

    def predict(self, data):
        self.multi_predictor: MultilabelPredictor
        return self.multi_predictor.predict(data)
