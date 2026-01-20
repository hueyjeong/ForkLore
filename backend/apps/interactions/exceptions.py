from rest_framework import status

from common.exceptions import BusinessException


class PaymentFailedException(BusinessException):
    """Exception raised when payment processing fails."""

    def __init__(
        self, message: str = "결제 처리에 실패했습니다.", details: dict | None = None
    ) -> None:
        """
        Initialize the PaymentFailedException with a message and optional contextual details and set the HTTP 400 Bad Request status.
        
        Parameters:
            message (str): Human-readable error message shown for the failure. Defaults to "결제 처리에 실패했습니다.".
            details (dict | None): Optional dictionary with additional context about the payment failure; stored on the instance as `details`.
        """
        self.details = details
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)