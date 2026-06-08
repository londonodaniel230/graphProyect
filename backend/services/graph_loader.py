import json
from typing import Any, Dict, Optional

from ..errors import ValidationError
from ..validators import GraphValidator


# Loads graph data from various payload formats (JSON, bytes, dict) and validates it.
# Returns a validated Graph object ready for route optimization and trip planning.
class GraphLoader:
    # Loads and validates graph data from various payload formats.
    def __init__(self, validator: Optional[GraphValidator] = None) -> None:
        self._validator = validator or GraphValidator()

    def load(self, payload: Any):
        data = self._coerce_payload(payload)
        return self._validator.validate(data)

    # Parses incoming payload (JSON bytes, dict, or string) into a Python dict.
    # Handles encoding and JSON format validation.
    def _coerce_payload(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, (bytes, bytearray)):
            try:
                text = payload.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValidationError(["File must be UTF-8 encoded."]) from exc
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValidationError([f"Invalid JSON: {exc.msg}"]) from exc

        if isinstance(payload, dict):
            return payload

        if payload is None:
            raise ValidationError(["Empty JSON payload."])

        raise ValidationError(["Unsupported payload type."])
