import unittest


class RobotQaDepartment(unittest.TestCase):
    class AssertableRelationship:
        def __init__(self, request_param, response_param, alteration_assertion):
            self.request_param, self.response_param, self.alteration_assertion = request_param, response_param, alteration_assertion


class RobotQaTest(unittest.TestCase):

    def request(self):
        return {
            "a1": 5, "a2": 10,
            "d1": 10, "d2": 2
        }

    def test_relationships(self):
        self.assertEqual(self.get_relationship('a1', 'sum'), "P")
        self.assertEqual(self.get_relationship('d2', 'division'), "I")

    def test_gets_proportional(self):
        request = self.request()
        old_response = self.process(request)
        request['a1'] += 1
        request['d2'] += 1
        self.assertGreater(self.process(request)['sum'], old_response['sum'])
        self.assertLess(self.process(request)['division'], old_response['division'])

    def process(self, request):
        return {"sum": request['a1'] + request['a2'] + request['d2'],
                "division": (request['d1'] + request['a1']) / (request['d2'] + request['a2'])
                }

    def get_relationship(self, param, param1):
        proportional = {
            Holder(['a1', 'a2', 'd2'], ['sum']),
            Holder(['d1', 'a1'], ['division'])
        }
        inverse = {
            Holder(['d2', 'a2'], ['division'])
        }
        for relationship in proportional:
            if param in relationship.keys and param1 in relationship.values:
                return "P"
        for relationship in inverse:
            if param in relationship.keys and param1 in relationship.values:
                return "I"


class Holder:
    def __init__(self, keys, values):
        self.keys = keys
        self.values = values
