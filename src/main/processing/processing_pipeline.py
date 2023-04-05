class ProcessingPipeline:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def process(self, request):
        for function in self.pipeline:
            request = function(request)
        return request
