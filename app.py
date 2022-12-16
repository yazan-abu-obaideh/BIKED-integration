from main.recommendation.bike_recommendation_service import BikeRecommendationService
from main.evaluation.evaluation_service import EvaluationService
from flask import Flask, request, make_response

BAD_REQUEST = 400

UTF_8 = "utf-8"

app = Flask(__name__)
evaluation_service = EvaluationService()
recommendation_service = BikeRecommendationService()


@app.errorhandler(ValueError)
def handle_value_error(e):
    response_json = {"message": f"{e}"}
    return make_response(response_json, BAD_REQUEST)


@app.route("/evaluate")
def evaluate_design():
    request_as_raw_xml = request.data.decode(UTF_8)
    return evaluation_service.predict_from_xml(request_as_raw_xml)


@app.route("/recommend")
def recommend_similar():
    request_as_raw_xml = request.data.decode(UTF_8)
    return recommendation_service.recommend_bike(request_as_raw_xml)

@app.route("/health")
def get_health():
    return "UP"
