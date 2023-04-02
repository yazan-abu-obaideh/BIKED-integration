from typing import Optional


class AlgebraicParser:
    def parse(self, value: str):
        return self._parse_value(value)

    def _parse_value(self, value: str) -> Optional[float]:
        if self._is_bool(value):
            return float(value.lower() == "true")
        if self._is_float(value):
            return float(value)
        return None

    def _is_float(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _is_bool(self, value: str) -> bool:
        return value.lower() in ["true", "false"]
