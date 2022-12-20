from main.request_processing.request_processor_settings import RequestProcessorSettings


class Settings(RequestProcessorSettings):
    """THIS IS NOT DUPLICATION. The test settings just so happen to match the real settings because we have not done the
    requisite work on the real settings just yet."""

    def millimeters_to_meters(self):
        return ['CS F']

    def expected_input_keys(self) -> list:
        return ['Material=Steel', 'Material=Aluminum', 'Material=Titanium',
                'SSB_Include', 'CSB_Include', 'CS Length', 'BB Drop', 'Stack',
                'SS E', 'ST Angle', 'BB OD', 'TT OD', 'HT OD', 'DT OD', 'CS OD',
                'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX', 'HT UX', 'HT Angle',
                'HT Length', 'ST Length', 'BB Length', 'Dropout Offset', 'SSB OD',
                'CSB OD', 'SSB Offset', 'CSB Offset', 'SS Z', 'SS Thickness',
                'CS Thickness', 'TT Thickness', 'BB Thickness', 'HT Thickness',
                'ST Thickness', 'DT Thickness', 'DT Length']

    def bikeCad_to_model_map(self) -> dict:
        # noinspection SpellCheckingInspection
        return {'CS textfield': 'CS Length', 'BB textfield': 'BB Drop', 'Stack': 'Stack',
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

    def keys_whose_presence_indicates_their_value(self) -> list:
        return ["CSB_Include", "SSB_Include"]

    def raise_exception_if_missing(self) -> list:
        return []
