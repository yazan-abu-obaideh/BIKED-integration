class ProcessingPipeline:
    def __init__(self, steps):
        self.pipeline = steps

    def process(self, request):
        for function in self.pipeline:
            request = function(request)
        return request
