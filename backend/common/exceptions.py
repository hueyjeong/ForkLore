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
        인증이 필요한 경우 사용할 예외 인스턴스를 초기화한다. 기본 메시지는 "인증이 필요합니다."이며 HTTP 401 상태 코드로 설정한다.
        
        Parameters:
            message (str): 예외에 사용할 메시지. 기본값은 "인증이 필요합니다.".
        """
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ConflictError(BusinessException):
    def __init__(self, message: str = "데이터가 변경되었습니다. 다시 시도해주세요.") -> None:
        """
        충돌(HTTP 409) 상황을 나타내는 예외를 초기화합니다.
        
        Parameters:
            message (str): 클라이언트에 전달될 오류 메시지. 기본값은 "데이터가 변경되었습니다. 다시 시도해주세요."이며, 예외는 HTTP 409 CONFLICT 상태 코드로 설정됩니다.
        """
        super().__init__(message, status.HTTP_409_CONFLICT)