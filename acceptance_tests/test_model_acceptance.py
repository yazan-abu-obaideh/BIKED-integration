import unittest
from sample_request import request
from main.evaluation.evaluation_service import EvaluationService
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

qa.add_proportional_relationship(
    Relationship(request_parameters=DIAMETER_PARAMETERS, affected_values=MODEL_MASS_PARAMETERS))
qa.add_proportional_relationship(
    Relationship(request_parameters=DOWN_TUBE_LENGTH_PARAMETERS,
                 affected_values=MODEL_MASS_PARAMETERS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS))
qa.add_proportional_relationship(
    Relationship(request_parameters=STAY_BRIDGES, affected_values=[SAFETY_3_INVERTED]))

qa.add_inverse_relationship(Relationship(DIAMETER_PARAMETERS, SAFETY_INVERTED_PARAMETERS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS))
qa.add_inverse_relationship(Relationship(STAY_BRIDGES, SIM_2_DEFLECTIONS + ['Sim 3 Bottom Bracket X Rot. Magnitude']))



class ModelAcceptanceTest(unittest.TestCase):
    def test_acceptance(self):
        qa.set_request(request)
        qa.execute_assertions()
        print(qa.successful_executions)
        print(qa.reported_errors)

