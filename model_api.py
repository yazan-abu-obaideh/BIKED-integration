from flask import Flask, request
from src.xml_handler import XmlHandler
from autogluon_.autogluon_wrapper import AutogluonPredictorWrapper
from autogluon_.test_saved_autogluon import AutogluonLearningTest

app = Flask(__name__)
xml_handler = XmlHandler()
predictor = AutogluonPredictorWrapper()
test = AutogluonLearningTest()
test.setUp()


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    xml_handler.set_xml(request_as_raw_xml)
    model_response_dict = predictor.predict(**xml_handler.get_entries_dict())
    xml_handler.update_entries_from_dict(model_response_dict)
    return xml_handler.get_content_string()


def assert_model_is_functional():
    x, y = test.prepare_x_y()
    predictions = predictor.predict(x)
    r2, mse, mae = test.get_metrics(predictions, y)
    assert r2 > 0.93
    assert mse < 0.06
    assert mae < 0.11
    print("Model functional. All systems online.")


if __name__ == "__main__":
    assert_model_is_functional()
    app.run(debug=True, port=5050)
