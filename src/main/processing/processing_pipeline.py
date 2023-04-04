from typing import List, Callable, TypeVar

T = TypeVar('T')


class ProcessingPipeline:
    def __init__(self, pipeline: List[Callable[[T], T]]):
        self.pipeline = pipeline

    def process(self, request: T) -> T:
        for function in self.pipeline:
            request = function(request)
        return request
