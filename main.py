from flask import Flask, request
from production.autogluon.autogluon_service import AutogluonService
import waitress
import logging

app = Flask(__name__)
service = AutogluonService()


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    return service.predict_from_xml(request_as_raw_xml)


if __name__ == "__main__":
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    waitress.serve(app, host="0.0.0.0", port=80)
