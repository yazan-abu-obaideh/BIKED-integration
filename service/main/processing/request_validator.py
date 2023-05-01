class RequestValidator:
    def raise_if_empty(self, request: dict, exception_message: str):
        if len(request) == 0:
            raise ValueError(exception_message)

    def raise_if_does_not_contain(self, request: dict, required_parameters: list):
        missing_parameters = self._find_missing_parameters(request, required_parameters)
        if missing_parameters:
            raise ValueError(f"Required parameters {missing_parameters} missing")

    def _find_missing_parameters(self, request: dict, required_parameters: list) -> list:
        actual_params = request.keys()
        return [param for param in required_parameters if param not in actual_params]
