import os.path


def get_path(path):
    return os.path.join(os.path.dirname(__file__), path)


MODEL_PATH = get_path("resources/large/generated/models/Trained Models/AutogluonModels/ag-20220911_073209/")
RECOMMENDATION_DATASET_PATH = get_path("resources/generated/BIKED_recommend.csv")
ALL_STRUCTURAL_DATASET = get_path("resources/all_structural_data_aug.csv")
