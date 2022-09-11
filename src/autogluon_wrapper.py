from MultilabelPredictor import MultilabelPredictor
import os
from predictor import Predictor


class AutogluonPredictorWrapper(Predictor):
    def __init__(self):
        relative_path = "src/AutogluonModels/ag-20220911_073209"
        self.multi_predictor = MultilabelPredictor.load(os.path.abspath(relative_path))

    def predict(self, data):
        self.multi_predictor: MultilabelPredictor
        return self.multi_predictor.predict(data)
