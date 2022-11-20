from flask import Flask, request, make_response
from main.autogluon_model_helpers.autogluon_service import AutogluonService

app = Flask(__name__)
service = AutogluonService()


@app.errorhandler(ValueError)
def handle_value_error(e):
    return make_response(f"Bad Request {e}", 400)


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    return service.predict_from_xml(request_as_raw_xml)
