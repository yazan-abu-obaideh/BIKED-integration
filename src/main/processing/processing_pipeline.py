class ProcessingPipeline:
    def __init__(self, steps):
        self.steps = steps

    def process(self, request):
        for function in self.steps:
            request = function(request)
        return request
