from bs4 import BeautifulSoup


class XmlHandler:
    def __init__(self, xml: str):
        self.xml_tree = self.generate_xml_tree(xml)

    def generate_xml_tree(self, xml: str):
        return BeautifulSoup(xml, "xml")

    def get_all_entries(self):
        return self.xml_tree.find_all("entry")

    def copy_first_entry(self):
        fes = self.get_first_entry_string()
        new_tree = self.generate_xml_tree(fes)
        entry_alone = self.strip_tree_of_needless_tags(new_tree)
        return entry_alone

    def get_first_entry_string(self):
        return self.get_all_entries()[0].__str__()

    def strip_tree_of_needless_tags(self, new_tree):
        return new_tree.find_all("entry")[0]

    def add_new_entry(self, key, value):
        new_entry = self.copy_first_entry()
        new_entry["key"] = key
        new_entry.find(string="3").replace_with(value)
        self.xml_tree.find_all("properties")[0].append(new_entry)

