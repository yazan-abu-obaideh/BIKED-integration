from flask import Flask, request

from MultilabelPredictor import MultilabelPredictor
from src.xml_handler import XmlHandler
from src.autogluon_wrapper import AutogluonPredictorWrapper
from src.test_saved_autogluon import AutogluonLearningTest
import __main__

app = Flask(__name__)
xml_handler = XmlHandler()
predictor = AutogluonPredictorWrapper()


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    xml_handler.set_xml(request_as_raw_xml)
    model_response_dict = predictor.predict(**xml_handler.get_entries_dict())
    xml_handler.update_entries_from_dict(model_response_dict)
    return xml_handler.get_content_string()


def do_stuff():
    __main__.MultilabelPredictor = MultilabelPredictor
    test = AutogluonLearningTest()
    test.setUp()
    x, y = test.prepare_x_y()
    predictions = predictor.predict(x)
    r2, mse, mae = test.get_metrics(predictions, y)
    print(r2, mse, mae)


if __name__ == "__main__":
    do_stuff()
    app.run(debug=True, port=5050)
