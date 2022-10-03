from flask import Flask, request
from production.xml_handler import XmlHandler
from production.autogluon.autogluon_wrapper import AutogluonPredictorWrapper
from test.autogluon.test_saved_autogluon import AutogluonLearningTest
import pandas as pd

app = Flask(__name__)
xml_handler = XmlHandler()
predictor = AutogluonPredictorWrapper()
test = AutogluonLearningTest()
test.setUp()


def get_row_from_dict(model_input_dict):
    return pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    xml_handler.set_xml(request_as_raw_xml)
    response = predictor.predict(get_row_from_dict(xml_handler.get_entries_dict()))
    return response.to_dict()


def assert_model_is_functional():
    x, y = test.prepare_x_y()
    predictions = predictor.predict(x)
    r2, mse, mae = test.get_metrics(predictions, y)
    print(f"{r2=}")
    print(f"{mae=}")
    print(f"{mse=}")
    print("Model functional. All systems online.")


if __name__ == "__main__":
    assert_model_is_functional()
    app.run(debug=True, port=5050)
