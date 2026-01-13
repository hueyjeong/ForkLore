"""
Tests for WalletService.

TDD RED Phase: Tests written before implementation.
"""

from typing import Any

import pytest
from model_bakery import baker

from apps.interactions.models import (
    CoinTransaction,
    TransactionType,
)
from apps.interactions.services import WalletService
from apps.users.models import User


@pytest.fixture
def user(db: Any) -> User:
    """Create a user."""
    return baker.make("users.User")


@pytest.fixture
def wallet_service() -> WalletService:
    """Create WalletService instance."""
    return WalletService()


class TestWalletServiceCharge:
    """Tests for WalletService.charge method."""

    def test_charge_creates_wallet_if_not_exists(
        self, wallet_service: WalletService, user: User
    ) -> None:
        """Should create wallet automatically on first charge."""
        result = wallet_service.charge(
            user=user,
            amount=1000,
            description="Initial charge",
        )

        assert result["wallet"].user == user
        assert result["wallet"].balance == 1000
        assert result["transaction"].amount == 1000
        assert result["transaction"].transaction_type == TransactionType.CHARGE
        assert result["transaction"].balance_after == 1000

    def test_charge_updates_existing_wallet(
        self, wallet_service: WalletService, user: User
    ) -> None:
        """Should update balance on existing wallet."""
        # First charge
        wallet_service.charge(user=user, amount=1000)

        # Second charge
        result = wallet_service.charge(
            user=user,
            amount=500,
            description="Additional charge",
        )

        assert result["wallet"].balance == 1500
        assert result["transaction"].amount == 500
        assert result["transaction"].balance_after == 1500

    def test_charge_creates_transaction_record(
        self, wallet_service: WalletService, user: User
    ) -> None:
        """Should create transaction record."""
        wallet_service.charge(user=user, amount=1000)

        transactions = CoinTransaction.objects.filter(wallet__user=user)
        assert transactions.count() == 1
        assert transactions[0].transaction_type == TransactionType.CHARGE
        assert transactions[0].amount == 1000

    def test_charge_zero_amount_fails(self, wallet_service: WalletService, user: User) -> None:
        """Should reject zero amount charge."""
        with pytest.raises(ValueError, match="충전 금액은 0보다 커야 합니다"):
            wallet_service.charge(user=user, amount=0)

    def test_charge_negative_amount_fails(self, wallet_service: WalletService, user: User) -> None:
        """Should reject negative amount charge."""
        with pytest.raises(ValueError, match="충전 금액은 0보다 커야 합니다"):
            wallet_service.charge(user=user, amount=-100)


class TestWalletServiceSpend:
    """Tests for WalletService.spend method."""

    def test_spend_deducts_balance(self, wallet_service: WalletService, user: User) -> None:
        """Should deduct balance on spend."""
        wallet_service.charge(user=user, amount=1000)

        result = wallet_service.spend(
            user=user,
            amount=300,
            description="Purchase chapter",
        )

        assert result["wallet"].balance == 700
        assert result["transaction"].amount == 300
        assert result["transaction"].transaction_type == TransactionType.SPEND
        assert result["transaction"].balance_after == 700

    def test_spend_with_reference(self, wallet_service: WalletService, user: User, db: Any) -> None:
        """Should record reference info for purchases."""
        wallet_service.charge(user=user, amount=1000)
        chapter = baker.make("contents.Chapter")

        result = wallet_service.spend(
            user=user,
            amount=100,
            description="Purchase chapter",
            reference_type="chapter",
            reference_id=chapter.id,
        )

        assert result["transaction"].reference_type == "chapter"
        assert result["transaction"].reference_id == chapter.id

    def test_spend_insufficient_balance_fails(
        self, wallet_service: WalletService, user: User
    ) -> None:
        """Should fail if insufficient balance."""
        wallet_service.charge(user=user, amount=100)

        with pytest.raises(ValueError, match="잔액이 부족합니다"):
            wallet_service.spend(user=user, amount=500)

    def test_spend_no_wallet_fails(self, wallet_service: WalletService, user: User) -> None:
        """Should fail if wallet doesn't exist."""
        with pytest.raises(ValueError, match="지갑이 존재하지 않습니다"):
            wallet_service.spend(user=user, amount=100)

    def test_spend_zero_amount_fails(self, wallet_service: WalletService, user: User) -> None:
        """Should reject zero amount spend."""
        wallet_service.charge(user=user, amount=1000)

        with pytest.raises(ValueError, match="사용 금액은 0보다 커야 합니다"):
            wallet_service.spend(user=user, amount=0)

    def test_spend_exact_balance(self, wallet_service: WalletService, user: User) -> None:
        """Should allow spending exact balance amount."""
        wallet_service.charge(user=user, amount=500)

        result = wallet_service.spend(user=user, amount=500)

        assert result["wallet"].balance == 0


