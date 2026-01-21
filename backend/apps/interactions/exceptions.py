from rest_framework import status

from common.exceptions import BusinessException


class PaymentFailedException(BusinessException):
    """Exception raised when payment processing fails."""

    def __init__(
        self, message: str = "결제 처리에 실패했습니다.", details: dict | None = None
    ) -> None:
        """
        결제 실패를 나타내는 예외 객체를 초기화합니다.
        
        Parameters:
            message (str): 예외 메시지; 기본값은 "결제 처리에 실패했습니다."입니다.
            details (dict | None): 추가 오류 정보(예: 결제 게이트웨이 응답 등)를 담은 사전이며 인스턴스의 `details` 속성에 저장됩니다.
        
        Notes:
            이 초기화는 HTTP 상태 코드 400(Bad Request)로 예외를 구성합니다.
        """
        self.details = details
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)