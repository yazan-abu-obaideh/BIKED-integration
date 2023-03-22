import unittest
from bs4 import BeautifulSoup
import os

RESOURCE_FILE_PATH = os.path.join(os.path.dirname(__file__), "../resources/test.xml")


class BSAndLxmlLearningTest(unittest.TestCase):
    def setUp(self):
        with open(RESOURCE_FILE_PATH, "r") as file:
            self.soup = BeautifulSoup(file.read(), "xml")
            self.original_first_entry = self.get_first_entry()

    def test_find_all_entries(self):
        self.assertEqual(self.soup.find_all("entry").__str__(),
                         '[<entry key="ready">3</entry>, <entry key="stuff">5</entry>]')

    def test_change_entry_text(self):
        original_text = "3"
        self.assertEqual(self.original_first_entry.text, original_text)
        updated = "5"
        self.original_first_entry.find(string=original_text).replace_with(updated)
        updated_first_entry = self.get_first_entry()
        self.assertEqual(updated_first_entry.text, updated)

    def test_change_entry_key(self):
        self.assertEqual(self.original_first_entry['key'], "ready")
        self.original_first_entry['key'] = "changed-ready"
        updated_first_entry = self.get_first_entry()
        self.assertEqual(updated_first_entry['key'], "changed-ready")

    def get_first_entry(self):
        return self.soup.find_all("entry")[0]

    def test_get_entire_document(self):
        self.assertEqual('''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
<comment> Made with care! </comment>
<entry key="ready">3</entry>
<entry key="stuff">5</entry>
</properties>''', self.soup.__str__())
