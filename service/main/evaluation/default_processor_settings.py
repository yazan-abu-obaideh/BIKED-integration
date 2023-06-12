from typing import List

from service.main.evaluation.request_processor_settings import RequestProcessorSettings


class DefaultMapperSettings(RequestProcessorSettings):
    __EXPECTED_XML_KEYS = ['FORKOR', 'dtd', 'Top tube front diameter', 'Top tube front dia2',
                           'Down tube rear diameter', 'Dropout spacing', 'Down tube front dia2',
                           'CHAINSTAYbrdgCheck', 'Wall thickness Head tube', 'FCD textfield',
                           'Down tube rear dia2', 'Chain stay position on BB', 'ttd',
                           'SEATSTAYbrdgshift', 'BB diameter', 'CHAINSTAYbrdgshift', 'Chain stay vertical diameter',
                           'Seat tube extension2', 'Wall thickness Chain stay', 'DT Length',
                           'Seat stay bottom diameter',
                           'Head tube lower extension2', 'MATERIAL', 'Seat stay junction', 'SEATSTAYbrdgdia1',
                           'CS textfield',
                           'Seat tube length', 'Down tube front diameter', 'SSTopZOFFSET', 'FORK0L',
                           'CHAINSTAYbrdgdia1',
                           'csd', 'Head tube diameter', 'Wall thickness Top tube', 'lower stack height', 'SEATSTAY_HR',
                           'ssd', 'Top tube rear dia2', 'Head tube upper extension2', 'Wall thickness Down tube',
                           'Seat angle',
                           'Head tube length textfield', 'Head angle', 'Wall thickness Seat stay',
                           'Wall thickness Seat tube',
                           'Seat tube diameter', 'BB length', 'Wall thickness Bottom Bracket',
                           'Chain stay back diameter',
                           'SEATSTAYbrdgCheck', 'Top tube rear diameter', 'Stack', 'BB textfield']
    __EXPECTED_INPUT_KEYS = ['Material=Steel', 'Material=Aluminum', 'Material=Titanium',
                             'SSB_Include', 'CSB_Include', 'CS Length', 'BB Drop',
                             'Stack', 'SS E', 'ST Angle', 'BB OD', 'TT OD', 'HT OD',
                             'DT OD', 'CS OD', 'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX',
                             'HT UX', 'HT Angle', 'HT Length', 'ST Length', 'BB Length',
                             'Dropout Offset', 'SSB OD', 'CSB OD', 'SSB Offset', 'CSB Offset',
                             'SS Z', 'SS Thickness', 'CS Thickness', 'TT Thickness', 'BB Thickness',
                             'HT Thickness', 'ST Thickness', 'DT Thickness', 'DT Length']
    __BIKECAD_TO_MODEL_MAP = {'CS textfield': 'CS Length', 'BB textfield': 'BB Drop', 'Stack': 'Stack',
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

    __KEYS_WHOSE_PRESENCE = ["CSB_Include", "SSB_Include"]
    __REQUIRED_PARAMETERS = []
    __MILLIMETERS_TO_METERS = ['CS Length', 'BB Drop', 'Stack', 'SS E', 'BB OD', 'TT OD', 'HT OD', 'DT OD',
                               'CS OD', 'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX', 'HT UX', 'HT Length',
                               'ST Length', 'BB Length', 'Dropout Offset', 'SSB OD', 'CSB OD', 'SSB Offset',
                               'CSB Offset', 'SS Z', 'SS Thickness', 'CS Thickness', 'TT Thickness',
                               'BB Thickness', 'HT Thickness', 'ST Thickness', 'DT Thickness', 'DT Length']

    def expected_xml_keys(self) -> list:
        return self.__EXPECTED_XML_KEYS

    def expected_input_keys(self) -> list:
        # warn users when the supplied bikecad file has no materials field OR whenever the material value is not
        # in steel, alum, titanium
        return self.__EXPECTED_INPUT_KEYS

    def bikeCad_to_model_map(self) -> dict:
        # noinspection SpellCheckingInspection
        return self.__BIKECAD_TO_MODEL_MAP

    def keys_whose_presence_indicates_their_value(self) -> List[str]:
        return self.__KEYS_WHOSE_PRESENCE

    def required_parameters(self) -> List[str]:
        return self.__REQUIRED_PARAMETERS

    def millimeters_to_meters(self) -> list:
        return self.__MILLIMETERS_TO_METERS
