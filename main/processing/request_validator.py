class RequestValidator:
    def throw_if_empty(self, request: dict, exception_message: str):
        if len(request) == 0:
            raise ValueError(exception_message)

    def throw_if_does_not_contain(self, request: dict, required_parameters: list, message: str):
        for parameter in required_parameters:
            if parameter not in request.keys():
                raise ValueError(message)
