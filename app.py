from flask import Flask, request
from production.autogluon.autogluon_service import AutogluonService

app = Flask(__name__)
service = AutogluonService()


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    return service.predict_from_xml(request_as_raw_xml)
