import os.path
import unittest


MODEL_NAME = "ag-20220911_073209"
class ResourcesTester(unittest.TestCase):
    def model_exists(self):
        self.assertTrue(os.path.isdir(""))
