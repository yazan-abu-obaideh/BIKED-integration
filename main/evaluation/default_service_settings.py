from typing import List

from main.evaluation.request_processor_settings import RequestProcessorSettings


class DefaultAdapterSettings(RequestProcessorSettings):

    def get_label_replacements(self):
        labels_inverted = ["Sim 1 Safety Factor",
                           "Sim 3 Safety Factor"]
        labels_magnitude = ['Sim 1 Dropout X Disp.', 'Sim 1 Dropout Y Disp.', 'Sim 1 Bottom Bracket X Disp.',
                            'Sim 1 Bottom Bracket Y Disp.', 'Sim 2 Bottom Bracket Z Disp.',
                            'Sim 3 Bottom Bracket Y Disp.',
                            'Sim 3 Bottom Bracket X Rot.', 'Model Mass']
        label_replacements = {label: label + " (Inverted)" for label in labels_inverted}
        label_replacements.update({label: label + " Magnitude" for label in labels_magnitude})
        return label_replacements

    def get_expected_input_keys(self) -> list:
        # warn users when the supplied bikecad file has no materials field OR whenever the material value is not
        # in steel, alum, titanium
        return ['Material=Steel', 'Material=Aluminum', 'Material=Titanium',
                'SSB_Include', 'CSB_Include', 'CS Length', 'BB Drop',
                'Stack', 'SS E', 'ST Angle', 'BB OD', 'TT OD', 'HT OD',
                'DT OD', 'CS OD', 'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX',
                'HT UX', 'HT Angle', 'HT Length', 'ST Length', 'BB Length',
                'Dropout Offset', 'SSB OD', 'CSB OD', 'SSB Offset', 'CSB Offset',
                'SS Z', 'SS Thickness', 'CS Thickness', 'TT Thickness', 'BB Thickness',
                'HT Thickness', 'ST Thickness', 'DT Thickness', 'DT Length']

    def get_bikeCad_to_model_map(self) -> dict:
        # noinspection SpellCheckingInspection
        return {'CS textfield': 'CS Length', 'BB textfield': 'BB Drop', 'Stack': 'Stack',
                'Head angle': 'HT Angle', 'Head tube length textfield': 'HT Length',
                'Seat stay junction': 'SS E', 'Seat angle': 'ST Angle', 'DT Length': 'DT Length',
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

    def keys_whose_presence_indicates_their_value(self) -> List[str]:
        return ["CSB_Include", "SSB_Include"]

    def get_required_parameters(self) -> List[str]:
        return []

    def millimeters_to_meters(self):
        return ['CS Length', 'BB Drop', 'Stack', 'SS E', 'BB OD', 'TT OD', 'HT OD', 'DT OD',
                'CS OD', 'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX', 'HT UX', 'HT Length',
                'ST Length', 'BB Length', 'Dropout Offset', 'SSB OD', 'CSB OD', 'SSB Offset',
                'CSB Offset', 'SS Z', 'SS Thickness', 'CS Thickness', 'TT Thickness',
                'BB Thickness', 'HT Thickness', 'ST Thickness', 'DT Thickness', 'DT Length']
