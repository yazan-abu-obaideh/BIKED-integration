from flask import Flask, request
from src.xml_handler import XmlHandler
from src.autogluon_wrapper import AutogluonPredictorWrapper
from src.test_saved_autogluon import AutogluonLearningTest

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


if __name__ == "__main__":
    app.run(debug=True, port=5050)
