import unittest


class Relationship:
    def __init__(self, keys: list, affected_values: list):
        self.keys = keys
        self.affected_values = affected_values


class RobotQaDepartment(unittest.TestCase):
    def __init__(self, processing_function):
        super().__init__()
        self.processing_function = processing_function
        self.proportional_relationships = []
        self.inverse_relationships = []

    def add_proportional_relationship(self, relationship: Relationship):
        self.proportional_relationships.append(relationship)

    def add_inverse_relationship(self, relationship: Relationship):
        self.inverse_relationships.append(relationship)

    def execute_assertions(self):
        self.execute_proportional(self.proportional_relationships, self.assertGreater)
        self.execute_proportional(self.inverse_relationships, self.assertLess)

    def execute_proportional(self, relationships: list, assertion_function: callable):
        for relationship in relationships:
            for key in relationship.keys:
                for value in relationship.affected_values:
                    base_request = self.request()
                    old_response = self.processing_function(base_request)
                    base_request[key] += 1
                    assertion_function(self.processing_function(base_request)[value], old_response[value])

    def request(self):
        return {
            "a1": 5, "a2": 10,
            "d1": 10, "d2": 2
        }


class RobotQaTest(unittest.TestCase):

    def setUp(self) -> None:
        self.robot_qa = RobotQaDepartment(self.process)
        self.robot_qa.add_proportional_relationship(Relationship(keys=['a1', 'a2', 'd2'], affected_values=['sum']))
        self.robot_qa.add_proportional_relationship(Relationship(['d1', 'a1'], ['division']))
        self.robot_qa.add_inverse_relationship(Relationship(['d2', 'a2'], ['division']))

    def test_request_immutable(self):
        request = self.robot_qa.request()
        self.assertIsNot(request, self.robot_qa.request())

    def test_qa(self):
        self.robot_qa.execute_assertions()

    def request(self):
        return {
            "a1": 5, "a2": 10,
            "d1": 10, "d2": 2
        }

    def process(self, request):
        return {"sum": request['a1'] + request['a2'] + request['d2'],
                "division": (request['d1'] + request['a1']) / (request['d2'] + request['a2'])
                }
