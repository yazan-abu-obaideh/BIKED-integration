from flask import Flask, request, make_response
from main.evaluation.autogluon_service import EvaluationService

app = Flask(__name__)
service = EvaluationService()


@app.errorhandler(ValueError)
def handle_value_error(e):
    response_json = {"message": f"{e}"}
    return make_response(response_json, 400)


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    return service.predict_from_xml(request_as_raw_xml)
