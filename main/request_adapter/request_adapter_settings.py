from abc import abstractmethod


class RequestAdapterSettings:
    @abstractmethod
    def default_values(self) -> dict:
        pass

    @abstractmethod
    def bikeCad_to_model_map(self) -> dict:
        pass

    @abstractmethod
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def raise_exception_if_missing(self) -> list:
        pass


class DefaultAdapterSettings(RequestAdapterSettings):
    def default_values(self) -> dict:
        return {'Material=Steel': 0, 'Material=Aluminum': 0, 'Material=Titanium': 0, 'SSB_Include': 0,
                'CSB_Include': 0, 'CS Length': 0, 'BB Drop': 0, 'Stack': 0, 'SS E': 0,
                'ST Angle': 0, 'BB OD': 0, 'TT OD': 0, 'HT OD': 0, 'DT OD': 0, 'CS OD': 0,
                'SS OD': 0, 'ST OD': 0, 'CS F': 0, 'HT LX': 0, 'ST UX': 0,
                'HT UX': 0, 'HT Angle': 0, 'HT Length': 0, 'ST Length': 0, 'BB Length': 0,
                'Dropout Offset': 0, 'SSB OD': 0, 'CSB OD': 0, 'SSB Offset': 0,
                'CSB Offset': 0, 'SS Z': 0, 'SS Thickness': 0, 'CS Thickness': 0,
                'TT Thickness': 0, 'BB Thickness': 2, 'HT Thickness': 2, 'ST Thickness': 0,
                'DT Thickness': 0, 'DT Length': 0}

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
