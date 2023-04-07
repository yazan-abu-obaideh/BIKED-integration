from service.main.processing.scaling_filter import ScalingFilter
from service.main.processing.processing_pipeline import ProcessingPipeline


class ModelResponseProcessor:
    def __init__(self, response_scaler: ScalingFilter):
        self._response_scaler = response_scaler
        self._model_input_to_validated_response_pipeline = ProcessingPipeline(steps=[
            self._response_scaler.unscale,
            self._ensure_magnitude
        ])

    def map_to_validated_response(self, model_output):
        return self._model_input_to_validated_response_pipeline.process(model_output)

    def _ensure_magnitude(self, scaled_result):
        return {key: abs(value) for key, value in scaled_result.items()}
