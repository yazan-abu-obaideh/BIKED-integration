from flask import Flask, request, make_response
from main.evaluation.evaluation_service import EvaluationService

UTF_8 = "utf-8"

app = Flask(__name__)
evaluation_service = EvaluationService()


@app.errorhandler(ValueError)
def handle_value_error(e):
    response_json = {"message": f"{e}"}
    return make_response(response_json, 400)


@app.route("/evaluate")
def evaluate_design():
    request_as_raw_xml = request.data.decode(UTF_8)
    return evaluation_service.predict_from_xml(request_as_raw_xml)


@app.route("/recommend")
def recommend_similar():
    request_dict = request.data.decode(UTF_8)
    return request_dict
