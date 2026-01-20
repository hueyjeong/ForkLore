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
        Approve a payment through the configured payment gateway.
        
        Parameters:
            payment_key (str): The payment key issued by the gateway.
            order_id (str): The application-generated order identifier.
            amount (int): The amount to approve (in the gateway's smallest currency unit).
        
        Returns:
            dict: The gateway's response payload.
        
        Raises:
            PaymentFailedException: If the gateway request fails or the gateway returns an error.
        """
        ...

    def cancel(self, payment_key: str, cancel_reason: str) -> dict[str, Any]:
        """
        Cancel a payment through the configured Toss Payments gateway.
        
        If mock mode is enabled, returns a deterministic mock cancellation response; otherwise sends a cancellation request to the gateway and returns the gateway's JSON response.
        
        Parameters:
            payment_key (str): Identifier of the payment to cancel.
            cancel_reason (str): Reason for cancelling the payment.
        
        Returns:
            dict[str, Any]: The payment gateway's response JSON for the cancellation.
        
        Raises:
            PaymentFailedException: When the gateway request fails or the gateway returns an error.
        """
        ...


class TossPaymentAdapter:
    """Adapter for Toss Payments API."""

    BASE_URL = "https://api.tosspayments.com/v1/payments"

    def __init__(self) -> None:
        """
        Initialize the adapter by reading the Toss Payments secret key from Django settings and storing it on the instance.
        
        The secret key is read from `settings.TOSS_PAYMENTS_SECRET_KEY` and assigned to `self.secret_key`.
        """
        self.secret_key = settings.TOSS_PAYMENTS_SECRET_KEY

    def _get_headers(self) -> dict[str, str]:
        """
        Build HTTP headers for Toss Payments API requests.
        
        Returns:
            dict[str, str]: HTTP headers for requests. If `self.secret_key` is set, includes an `Authorization` header using Basic auth with the secret key (empty password) and `Content-Type: application/json`. Returns an empty dict when `self.secret_key` is not set.
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
        Determine whether the adapter should operate in mock mode.
        
        If the TOSS_PAYMENTS_USE_MOCK setting is defined, its boolean value is used.
        If the setting is not defined, mock mode is enabled when the adapter has no secret key.
        
        Returns:
            bool: `True` if mock mode is active, `False` otherwise.
        """
        # Prefer an explicit setting to control mock mode. If the setting is
        # not defined, fall back to treating a missing secret key as mock mode.
        use_mock = getattr(settings, "TOSS_PAYMENTS_USE_MOCK", None)
        if use_mock is not None:
            return bool(use_mock)

        return self.secret_key is None

    def approve(self, payment_key: str, order_id: str, amount: int) -> dict[str, Any]:
        """
        Confirm a payment with Toss Payments and return the gateway response.
        
        When mock mode is active (for example when a test key is used or no secret key is configured), returns a deterministic mock success response containing payment details.
        
        Returns:
            dict[str, Any]: The gateway's JSON response or a mock response with keys such as `paymentKey`, `orderId`, `amount`, `status`, and `approvedAt`.
        
        Raises:
            PaymentFailedException: If the HTTP request fails or the gateway responds with an error. The exception's `details` may contain the parsed JSON error body when available.
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
        Cancel a Toss Payments payment.
        
        Parameters:
            payment_key (str): Toss Payments `paymentKey` identifying the payment to cancel.
            cancel_reason (str): Human-readable reason for the cancellation.
        
        Returns:
            dict[str, Any]: Parsed JSON response from the gateway. In mock mode returns a dict containing
                `paymentKey`, `status` ("CANCELED"), `cancelReason`, and `mock` (True).
        
        Raises:
            PaymentFailedException: If the HTTP request fails or the gateway responds with an error;
                the exception contains a `message` and optional `details` extracted from the gateway response.
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
        Initialize the PaymentService with a payment gateway adapter.
        
        If `adapter` is not provided, a `TossPaymentAdapter` instance is used as the default.
        
        Parameters:
            adapter (PaymentGatewayAdapter | None): Optional adapter implementing the payment gateway interface.
        """
        self.adapter = adapter or TossPaymentAdapter()

    def confirm_payment(self, payment_key: str, order_id: str, amount: int) -> dict[str, Any]:
        """
        Confirm a payment using the configured payment gateway.
        
        Returns:
            dict: Gateway response containing payment details.
        
        Raises:
            PaymentFailedException: If the payment confirmation fails.
        """
        return self.adapter.approve(payment_key, order_id, amount)

    def cancel_payment(self, payment_key: str, cancel_reason: str) -> dict[str, Any]:
        """
        Cancel a payment through the configured gateway.

        Args:
            payment_key: The payment key to cancel.
            cancel_reason: The reason for cancellation.

        Returns:
            dict: The cancellation details.

        Raises:
            PaymentFailedException: If the payment cancellation fails.
        """
        return self.adapter.cancel(payment_key, cancel_reason)