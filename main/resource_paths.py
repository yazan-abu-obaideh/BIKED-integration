import os.path


def get_absolute(path):
    return os.path.abspath


MODEL_PATH = os.path.join(os.path.dirname(__file__),
                          "resources/large/generated/models/Trained Models/AutogluonModels/ag-20220911_073209/")
