from main.xml_handler import XmlHandler
from main.request_adapter.request_adapter_settings import RequestAdapterSettings
import numpy as np


class RequestAdapter:
    def __init__(self, settings: RequestAdapterSettings):
        self.xml_handler = XmlHandler()
        self.settings = settings

    def convert_xml(self, raw_xml: str) -> dict:
        self.set_xml_or_throw(raw_xml)
        bikeCad_file_entries = self.xml_handler.get_entries_dict()
        return self.convert_dict(bikeCad_file_entries)

    def set_xml_or_throw(self, raw_xml):
        try:
            self.xml_handler.set_xml(raw_xml)
        except ValueError:
            raise ValueError("Invalid BikeCAD file")

    def convert_dict(self, bikeCad_file_entries):
        result_dict = self.parse_values(bikeCad_file_entries)
        result_dict = self.calculate_composite_values(result_dict)
        result_dict = self.map_to_model_input(result_dict)
        self.handle_special_behavior(bikeCad_file_entries, result_dict)
        self.fill_default(result_dict)
        self.convert_units(result_dict)
        return result_dict

    def map_to_model_input(self, bikeCad_file_entries):
        result_dict = {}
        for key, value in bikeCad_file_entries.items():
            model_key = self.settings.bikeCad_to_model_map().get(key, key)
            if self.valid_model_key(model_key):
                result_dict[model_key] = value
        return result_dict

    def valid_model_key(self, model_key):
        return model_key in self.settings.default_values().keys()

    def handle_special_behavior(self, bikeCad_file_entries, result_dict):
        self.one_hot_encode(result_dict, bikeCad_file_entries["MATERIAL"])
        self.handle_keys_whose_presence_indicates_their_value(result_dict)
        self.handle_ramifications(result_dict)

    def one_hot_encode(self, result_dict, materials_entry: str):
        result_dict[f"Material={materials_entry.lower().title()}"] = 1

    def handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in self.settings.keys_whose_presence_indicates_their_value():
            # TODO: ask Lyle whether it's a bug or a feature that CSB_Include is
            #  assigned to 0 in both the IF and ELSE clauses
            result_dict[key] = int(key in result_dict)

    def handle_ramifications(self, result_dict):
        # TODO: check whether this should be done before or after scaling
        if result_dict["CSB_Include"] == 0:
            result_dict["CSB OD"] = 0.017759
        if result_dict["SSB_Include"] == 0:
            result_dict["SSB OD"] = 0.015849

    def fill_default(self, result_dict):
        for key, value in self.settings.default_values().items():
            if key not in result_dict:
                result_dict[key] = value

    def parse_values(self, result_dict):
        return {key: self.get_float_or_strip(value) for key, value in result_dict.items()}

    def get_float_or_strip(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()

    def convert_units(self, result_dict):
        for key, divider in self.settings.unit_conversion_division_dict().items():
            result_dict[key] = result_dict[key]/divider

    def calculate_composite_values(self, bikeCad_file_entries):
        #             BBD=df.at[idx, "BB textfield"]
        bbd = bikeCad_file_entries['BB textfield']
        #
        #             FCD=df.at[idx, "FCD textfield"]
        fcd = bikeCad_file_entries['FCD textfield']
        #
        #             FTY=BBD
        fty = bbd
        #
        #             FTX=np.sqrt(FTY**2+FCD**2)
        ftx = np.sqrt(fty**2 + fcd ** 2)
        #
        #             x=df.at[idx, "FORK0R"]
        x = bikeCad_file_entries.get('FORKOR', 0)
        #
        #             fkl=df.at[idx, "FORK0L"]
        fkl = bikeCad_file_entries['FORK0L']
        #
        #             htlx=df.at[idx, "Head tube lower extension2"]
        htlx = bikeCad_file_entries['Head tube lower extension2']
        #
        #             lsth=df.at[idx, "Lower stack height"]
        lsth = bikeCad_file_entries.get('lower stack height', 0)
        #
        #             y=fkl+htlx+lsth
        y = fkl + htlx + lsth
        #
        #             ha=df.at[idx, "Head angle"]*np.pi/180
        ha = bikeCad_file_entries['Head angle'] * np.pi/180
        #
        #             dtx=FTX-y*np.cos(ha)-x*np.sin(ha)
        dtx = ftx - y * np.cos(ha) - x * np.sin(ha)
        #
        #             dty=FTY+y*np.sin(ha)+x*np.cos(ha)
        dty = fty + y * np.sin(ha) + x * np.cos(ha)
        #
        #             df.at[idx, "DT Length"]=np.sqrt(dtx**2+dty**2)
        bikeCad_file_entries['DT Length'] = np.sqrt(dtx ** 2 + dty ** 2)
        #             csbd=df.at[idx, "Chain stay back diameter"]
        csbd = bikeCad_file_entries['Chain stay back diameter']
        #
        #             csvd=df.at[idx, "Chain stay vertical diameter"]
        csvd = bikeCad_file_entries['Chain stay vertical diameter']
        #
        #             csd=(csbd+csvd)/2
        csd = (csbd + csvd)/2
        #
        #             df.at[idx, "csd"]=csd
        bikeCad_file_entries['csd'] = csd
        #             ssbd=df.at[idx, "Seat stay bottom diameter"]
        ssbd = bikeCad_file_entries['Seat stay bottom diameter']
        #             sshr=df.at[idx, "SEATSTAY_HR"]
        sshr = bikeCad_file_entries["SEATSTAY_HR"]
        #             ssd=(ssbd+sshr)/2
        ssd = (ssbd + sshr)/2
        #             df.at[idx, "ssd"]=ssd
        bikeCad_file_entries['ssd'] = ssd
        #             ttrd=df.at[idx, "Top tube rear diameter"]
        ttrd = bikeCad_file_entries.get('Top tube rear diameter', 0)
        #             ttrd2=df.at[idx, "Top tube rear dia2"]
        ttrd2 = bikeCad_file_entries.get("Top tube rear dia2", 0)
        #             ttfd=df.at[idx, "Top tube front diameter"]
        ttfd = bikeCad_file_entries['Top tube front diameter']
        #             ttfd2=df.at[idx, "Top tube front dia2"]
        ttfd2 = bikeCad_file_entries.get("Top tube front dia2", 0)
        #             ttd=(ttrd+ttrd2+ttfd+ttfd2)/4
        ttd = (ttrd + ttrd2 + ttfd ++ ttfd2) / 4
        #             df.at[idx, "ttd"]=ttd
        bikeCad_file_entries['ttd'] = ttd
        #             dtrd=df.at[idx, "Down tube rear diameter"]
        #             dtrd2=df.at[idx, "Down tube rear dia2"]
        #             dtfd=df.at[idx, "Down tube front diameter"]
        #             dtfd2=df.at[idx, "Down tube front dia2"]
        dtrd, dtrd2, dtfd, dtfd2 = bikeCad_file_entries['Down tube rear diameter'], bikeCad_file_entries.get('Down tube rear dia2', 0), \
            bikeCad_file_entries['Down tube front diameter'], bikeCad_file_entries.get('Down tube front dia2', 0)
        #             dtd=(dtrd+dtrd2+dtfd+dtfd2)/4
        #             df.at[idx, "dtd"]=dtd
        dtd = (dtrd + dtrd2 + dtfd + dtfd2) / 4
        bikeCad_file_entries['dtd'] = dtd
        #             df.at[idx, "Wall thickness Bottom Bracket"]=2.0
        #             df.at[idx, "Wall thickness Head tube"]=1.1
        bikeCad_file_entries['Wall thickness Bottom Bracket'] = 2.0
        bikeCad_file_entries['Wall thickness Head tube'] = 1.1
        return bikeCad_file_entries
