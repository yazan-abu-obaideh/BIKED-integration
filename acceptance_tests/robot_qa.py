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
    def __init__(self, processing_function, preprocessing_function):
        super().__init__()
        self.preprocessing_function = preprocessing_function
        self.successful_executions = []
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
        return self.successful_executions, self.reported_errors

    def report_assertGreater(self, a, b):
        return self.does_pass(self.assertGreater, a, b)

    def report_assertLess(self, a, b):
        return self.does_pass(self.assertLess, a, b)

    def does_pass(self, assertion_function, a, b):
        try:
            assertion_function(a, b)
            self.log_message("passed")
            return True
        except AssertionError:
            self.log_message("failed")
            return False

    def log_message(self, result):
        print(f"Assertion RESULT".replace("RESULT", result))

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
                base_request = self.preprocessing_function(self.get_request())
                old_response = self.processing_function(base_request)
                base_request[key] = float(base_request[key]) + 1
                passed = assertion_function(self.processing_function(base_request)[value], old_response[value])
                if passed:
                    self.successful_executions.append({"request_param": key,
                                                       "response_param": value})
                else:
                    self.reported_errors.append({"request_param": key,
                                                 "response_param": value})


class RobotQaTest(unittest.TestCase):

    def setUp(self) -> None:
        self.robot_qa = RobotQaDepartment(self.process, lambda x: x)
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
        successful, errors = self.robot_qa.execute_assertions()
        self.assertEqual(len(successful), 7)
        self.assertEqual(len(errors), 0)

    def test_qa_reports_errors(self):
        self.robot_qa.processing_function = lambda x: {"sum": x['a1'] + x['a2'] + x['d2'],
                                                       "division": (x['d2'] + x['a1']) / (x['d2'] + x['a2'])}
        self.assertEqual(0, len(self.robot_qa.reported_errors))
        self.robot_qa.execute_assertions()
        self.assertEqual(5, len(self.robot_qa.successful_executions))
        self.assertEqual(2, len(self.robot_qa.reported_errors))

    def request(self):
        return {
            "a1": 5, "a2": 10,
            "d1": 10, "d2": 2
        }

    def process(self, request):
        return {"sum": request['a1'] + request['a2'] + request['d2'],
                "division": (request['d1'] + request['a1']) / (request['d2'] + request['a2'])
                }
