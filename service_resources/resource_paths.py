import os.path


def get_path(path):
    return os.path.join(os.path.dirname(__file__), path)


MODEL_PATH = get_path("generated/models/Trained Models/AutogluonModels/ag-20231012_051754/")
RECOMMENDATION_DATASET_PATH = get_path("generated/BIKED_recommend.csv")
ALL_STRUCTURAL_DATASET = get_path("all_structural_data_aug.csv")
