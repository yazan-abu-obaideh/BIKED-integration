from production.xml_handler import XmlHandler

DEFAULT_VALUE = 0


class RequestAdapter:
    def __init__(self):
        self.xml_handler = XmlHandler()
        self.map = {'CS textfield': 'CS Length', 'BB textfield': 'BB Drop', 'Stack': 'Stack',
                    'Head angle': 'HT Angle', 'Head tube length textfield': 'HT Length',
                    'Seat stay junction0': 'SS E', 'Seat angle': 'ST Angle', 'DT Length': 'DT Length',
                    'Seat tube length': 'ST Length', 'BB diameter': 'BB OD', 'ttd': 'TT OD',
                    'Head tube diameter': 'HT OD', 'dtd': 'DT OD', 'csd': 'CS OD', 'ssd': 'SS OD',
                    'Seat tube diameter': 'ST OD', 'Wall thickness Bottom Bracket': 'BB Thickness',
                    'Wall thickness Top tube': 'TT Thickness', 'Wall thickness Head tube': 'HT Thickness',
                    'Wall thickness Down tube': 'DT Thickness', 'Wall thickness Chain stay': 'CS Thickness',
                    'Wall thickness Seat stay': 'SS Thickness', 'Wall thickness Seat tube': 'ST Thickness',
                    'BB length': 'BB Length', 'Chain stay position on BB': 'CS F', 'SSTopZOFFSET': 'SS Z',
                    'Head tube upper extension2': 'HT UX', 'Seat tube extension2': 'ST UX',
                    'Head tube lower extension2': 'HT LX', 'SEATSTAYbrdgshift': 'SSB Offset',
                    'CHAINSTAYbrdgshift': 'CSB Offset', 'Dropout spacing': 'Dropout Offset',
                    'CHAINSTAYbrdgCheck': 'CSB_Include', 'SEATSTAYbrdgCheck': 'SSB_Include',
                    'SEATSTAYbrdgdia1': 'SSB OD', 'CHAINSTAYbrdgdia1': 'CSB OD'}

    def convert(self, raw_xml: str) -> dict:
        self.xml_handler.set_xml(raw_xml)

        bikeCad_file_entries = self.xml_handler.get_entries_dict()
        result_dict = {self.map.get(key): self.get_float_if_float(value) for
                       key, value in bikeCad_file_entries.items() if key in self.map.keys()}

        result_dict["Material=Steel"] = True
        result_dict["Material=Titanium"] = False
        result_dict["Material=Aluminum"] = False

        if " CSB_Include" not in result_dict:
            result_dict[" CSB_Include"] = "false"
        if " SSB_Include" not in result_dict:
            result_dict[" SSB_Include"] = "false"

        if result_dict[" CSB_Include"] == "false":
            result_dict[" CSB_OD"] = 0.017759
            result_dict[" CSB_Include"] = 0
        else:
            result_dict[" CSB_Include"] = 0
        if result_dict[" SSB_Include"] == "false":
            result_dict[" SSB_OD"] = 0.015849
            result_dict[" SSB_Include"] = 0
        else:
            result_dict[" SSB_Include"] = 1

        result_dict["HT Thickness"] = 2
        result_dict["BB Thickness"] = 2

        return result_dict

    def get_float_if_float(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()
