from time import time


class XmlFiller:
    TEMPLATE = "XML_TEMPLATE.txt"
    REPLACEABLE_PORTION = "REPLACEABLE"

    def create_xml(self, **keyword_entries):
        entries = self.construct_entries_string(keyword_entries)
        xml_content = self.get_xml_content(entries)
        self.write_to_xml(self.get_xml_filename(), xml_content)

    def get_xml_content(self, entries):
        return self.get_xml_template_string().replace(self.REPLACEABLE_PORTION,
                                                      self.remove_trailing_new_line(entries))

    def construct_entries_string(self, keyword_entries: dict):
        entries = ""
        for key, value in keyword_entries.items():
            entries += self.get_entry_string(key, value)
        return entries

    def remove_trailing_new_line(self, entries):
        if entries:
            return entries[:-1]
        return entries

    def get_xml_template_string(self):
        return self.read_xml(self.TEMPLATE)

    def read_xml(self, path) -> str:
        with open(path, "r") as file:
            contents = file.read()
        return contents

    def write_to_xml(self, path, content):
        with open(path, "w") as file:
            file.write(content)

    def get_entry_string(self, key, value):
        return f"<entry key=\"{key}\">{value}</entry>\n"

    def get_xml_filename(self):
        return f"new_xml_{time()}.xml"
