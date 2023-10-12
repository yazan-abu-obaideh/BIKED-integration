from service.main.processing.scaling_filter import ScalingFilter
from service.main.processing.processing_pipeline import ProcessingPipeline


class ModelResponseProcessor:
    def __init__(self, response_scaler: ScalingFilter):
        self._response_scaler = response_scaler
        self._model_input_to_validated_response_pipeline = ProcessingPipeline(steps=[
            self._response_scaler.unscale,
        ])

    def map_to_validated_response(self, model_output: dict) -> dict:
        return self._model_input_to_validated_response_pipeline.process(model_output)
