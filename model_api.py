from flask import Flask, request
from predictor import Predictor

app = Flask(__name__)


@app.route("/")
def index():
    model_response = Predictor.predict(**request.json)
    return model_response


if __name__ == "__main__":
    app.run(debug=True, port=5050)
