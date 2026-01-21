from rest_framework import status

from common.exceptions import BusinessException


class PaymentFailedException(BusinessException):
    """Exception raised when payment processing fails."""

    def __init__(
        self, message: str = "결제 처리에 실패했습니다.", details: dict | None = None
    ) -> None:
        self.details = details
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
