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
    """Create a user."""
    return baker.make("users.User")


@pytest.fixture
def wallet_service():
    """
    Provide a WalletService instance for tests.
    
    Returns:
        WalletService: An initialized WalletService to be used by test cases.
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
        """
        Do not update the user's wallet balance or create a CoinTransaction when payment confirmation raises PaymentFailedException.
        """
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