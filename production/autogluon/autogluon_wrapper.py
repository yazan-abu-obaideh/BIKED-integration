import __main__
import os
from production.autogluon.MultilabelPredictor import MultilabelPredictor
from production.predictor import Predictor


class AutogluonPredictorWrapper(Predictor):

    def __init__(self):
        __main__.MultilabelPredictor = MultilabelPredictor
        relative_path = os.path.join(os.path.dirname(__file__),
                                     "../../resources/models/Trained Models/AutogluonModels/ag-20220911_073209/")
        self.multi_predictor = MultilabelPredictor.load(os.path.abspath(relative_path))
        self.labels = self.multi_predictor.labels

    def predict(self, data):
        self.multi_predictor: MultilabelPredictor
        return self.multi_predictor.predict(data)

