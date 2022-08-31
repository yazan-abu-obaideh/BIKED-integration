from flask import Flask, request
from src.predictor import Predictor
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route("/")
def index():
    request_string = request.data.decode("utf-8")
    soup = BeautifulSoup(request_string, "xml")
    entries = soup.find_all("entry")
    entries_dict = {entry['key']: entry.text for entry in entries}
    print(entries_dict)
    p = Predictor()

    model_response = p.predict(**request.json)
    return f"{model_response}"


if __name__ == "__main__":
    app.run(debug=True, port=5050)
