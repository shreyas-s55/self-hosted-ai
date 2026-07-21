"""JSON log formatter."""

import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "gateway",
            "message": record.getMessage(),
        }

        if hasattr(record, "extra"):
            payload.update(record.extra)

        return json.dumps(payload)