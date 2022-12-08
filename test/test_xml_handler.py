from main.xml_handler import XmlHandler
import unittest
import os

file_path = os.path.join(os.path.dirname(__file__), "../resources/test-assets/test.xml")


class XmlHandlerTest(unittest.TestCase):
    def setUp(self):
        with open(file_path, "r") as file:
            self.xml_handler = XmlHandler()
            self.xml_handler.set_xml(file.read())
        self.ENTRY_TAG = self.xml_handler.ENTRY_TAG
        self.ENTRY_KEY = self.xml_handler.ENTRY_KEY
        self.PARENT_TAG = self.xml_handler.PARENT_TAG

    def test_xml_tree_contains_entries(self):
        assert self.xml_handler.get_entries_count() == 2

    def test_can_copy(self):
        assert self.xml_handler.copy_first_entry()[self.ENTRY_KEY] == "ready"
        assert self.xml_handler.copy_first_entry().text == "3"

    def test_can_add_new_entries(self):
        new_key = "key"
        new_value = "value"
        self.xml_handler.add_new_entry(new_key, new_value)
        assert self.xml_handler.get_entries_count() == 3
        assert self.xml_handler.get_all_entries_string() == \
               '[<entry key="ready">3</entry>, <entry key="stuff">5</entry>, ' + \
               f'<entry key="{new_key}">{new_value}</entry>]'

    def test_can_get_specific_entry(self):
        stuff_entry = self.get_stuff_entry()
        ready_entry = self.get_ready_entry()
        none_entry = self.xml_handler.find_entry_by_key("does not exist")
        assert ready_entry.__str__() == '<entry key="ready">3</entry>'
        assert stuff_entry.__str__() == '<entry key="stuff">5</entry>'
        assert none_entry is None

    def test_can_update_entry(self):
        new_stuff_key = "new_stuff"
        new_ready_key = "new_ready"
        self.xml_handler.update_entry_key(self.get_stuff_entry(), new_stuff_key)
        self.xml_handler.update_entry_key(self.get_ready_entry(), new_ready_key)
        assert self.xml_handler.get_all_entries_string() == \
               f'[<entry key="{new_ready_key}">3</entry>, <entry key="{new_stuff_key}">5</entry>]'

    def test_can_update_value(self):
        new_stuff_value = "NEW VALUE"
        self.xml_handler.update_entry_value(self.get_stuff_entry(), new_stuff_value)
        assert self.xml_handler.get_all_entries_string() == \
               f'[<entry key="ready">3</entry>, <entry key="stuff">{new_stuff_value}</entry>]'

    def test_modifying_copy_does_not_modify_original(self):
        original_entries = self.xml_handler.get_all_entries_string()
        copy = self.xml_handler.copy_first_entry()
        self.xml_handler.update_entry_value(copy, "DUMMY")
        self.xml_handler.update_entry_key(copy, "DUMMY")
        assert self.xml_handler.get_all_entries_string() == original_entries

    def test_end_to_end(self):
        expected_final_content = \
            '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE properties SYSTEM ' \
            '"http://java.sun.com/dtd/properties.dtd">\n<properties>\n<comment> Made with care! ' \
            '</comment>\n<entry key="ready-updated-key">3</entry>\n<entry ' \
            'key="stuff">new-stuff</entry>\n<entry ' \
            'key="new_key">10</entry></properties>'
        self.xml_handler.add_new_entry(key="new_key", value="10")
        self.xml_handler.update_entry_key(self.get_ready_entry(), "ready-updated-key")
        self.xml_handler.update_entry_value(self.get_stuff_entry(), "new-stuff")
        self.assertEqual(self.xml_handler.get_content_string(), expected_final_content)

    def test_can_get_entries_dict(self):
        self.assertEqual(self.xml_handler.get_entries_dict(), {"ready": "3", "stuff": "5"})

    def test_does_entry_exist(self):
        self.assertFalse(self.xml_handler.does_entry_exist("does not exist"))
        self.assertTrue(self.xml_handler.does_entry_exist("ready"))

    def test_remove_entry(self):
        self.xml_handler.remove_entry(self.get_stuff_entry())
        assert self.xml_handler.get_all_entries_string() == '[<entry key="ready">3</entry>]'
        self.xml_handler.remove_entry(self.get_ready_entry())
        assert self.xml_handler.get_entries_count() == 0

    def test_remove_all_entries(self):
        self.xml_handler.remove_all_entries()
        assert self.xml_handler.get_entries_count() == 0

    def test_empty_xml(self):
        with self.assertRaises(ValueError) as raised_exception:
            self.xml_handler.set_xml("")

        assert raised_exception.exception.args[0] == "Malformed XML"

    def test_generate_xml_from_dict(self):
        handler = XmlHandler()
        handler.set_entries_from_dict({"first": "1", "second": "2"})
        self.assertEqual('[<entry key="first">1</entry>, <entry key="second">2</entry>]',
                         handler.get_all_entries().__str__())

    def test_fill_entries_from_dict(self):
        self.xml_handler.set_entries_from_dict({"first": "1", "second": "2"})
        self.assertEqual(self.xml_handler.get_all_entries_string(), '[<entry key="first">1</entry>, <entry key="second">2</entry>]')

    def test_update_xml_from_dict(self):
        self.xml_handler.update_entries_from_dict({"ready": "ready-new", "new": "new-value"})
        self.assertEqual(self.xml_handler.get_all_entries_string(), '[<entry key="ready">ready-new</entry>, <entry key="stuff">5</entry>, <entry key="new">new-value</entry>]')


    def get_ready_entry(self):
        return self.xml_handler.find_entry_by_key("ready")

    def get_stuff_entry(self):
        return self.xml_handler.find_entry_by_key("stuff")

