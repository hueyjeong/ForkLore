import base64
from typing import Any, Protocol, runtime_checkable

import requests
from django.conf import settings

from apps.interactions.exceptions import PaymentFailedException


@runtime_checkable
class PaymentGatewayAdapter(Protocol):
    """Protocol for payment gateway adapters."""

    def approve(self, payment_key: str, order_id: str, amount: int) -> dict[str, Any]:
        """
        결제 승인 요청을 전송하고 결제 게이트웨이의 응답을 반환합니다.
        
        Parameters:
            payment_key (str): 게이트웨이에서 발급한 결제 키.
            order_id (str): 애플리케이션에서 생성한 주문 ID.
            amount (int): 결제 금액(원 단위).
        
        Returns:
            dict: 결제 게이트웨이가 반환한 응답(JSON)을 파싱한 딕셔너리.
        
        Raises:
            PaymentFailedException: 결제 승인 처리 중 오류가 발생하면 상세 정보와 함께 발생합니다.
        """
        ...

    def cancel(self, payment_key: str, cancel_reason: str) -> dict[str, Any]:
        """
        결제 취소를 요청하고 결제 게이트웨이의 응답을 반환합니다.
        
        Parameters:
            payment_key (str): 취소할 결제를 식별하는 결제 키.
            cancel_reason (str): 취소 사유(사용자 또는 시스템에서 제공하는 설명).
        
        Returns:
            dict: 결제 게이트웨이가 반환한 응답(JSON)을 파싱한 딕셔너리.
        
        Raises:
            PaymentFailedException: 결제 취소 요청이 실패한 경우(게이트웨이 오류 응답 포함).
        """
        ...


