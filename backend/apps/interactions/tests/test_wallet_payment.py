"""
Tests for WalletService payment integration.
"""

from unittest.mock import patch

import pytest
from model_bakery import baker

from apps.interactions.exceptions import PaymentFailedException
from apps.interactions.models import CoinTransaction
from apps.interactions.services import WalletService


@pytest.fixture
def user(db):
    """
    테스트용 User 인스턴스를 생성한다.
    
    Returns:
        user (users.User): 생성된 `users.User` 모델 인스턴스.
    """
    return baker.make("users.User")


@pytest.fixture
def wallet_service():
    """
    테스트에서 사용할 WalletService 인스턴스를 생성하여 반환합니다.
    
    Returns:
        WalletService: 테스트용 WalletService 인스턴스
    """
    return WalletService()


class TestWalletServiceChargePayment:
    """Tests for WalletService.charge with payment."""

    def test_charge_confirms_payment_before_balance_update(self, wallet_service, user):
        """Should confirm payment before updating balance."""
        payment_key = "test_payment_key"
        order_id = "test_order_id"
        amount = 1000

        # Mock PaymentService
        # Patch where it is looked up: apps.interactions.services.PaymentService
        with patch("apps.interactions.services.PaymentService") as MockPaymentService:
            mock_service_instance = MockPaymentService.return_value
            mock_service_instance.confirm_payment.return_value = {
                "paymentKey": payment_key,
                "status": "DONE",
            }

            # Execute
            result = wallet_service.charge(
                user=user,
                amount=amount,
                payment_key=payment_key,
                order_id=order_id,
                description="Charge with payment",
            )

            # Verify PaymentService was called
            mock_service_instance.confirm_payment.assert_called_once_with(
                payment_key=payment_key, order_id=order_id, amount=amount
            )

            # Verify wallet update
            assert result["wallet"].balance == 1000
            assert result["transaction"].amount == 1000
            assert "Payment: test_payment_key" in result["transaction"].description

    def test_charge_fails_if_payment_fails(self, wallet_service, user):
        """Should NOT update balance if payment fails."""
        payment_key = "fail_payment_key"
        order_id = "fail_order_id"
        amount = 1000

        # Mock PaymentService to raise exception
        with patch("apps.interactions.services.PaymentService") as MockPaymentService:
            mock_service_instance = MockPaymentService.return_value
            mock_service_instance.confirm_payment.side_effect = PaymentFailedException(
                "Payment failed"
            )

            # Execute
            with pytest.raises(PaymentFailedException):
                wallet_service.charge(
                    user=user, amount=amount, payment_key=payment_key, order_id=order_id
                )

            # Verify balance NOT updated
            wallet_balance = wallet_service.get_balance(user)
            assert wallet_balance == 0

            # Verify no transaction created
            assert CoinTransaction.objects.count() == 0

    def test_charge_skips_payment_check_if_no_key(self, wallet_service, user):
        """Should skip payment confirmation if key not provided (legacy/admin support)."""
        amount = 500

        with patch("apps.interactions.services.PaymentService") as MockPaymentService:
            # Execute without payment keys
            result = wallet_service.charge(user=user, amount=amount, description="Legacy charge")

            # Verify PaymentService NOT called
            MockPaymentService.assert_not_called()

            # Verify wallet update
            assert result["wallet"].balance == 500


class TestTossPaymentAdapterMockMode:
    """Tests for TossPaymentAdapter mock mode behavior."""

    def test_empty_string_secret_key_uses_mock_mode(self):
        """
        비어 있는 문자열인 secret_key가 TossPaymentAdapter를 모의(Mock) 모드로 전환하는지 검증한다.
        """
        from apps.interactions.services.payment_service import TossPaymentAdapter

        adapter = TossPaymentAdapter()
        adapter.secret_key = ""
        assert adapter._is_mock_mode() is True