from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Any:
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            "success": False,
            "message": _extract_message(response.data),
            "errors": response.data if isinstance(response.data, dict) else None,
            "timestamp": timezone.now().isoformat(),
        }
        response.data = custom_response

    return response


def _extract_message(data: Any) -> str | None:
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        if "non_field_errors" in data:
            return str(data["non_field_errors"][0])
        first_key = next(iter(data), None)
        if first_key:
            value = data[first_key]
            if isinstance(value, list) and value:
                return f"{first_key}: {value[0]}"
            return f"{first_key}: {value}"
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)


class BusinessException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EntityNotFoundException(BusinessException):
    def __init__(self, entity_name: str, entity_id: Any = None) -> None:
        message = f"{entity_name}을(를) 찾을 수 없습니다."
        if entity_id:
            message = f"{entity_name}(ID: {entity_id})을(를) 찾을 수 없습니다."
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ForbiddenException(BusinessException):
    def __init__(self, message: str = "접근 권한이 없습니다.") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class UnauthorizedException(BusinessException):
    def __init__(self, message: str = "인증이 필요합니다.") -> None:
        """
        Initialize an UnauthorizedException with an optional message and set its HTTP status to 401 UNAUTHORIZED.
        
        Parameters:
            message (str): Human-readable error message; defaults to "인증이 필요합니다." and is stored as the exception message. The exception's `status_code` is set to HTTP 401 UNAUTHORIZED.
        """
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ConflictError(BusinessException):
    def __init__(self, message: str = "데이터가 변경되었습니다. 다시 시도해주세요.") -> None:
        """
        Initialize a ConflictError with a message and HTTP 409 Conflict status.
        
        Parameters:
            message (str): Human-readable error message; defaults to "데이터가 변경되었습니다. 다시 시도해주세요.".
        
        Description:
            Sets the exception's message and HTTP status code to 409 (Conflict).
        """
        super().__init__(message, status.HTTP_409_CONFLICT)