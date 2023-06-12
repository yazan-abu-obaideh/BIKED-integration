from service.main.recommendation.bike_recommendation_service import BikeRecommendationService
from service.main.evaluation.evaluation_service import EvaluationService
from flask import Flask, request, make_response

BAD_REQUEST = 400

UTF_8 = "utf-8"

app = Flask(__name__)
evaluation_service = EvaluationService()
recommendation_service = BikeRecommendationService()


def get_xml(_request) -> str:
    return _request.data.decode(UTF_8)


@app.errorhandler(ValueError)
def handle_value_error(e):
    response_json = {"message": f"{e}"}
    return make_response(response_json, BAD_REQUEST)


@app.route("/evaluate")
def evaluate_design():
    return evaluation_service.evaluate_xml(get_xml(request))


@app.route("/recommend")
def recommend_similar():
    return recommendation_service.recommend_bike_from_xml(get_xml(request))


@app.route("/health")
def get_health():
    return make_response({"health": "UP"})
