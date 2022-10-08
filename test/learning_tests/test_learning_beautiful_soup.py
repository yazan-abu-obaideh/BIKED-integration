import unittest
from bs4 import BeautifulSoup


class BSAndLxmlLearningTest(unittest.TestCase):
    def setUp(self):
        with open("../resources/test.xml", "r") as file:
            self.soup = BeautifulSoup(file.read(), "xml")
            self.original_first_entry = self.get_first_entry()

    def test_find_all_entries(self):
        assert self.soup.find_all("entry").__str__() == \
               '[<entry key="ready">3</entry>, <entry key="stuff">5</entry>]'

    def test_change_entry_text(self):
        original_text = "3"
        assert self.original_first_entry.text == original_text
        updated = "5"
        self.original_first_entry.find(string=original_text).replace_with(updated)
        updated_first_entry = self.get_first_entry()
        assert updated_first_entry.text == updated

    def test_change_entry_key(self):
        assert self.original_first_entry['key'] == "ready"
        self.original_first_entry['key'] = "changed-ready"
        updated_first_entry = self.get_first_entry()
        assert updated_first_entry['key'] == "changed-ready"

    def get_first_entry(self):
        return self.soup.find_all("entry")[0]
