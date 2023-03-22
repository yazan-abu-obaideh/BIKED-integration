class RequestValidator:
    def throw_if_empty(self, request: dict, exception_message: str):
        if len(request) == 0:
            raise ValueError(exception_message)

    def throw_if_does_not_contain(self, request: dict, required_parameters: list):
        missing_parameters = self.__find_missing_parameters(request, required_parameters)
        if missing_parameters:
            raise ValueError(f"Required parameters {missing_parameters} missing")

    def __find_missing_parameters(self, request: dict, required_parameters: list) -> list:
        missing_parameters = []
        for parameter in required_parameters:
            if parameter not in request.keys():
                missing_parameters.append(parameter)
        return missing_parameters
