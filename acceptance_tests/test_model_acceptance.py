import unittest
from sample_request import request
from main.evaluation.evaluation_service import EvaluationService, DefaultAdapterSettings
from acceptance_tests.robot_qa import RobotQaDepartment
from acceptance_tests.robot_qa import Relationship

SAFETY_3_INVERTED = 'Sim 3 Safety Factor (Inverted)'

SAFETY_1_INVERTED = 'Sim 1 Safety Factor (Inverted)'

SIM_1_DEFLECTIONS = ['Sim 1 Bottom Bracket Y Disp. Magnitude',
                     'Sim 1 Dropout X Disp. Magnitude',
                     'Sim 1 Bottom Bracket X Disp. Magnitude',
                     'Sim 1 Dropout Y Disp. Magnitude']
SIM_2_DEFLECTIONS = ['Sim 2 Bottom Bracket Z Disp. Magnitude']
SIM_3_DEFLECTIONS = ['Sim 3 Bottom Bracket X Rot. Magnitude',
                     'Sim 3 Bottom Bracket Y Disp. Magnitude']
DEFLECTIONS = SIM_1_DEFLECTIONS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS

DIAMETER_PARAMETERS = ['BB OD', 'TT OD', 'HT OD', 'DT OD', 'CS OD', 'SS OD', 'ST OD', 'SSB OD', 'CSB OD']
THICKNESS_PARAMETERS = ['SS Thickness', 'CS Thickness', 'TT Thickness', 'BB Thickness', 'HT Thickness', 'ST Thickness',
                        'DT Thickness']
DOWN_TUBE_LENGTH_PARAMETERS = ['DT Length']
SAFETY_INVERTED_PARAMETERS = [SAFETY_1_INVERTED, SAFETY_3_INVERTED]
MODEL_MASS_PARAMETERS = ['Model Mass Magnitude']

CHAIN_STAY_BRIDGE = ['CSB_Include']
SEAT_STAY_BRIDGE = ['SSB_Include']
STAY_BRIDGES = CHAIN_STAY_BRIDGE + SEAT_STAY_BRIDGE

service = EvaluationService()

qa = RobotQaDepartment(processing_function=service.predict_from_dict)

SETTINGS = DefaultAdapterSettings()
reversed_map = {value: key for key, value in SETTINGS.bikeCad_to_model_map().items()}
def build_relationship(request_parameters, response_parameters):
    return Relationship(request_parameters=[reversed_map[key] for key in request_parameters], affected_values=response_parameters)


qa.add_proportional_relationship(build_relationship(DIAMETER_PARAMETERS, MODEL_MASS_PARAMETERS))
qa.add_proportional_relationship(build_relationship(DOWN_TUBE_LENGTH_PARAMETERS, MODEL_MASS_PARAMETERS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS))
qa.add_proportional_relationship(build_relationship(STAY_BRIDGES, [SAFETY_3_INVERTED]))

qa.add_inverse_relationship(build_relationship(DIAMETER_PARAMETERS, SAFETY_INVERTED_PARAMETERS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS))
qa.add_inverse_relationship(build_relationship(STAY_BRIDGES, SIM_2_DEFLECTIONS + ['Sim 3 Bottom Bracket X Rot. Magnitude']))



class ModelAcceptanceTest(unittest.TestCase):
    def test_acceptance(self):
        qa.set_request(request)
        qa.execute_assertions()
        print(qa.successful_executions)
        print(qa.reported_errors)