class TossPaymentAdapter:
    """Adapter for Toss Payments API."""

    BASE_URL = "https://api.tosspayments.com/v1/payments"

    def __init__(self) -> None:
        """
        TossPaymentAdapter를 초기화하고 설정에서 TOSS_PAYMENTS_SECRET_KEY 값을 읽어 인스턴스에 저장합니다.
        
        self.secret_key에는 설정에 정의된 비밀 키 값이 할당되며, 설정에 값이 없으면 None이 됩니다.
        """
        self.secret_key = settings.TOSS_PAYMENTS_SECRET_KEY

    def _get_headers(self) -> dict[str, str]:
        """
        Toss Payments API에 사용할 HTTP 요청 헤더를 생성한다.
        
        비밀 키가 설정되어 있지 않으면 빈 사전을 반환한다.
        
        Returns:
            dict[str, str]: Authorization 및 Content-Type 헤더를 포함한 헤더 사전. 비밀 키 미설정 시 빈 딕셔너리.
        """
        if not self.secret_key:
            return {}

        # Toss Payments requires Basic Auth with Secret Key and empty password
        # Format: "Basic base64(SECRET_KEY:)"
        secret_key_bytes = f"{self.secret_key}:".encode()
        encoded_key = base64.b64encode(secret_key_bytes).decode("utf-8")

        return {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json",
        }

    def _is_mock_mode(self) -> bool:
        """
        모의 결제(mock) 모드를 사용할지를 결정한다.
        
        설정값 `TOSS_PAYMENTS_USE_MOCK`이 명시적으로 정의되어 있으면 그 값을 우선 사용하고, 정의되어 있지 않으면 비밀 키가 없을 때 모의 모드를 활성화한다.
        
        Returns:
            `True`이면 모의 결제 모드를 사용하고, `False`이면 실제 결제 모드를 사용한다.
        """
        # Prefer an explicit setting to control mock mode. If the setting is
        # not defined, fall back to treating a missing secret key as mock mode.
        use_mock = getattr(settings, "TOSS_PAYMENTS_USE_MOCK", None)
        if use_mock is not None:
            return bool(use_mock)

        return not self.secret_key

    def approve(self, payment_key: str, order_id: str, amount: int) -> dict[str, Any]:
        """
        Toss Payments API로 결제를 승인하고 승인 결과 응답을 반환합니다.
        
        Parameters:
            payment_key (str): 결제 식별 키.
            order_id (str): 주문 식별자.
            amount (int): 승인할 금액(원 단위).
        
        Returns:
            dict[str, Any]: 결제 승인에 대한 응답 JSON(실제 API 응답 또는 모의 응답).
        
        Raises:
            PaymentFailedException: 네트워크 오류나 API 오류로 결제 승인에 실패한 경우. 오류 메시지는 API 응답의 `message`를 사용하거나 기본 메시지를 제공합니다.
        """
        if self._is_mock_mode():
            return {
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount,
                "status": "DONE",
                "method": "카드",
                "totalAmount": amount,
                "approvedAt": "2024-01-01T00:00:00+09:00",
                "mock": True,
            }

        url = f"{self.BASE_URL}/confirm"
        data = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount,
        }

        try:
            response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = "Payment approval failed"
            details = None

            if hasattr(e, "response") and e.response is not None:
                try:
                    details = e.response.json()
                    if "message" in details:
                        error_msg = details["message"]
                except ValueError:
                    # If the error response body is not valid JSON, ignore parsing failures
                    # and fall back to the default error message and details.
                    pass

            raise PaymentFailedException(message=error_msg, details=details) from e

    def cancel(self, payment_key: str, cancel_reason: str) -> dict[str, Any]:
        """
        Toss Payments에 결제 취소를 요청한다.
        
        취소가 모드(mock)일 경우에는 즉시 모의 취소 응답을 반환한다. 실제 요청 실행 중 네트워크 또는 API 오류가 발생하면 `PaymentFailedException`을 발생시키며, 가능하면 API가 반환한 오류 메시지와 상세 JSON을 함께 포함한다.
        
        Returns:
            dict[str, Any]: 결제 취소에 대한 응답 JSON을 파싱한 딕셔너리
        
        Raises:
            PaymentFailedException: 취소 요청이 실패했을 때 (가능하면 `message`와 `details`에 API 오류 정보를 포함)
        """
        if self._is_mock_mode():
            return {
                "paymentKey": payment_key,
                "status": "CANCELED",
                "cancelReason": cancel_reason,
                "mock": True,
            }

        url = f"{self.BASE_URL}/{payment_key}/cancel"
        data = {"cancelReason": cancel_reason}

        try:
            response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = "Payment cancellation failed"
            details = None

            if hasattr(e, "response") and e.response is not None:
                try:
                    details = e.response.json()
                    if "message" in details:
                        error_msg = details["message"]
                except ValueError:
                    # If the error response body is not valid JSON, ignore parsing failures
                    # and fall back to the default error message and details.
                    pass

            raise PaymentFailedException(message=error_msg, details=details) from e


class PaymentService:
    """Service for handling payment operations."""

    def __init__(self, adapter: PaymentGatewayAdapter | None = None) -> None:
        """
        PaymentService가 사용할 결제 게이트웨이 어댑터를 설정한다.
        
        Parameters:
            adapter (PaymentGatewayAdapter | None): 사용할 어댑터 인스턴스. 지정하지 않으면 기본으로 `TossPaymentAdapter`를 생성하여 사용한다.
        """
        self.adapter = adapter or TossPaymentAdapter()

    def confirm_payment(self, payment_key: str, order_id: str, amount: int) -> dict[str, Any]:
        """
        구성된 결제 게이트웨이를 통해 결제를 확정합니다.
        
        Parameters:
            payment_key (str): 게이트웨이가 발급한 결제 키.
            order_id (str): 애플리케이션에서 생성한 주문 ID.
            amount (int): 결제할 금액(정수, 원 단위).
        
        Returns:
            dict[str, Any]: 성공한 결제의 상세 정보.
        """
        return self.adapter.approve(payment_key, order_id, amount)

    def cancel_payment(self, payment_key: str, cancel_reason: str) -> dict[str, Any]:
        """
        지정된 결제를 구성된 결제 게이트웨이를 통해 취소합니다.
        
        Returns:
            dict: 결제 취소 응답(취소된 결제의 상태 및 관련 정보).
        
        Raises:
            PaymentFailedException: 결제 취소가 실패한 경우 발생합니다.
        """
        return self.adapter.cancel(payment_key, cancel_reason)