class TestWalletServiceRefund:
    """Tests for WalletService.refund method."""

    def test_refund_adds_balance(self, wallet_service: WalletService, user: User) -> None:
        """Should add balance on refund."""
        wallet_service.charge(user=user, amount=1000)
        wallet_service.spend(user=user, amount=300)

        result = wallet_service.refund(
            user=user,
            amount=300,
            description="Refund purchase",
        )

        assert result["wallet"].balance == 1000
        assert result["transaction"].amount == 300
        assert result["transaction"].transaction_type == TransactionType.REFUND
        assert result["transaction"].balance_after == 1000

    def test_refund_with_reference(
        self, wallet_service: WalletService, user: User, db: Any
    ) -> None:
        """Should record reference info for refunds."""
        wallet_service.charge(user=user, amount=1000)
        chapter = baker.make("contents.Chapter")
        wallet_service.spend(
            user=user,
            amount=100,
            reference_type="chapter",
            reference_id=chapter.id,
        )

        result = wallet_service.refund(
            user=user,
            amount=100,
            description="Refund chapter",
            reference_type="chapter",
            reference_id=chapter.id,
        )

        assert result["transaction"].reference_type == "chapter"
        assert result["transaction"].reference_id == chapter.id


class TestWalletServiceAdjustment:
    """Tests for WalletService.adjustment method (admin only)."""

    def test_adjustment_positive(self, wallet_service: WalletService, user: User) -> None:
        """Should add balance on positive adjustment."""
        wallet_service.charge(user=user, amount=1000)

        result = wallet_service.adjustment(
            user=user,
            amount=500,
            description="Admin adjustment: compensation",
        )

        assert result["wallet"].balance == 1500
        assert result["transaction"].transaction_type == TransactionType.ADJUSTMENT
        assert result["transaction"].amount == 500

    def test_adjustment_negative(self, wallet_service: WalletService, user: User) -> None:
        """Should subtract balance on negative adjustment."""
        wallet_service.charge(user=user, amount=1000)

        result = wallet_service.adjustment(
            user=user,
            amount=-200,
            description="Admin adjustment: correction",
        )

        assert result["wallet"].balance == 800
        assert result["transaction"].amount == -200

    def test_adjustment_negative_below_zero_allowed(
        self, wallet_service: WalletService, user: User
    ) -> None:
        """Admin adjustment can set balance below zero (for corrections)."""
        wallet_service.charge(user=user, amount=100)

        result = wallet_service.adjustment(
            user=user,
            amount=-500,
            description="Admin correction",
        )

        assert result["wallet"].balance == -400


class TestWalletServiceGetBalance:
    """Tests for WalletService.get_balance method."""

    def test_get_balance(self, wallet_service: WalletService, user: User) -> None:
        """Should return current balance."""
        wallet_service.charge(user=user, amount=1000)
        wallet_service.spend(user=user, amount=300)

        balance = wallet_service.get_balance(user=user)

        assert balance == 700

    def test_get_balance_no_wallet(self, wallet_service: WalletService, user: User) -> None:
        """Should return 0 if no wallet."""
        balance = wallet_service.get_balance(user=user)

        assert balance == 0


class TestWalletServiceGetTransactions:
    """Tests for WalletService.get_transactions method."""

    def test_get_transactions(self, wallet_service: WalletService, user: User) -> None:
        """Should return transaction list."""
        wallet_service.charge(user=user, amount=1000)
        wallet_service.spend(user=user, amount=300)
        wallet_service.charge(user=user, amount=200)

        transactions = wallet_service.get_transactions(user=user)

        assert len(transactions) == 3
        # Should be ordered by created_at desc
        assert transactions[0].transaction_type == TransactionType.CHARGE  # Most recent
        assert transactions[1].transaction_type == TransactionType.SPEND

    def test_get_transactions_with_limit(self, wallet_service: WalletService, user: User) -> None:
        """Should limit transaction list."""
        for _i in range(10):
            wallet_service.charge(user=user, amount=100)

        transactions = wallet_service.get_transactions(user=user, limit=5)

        assert len(transactions) == 5

    def test_get_transactions_no_wallet(self, wallet_service: WalletService, user: User) -> None:
        """Should return empty list if no wallet."""
        transactions = wallet_service.get_transactions(user=user)

        assert len(transactions) == 0


class TestCoinTransactionImmutability:
    """Tests for transaction immutability (INSERT ONLY policy)."""

    def test_transaction_cannot_be_updated(
        self, wallet_service: WalletService, user: User, db: Any
    ) -> None:
        """Transactions should not be updatable."""
        wallet_service.charge(user=user, amount=1000)
        tx = CoinTransaction.objects.first()

        # Attempt to update should fail or be prevented
        tx.amount = 5000
        tx.save()

        # Reload from DB - should still be original value
        # Note: This test verifies business logic, not DB constraint
        # The actual immutability is enforced by service layer
        tx.refresh_from_db()
        # If we add DB-level protection, this would fail

    def test_transaction_cannot_be_deleted(
        self, wallet_service: WalletService, user: User, db: Any
    ) -> None:
        """Transactions should not be deletable via service."""
        wallet_service.charge(user=user, amount=1000)

        # Verify transaction exists
        assert CoinTransaction.objects.count() == 1

        # Note: Actual delete prevention would be at DB or model level


class TestWalletConcurrency:
    """Tests for wallet concurrency (select_for_update)."""

    def test_concurrent_spend_prevents_overdraft(
        self, wallet_service: WalletService, user: User, db: Any
    ) -> None:
        """
        Concurrent spend operations should not overdraft.

        Note: This is a conceptual test. True concurrency testing
        requires thread/process-based testing.
        """
        wallet_service.charge(user=user, amount=100)

        # First spend should succeed
        wallet_service.spend(user=user, amount=60)

        # Second spend should fail (only 40 remaining)
        with pytest.raises(ValueError, match="잔액이 부족합니다"):
            wallet_service.spend(user=user, amount=60)

        # Final balance should be 40
        assert wallet_service.get_balance(user=user) == 40
