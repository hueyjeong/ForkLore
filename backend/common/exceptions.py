from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


def custom_exception_handler(exc, context):
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


def _extract_message(data):
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
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EntityNotFoundException(BusinessException):
    def __init__(self, entity_name, entity_id=None):
        message = f"{entity_name}을(를) 찾을 수 없습니다."
        if entity_id:
            message = f"{entity_name}(ID: {entity_id})을(를) 찾을 수 없습니다."
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ForbiddenException(BusinessException):
    def __init__(self, message="접근 권한이 없습니다."):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class UnauthorizedException(BusinessException):
    def __init__(self, message="인증이 필요합니다."):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
