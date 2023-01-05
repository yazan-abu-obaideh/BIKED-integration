import copy
import unittest


class Relationship:
    def __init__(self, request_parameters: list, affected_values: list):
        self.request_params = request_parameters
        self.affected_response_parameters = affected_values


class Attempt:
    def __init__(self):
        self.successful = False
        self.assertion = None


class RobotQaDepartment(unittest.TestCase):
    def __init__(self, processing_function):
        super().__init__()
        self.reported_errors = []
        self.processing_function = processing_function
        self.base_request = None
        self.proportional_relationships = []
        self.inverse_relationships = []

    def add_proportional_relationship(self, relationship: Relationship):
        self.proportional_relationships.append(relationship)

    def add_inverse_relationship(self, relationship: Relationship):
        self.inverse_relationships.append(relationship)

    def execute_assertions(self):
        self.__execute_for(self.proportional_relationships, self.report_assertGreater)
        self.__execute_for(self.inverse_relationships, self.report_assertLess)

    def report_assertGreater(self, a, b):
        self.report_assert(self.assertGreater, a, b)

    def report_assertLess(self, a, b):
        self.report_assert(self.assertLess, a, b)

    def report_assert(self, assertion_function, a, b):
        try:
            assertion_function(a, b)
        except AssertionError as error:
            self.reported_errors.append(error)

    def get_request(self):
        mutable_request = copy.deepcopy(self.base_request)
        return mutable_request

    def set_request(self, base_request):
        self.base_request = base_request

    def __execute_for(self, relationships: list, assertion_function: callable):
        for relationship in relationships:
            self.__process_relationship(relationship, assertion_function)

    def __process_relationship(self, relationship, assertion_function):
        for key in relationship.request_params:
            for value in relationship.affected_response_parameters:
                base_request = self.get_request()
                old_response = self.processing_function(base_request)
                base_request[key] += 1
                assertion_function(self.processing_function(base_request)[value], old_response[value])


class RobotQaTest(unittest.TestCase):

    def setUp(self) -> None:
        self.robot_qa = RobotQaDepartment(self.process)
        self.robot_qa.set_request({
            "a1": 6, "a2": 10,
            "d1": 10, "d2": 2
        })
        self.robot_qa.add_proportional_relationship(
            Relationship(request_parameters=['a1', 'a2', 'd2'], affected_values=['sum']))
        self.robot_qa.add_proportional_relationship(Relationship(['d1', 'a1'], ['division']))
        self.robot_qa.add_inverse_relationship(Relationship(['d2', 'a2'], ['division']))

    def test_base_request_constant(self):
        request = self.robot_qa.get_request()
        self.assertIsNot(request, self.robot_qa.get_request())
        self.assertEqual({
            "a1": 6, "a2": 10,
            "d1": 10, "d2": 2
        }, request)

    def test_qa_passes(self):
        self.robot_qa.execute_assertions()

    def test_qa_reports_errors(self):
        self.robot_qa.processing_function = lambda x: {"sum": x['a1'] + x['a2'] + x['d2'],
                                                       "division": (x['d2'] + x['a1']) / (x['d2'] + x['a2'])}
        self.assertEqual(len(self.robot_qa.reported_errors), 0)
        self.robot_qa.execute_assertions()
        self.assertEqual(len(self.robot_qa.reported_errors), 2)

    def request(self):
        return {
            "a1": 5, "a2": 10,
            "d1": 10, "d2": 2
        }

    def process(self, request):
        return {"sum": request['a1'] + request['a2'] + request['d2'],
                "division": (request['d1'] + request['a1']) / (request['d2'] + request['a2'])
                }
