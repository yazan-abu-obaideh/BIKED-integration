from flask import Flask, request
from production.autogluon.autogluon_service import AutogluonService

app = Flask(__name__)
service = AutogluonService()


@app.route("/")
def index():
    request_as_raw_xml = request.data.decode("utf-8")
    return service.predict(request_as_raw_xml)


def end_to_end_test():
    def get_sample_BikeCadXml():
        with open("resources/BikeCADXmlRequest.xml", "r") as file:
            return file.read()

    assert service.predict(get_sample_BikeCadXml()) == {'Model Mass': -0.9461116790771484,
                                                        'Sim 1 Bottom Bracket X Disp.': 0.02232583984732628,
                                                        'Sim 1 Bottom Bracket Y Disp.': 0.2731778919696808,
                                                        'Sim 1 Dropout X Disp.': 0.09372919797897339,
                                                        'Sim 1 Dropout Y Disp.': 0.1128099337220192,
                                                        'Sim 1 Safety Factor': -0.8752062320709229,
                                                        'Sim 2 Bottom Bracket Z Disp.': 1.7482761144638062,
                                                        'Sim 3 Bottom Bracket X Rot.': 2.0954513549804688,
                                                        'Sim 3 Bottom Bracket Y Disp.': 3.2179315090179443,
                                                        'Sim 3 Safety Factor': -0.3395128548145294}


if __name__ == "__main__":
    app.run(debug=True, port=5050)
