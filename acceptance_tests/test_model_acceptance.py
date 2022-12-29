import enum
import unittest

from main.evaluation.evaluation_service import DefaultAdapterSettings, EvaluationService

#         self.expected_output = {'Model Mass Magnitude': 3.189100876474357,
#                                 'Sim 1 Bottom Bracket Y Disp. Magnitude': 0.012939156170363236,
#                                 'Sim 1 Dropout X Disp. Magnitude': 0.011111431121145088,
#                                 'Sim 1 Bottom Bracket X Disp. Magnitude': 0.012183772767391373,
#                                 'Sim 1 Dropout Y Disp. Magnitude': 0.021787148423259715,
#                                 'Sim 2 Bottom Bracket Z Disp. Magnitude': 0.0023485019730819755,
#                                 'Sim 3 Bottom Bracket X Rot. Magnitude': 0.0063891630717543306,
#                                 'Sim 3 Bottom Bracket Y Disp. Magnitude': 0.01666142336216584,
#                                 'Sim 1 Safety Factor (Inverted)': 0.542653611374427,
#                                 'Sim 3 Safety Factor (Inverted)': 0.6966032103094124}
#         return ['Material=Steel', 'Material=Aluminum', 'Material=Titanium',
#                 'SSB_Include', 'CSB_Include', 'CS Length', 'BB Drop',
#                 'Stack', 'SS E', 'ST Angle', 'BB OD', 'TT OD', 'HT OD',
#                 'DT OD', 'CS OD', 'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX',
#                 'HT UX', 'HT Angle', 'HT Length', 'ST Length', 'BB Length',
#                 'Dropout Offset', 'SSB OD', 'CSB OD', 'SSB Offset', 'CSB Offset',
#                 'SS Z', 'SS Thickness', 'CS Thickness', 'TT Thickness', 'BB Thickness',
#                 'HT Thickness', 'ST Thickness', 'DT Thickness', 'DT Length']

SIM_1_DEFLECTIONS = ['Sim 1 Bottom Bracket Y Disp. Magnitude',
                     'Sim 1 Dropout X Disp. Magnitude',
                     'Sim 1 Bottom Bracket X Disp. Magnitude',
                     'Sim 1 Dropout Y Disp. Magnitude']
SIM_2_DEFLECTIONS = ['Sim 2 Bottom Bracket Z Disp. Magnitude']
SIM_3_DEFLECTIONS = ['Sim 3 Bottom Bracket X Rot. Magnitude',
                     'Sim 3 Bottom Bracket Y Disp. Magnitude']
DEFLECTIONS = SIM_1_DEFLECTIONS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS

DIAMETERS = ['BB OD', 'TT OD', 'HT OD', 'DT OD', 'CS OD', 'SS OD', 'ST OD', 'SSB OD', 'CSB OD']
THICKNESS = ['SS Thickness', 'CS Thickness', 'TT Thickness', 'BB Thickness', 'HT Thickness', 'ST Thickness',
             'DT Thickness']
SAFETY_INVERTED = ['Sim 1 Safety Factor (Inverted)', 'Sim 3 Safety Factor (Inverted)']
MODEL_MASS = ['Model Mass Magnitude']

CHAIN_STAY_BRIDGE = ['CSB_Include']
SEAT_STAY_BRIDGE = ['SSB_Include']

PROPORTIONAL = {
    DIAMETERS: [MODEL_MASS]
}

INVERSELY_PROPORTIONAL = {
    DIAMETERS: [SAFETY_INVERTED, SIM_2_DEFLECTIONS, SIM_3_DEFLECTIONS],
    CHAIN_STAY_BRIDGE + SEAT_STAY_BRIDGE:
        SIM_2_DEFLECTIONS + ['Sim 3 Bottom Bracket X Rot. Magnitude']
}


class ModelAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EvaluationService()
