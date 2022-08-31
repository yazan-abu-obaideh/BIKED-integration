import unittest

from src.xml_handler import XmlHandler


class XmlHandlerTest(unittest.TestCase):
    def setUp(self):
        with open("../resources/test.xml", "r") as file:
            self.xml_handler = XmlHandler(file.read())

    def test_xml_tree_contains_entries(self):
        assert self.get_entries_count() == 2

    def test_can_copy(self):
        assert self.xml_handler.copy_first_entry()['key'] == "ready"
        assert self.xml_handler.copy_first_entry().text == "3"

    def test_can_add_new_entries(self):
        new_key = "key"
        new_value = "value"
        self.xml_handler.add_new_entry(new_key, new_value)
        # TODO: generalize this so it doesn't depend on the word entry in so many places.
        assert self.get_entries_count() == 3
        assert self.xml_handler.get_all_entries().__str__() == \
               f'[<entry key="ready">3</entry>, ' \
               f'<entry key="stuff">5</entry>, ' \
               f'<entry key="{new_key}">{new_value}</entry>]'

    def test_can_get_specific_entry(self):
        pass

    def get_entries_count(self):
        return len(self.xml_handler.get_all_entries())
