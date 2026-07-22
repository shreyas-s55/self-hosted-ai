"""OpenAI-compatible API errors."""

from fastapi import HTTPException


class OpenAIError(HTTPException):
    """Base OpenAI-compatible HTTP error."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        error_type: str = "invalid_request_error",
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "message": message,
                    "type": error_type,
                    "code": code,
                }
            },
        )


class ModelNotFoundError(OpenAIError):
    """Raised when a requested deployment does not exist."""

    def __init__(self, model: str):
        super().__init__(
            status_code=404,
            code="model_not_found",
            message=f'Model "{model}" does not exist.',
        )