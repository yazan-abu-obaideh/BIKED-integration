from production.xml_handler import XmlHandler
from production.request_adapter.settings import default_values, keys_whose_presence_indicates_their_value

DEFAULT_VALUE = 0


class RequestAdapter:
    def __init__(self):
        self.xml_handler = XmlHandler()
        # noinspection SpellCheckingInspection
        self.bikeCad_to_model_map = {'CS textfield': 'CS Length', 'BB textfield': 'BB Drop', 'Stack': 'Stack',
                                     'Head angle': 'HT Angle', 'Head tube length textfield': 'HT Length',
                                     'Seat stay junction0': 'SS E', 'Seat angle': 'ST Angle', 'DT Length': 'DT Length',
                                     'Seat tube length': 'ST Length', 'BB diameter': 'BB OD', 'ttd': 'TT OD',
                                     'Head tube diameter': 'HT OD', 'dtd': 'DT OD', 'csd': 'CS OD', 'ssd': 'SS OD',
                                     'Seat tube diameter': 'ST OD', 'Wall thickness Bottom Bracket': 'BB Thickness',
                                     'Wall thickness Top tube': 'TT Thickness',
                                     'Wall thickness Head tube': 'HT Thickness',
                                     'Wall thickness Down tube': 'DT Thickness',
                                     'Wall thickness Chain stay': 'CS Thickness',
                                     'Wall thickness Seat stay': 'SS Thickness',
                                     'Wall thickness Seat tube': 'ST Thickness',
                                     'BB length': 'BB Length', 'Chain stay position on BB': 'CS F',
                                     'SSTopZOFFSET': 'SS Z',
                                     'Head tube upper extension2': 'HT UX', 'Seat tube extension2': 'ST UX',
                                     'Head tube lower extension2': 'HT LX', 'SEATSTAYbrdgshift': 'SSB Offset',
                                     'CHAINSTAYbrdgshift': 'CSB Offset', 'Dropout spacing': 'Dropout Offset',
                                     'CHAINSTAYbrdgCheck': 'CSB_Include', 'SEATSTAYbrdgCheck': 'SSB_Include',
                                     'SEATSTAYbrdgdia1': 'SSB OD', 'CHAINSTAYbrdgdia1': 'CSB OD'}
        self.default_values = default_values

    def convert(self, raw_xml: str) -> dict:
        self.xml_handler.set_xml(raw_xml)

        bikeCad_file_entries = self.xml_handler.get_entries_dict()
        result_dict = {}

        for key, value in bikeCad_file_entries.items():
            model_key = self.bikeCad_to_model_map.get(key, key)
            if model_key in self.default_values.keys():
                result_dict[model_key] = value

        material_value = bikeCad_file_entries["MATERIAL"]

        self.handle_materials(result_dict, material_value)
        # values whose presence indicates their value:
        self.handle_keys_whose_presence_indicates_their_value(result_dict)
        result_dict["CSB_Include"] = str("CSB_Include" in result_dict).lower()

        # if "CSB_Include" not in result_dict:
        #     result_dict["CSB_Include"] = "false"
        # TODO: ask Lyle whether it's fine to have an else clause here.
        if "SSB_Include" not in result_dict:
            result_dict["SSB_Include"] = "false"

        if result_dict["CSB_Include"] == "false":
            result_dict["CSB_OD"] = 0.017759
            result_dict["CSB_Include"] = 0
        else:
            result_dict["CSB_Include"] = 0
        if result_dict["SSB_Include"] == "false":
            result_dict["SSB_OD"] = 0.015849
            result_dict["SSB_Include"] = 0
        else:
            result_dict["SSB_Include"] = 1

        return result_dict

    def handle_materials(self, result_dict, materials_entry: str):
        result_dict[f"Material={materials_entry.lower().title()}"] = 1

    def handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in keys_whose_presence_indicates_their_value:
            result_dict[key] = str(key in result_dict).lower()

    def get_float_if_float(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()
