import os.path
import unittest
from src.main.resource_paths import *


class ResourcesTester(unittest.TestCase):
    def test_model_exists(self):
        self.assert_directory_exists(MODEL_PATH)

    def test_recommendation_dataset_exists(self):
        self.assert_file_exists(RECOMMENDATION_DATASET_PATH)

    def test_structural_dataset_exists(self):
        self.assert_file_exists(ALL_STRUCTURAL_DATASET)

    def assert_directory_exists(self, directory_path):
        self.assertTrue(os.path.isdir(directory_path))

    def assert_file_exists(self, filepath):
        self.assertTrue(os.path.isfile(filepath))
