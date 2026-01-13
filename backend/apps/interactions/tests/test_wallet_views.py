"""
Tests for Wallet API endpoints.

TDD RED Phase: Tests written before implementation.

Tests:
- POST /wallet/charge/ - Charge coins (MVP: internal simulation)
- GET /users/me/wallet/ - Get wallet balance and recent transactions
- GET /users/me/wallet/transactions/ - Get full transaction history
"""

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.interactions.services import WalletService
from apps.users.models import User


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.fixture
def user(db):
    """Create a regular user."""
    return baker.make(User)


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return baker.make(User, is_staff=True)


@pytest.fixture
def auth_client(user):
    """Create authenticated client for regular user."""
    client = APIClient()
    tokens = get_tokens_for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return client


@pytest.fixture
def admin_client(admin_user):
    """Create authenticated client for admin user."""
    client = APIClient()
    tokens = get_tokens_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return client


@pytest.fixture
def wallet_service():
    """Create WalletService instance."""
    return WalletService()


class TestWalletCharge:
    """Tests for POST /wallet/charge/"""

    def test_charge_coins(self, auth_client, user):
        """Should charge coins to user's wallet."""
        url = "/api/v1/wallet/charge/"
        data = {"amount": 1000, "description": "Test charge"}
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["balance"] == 1000

    def test_charge_additional_coins(self, auth_client, user, wallet_service):
        """Should add to existing balance."""
        wallet_service.charge(user=user, amount=500)

        url = "/api/v1/wallet/charge/"
        data = {"amount": 300}
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["data"]["balance"] == 800

    def test_charge_zero_fails(self, auth_client):
        """Should reject zero amount."""
        url = "/api/v1/wallet/charge/"
        data = {"amount": 0}
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_charge_negative_fails(self, auth_client):
        """Should reject negative amount."""
        url = "/api/v1/wallet/charge/"
        data = {"amount": -100}
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_charge_unauthenticated_fails(self):
        """Should reject unauthenticated request."""
        client = APIClient()
        url = "/api/v1/wallet/charge/"
        data = {"amount": 1000}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestWalletBalance:
    """Tests for GET /users/me/wallet/"""

    def test_get_wallet_balance(self, auth_client, user, wallet_service):
        """Should return wallet balance and recent transactions."""
        wallet_service.charge(user=user, amount=1000)
        wallet_service.spend(user=user, amount=300, description="Purchase")

        url = "/api/v1/users/me/wallet/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["balance"] == 700
        assert "recentTransactions" in resp_data["data"]
        assert len(resp_data["data"]["recentTransactions"]) == 2

    def test_get_wallet_no_wallet(self, auth_client):
        """Should return zero balance if no wallet."""
        url = "/api/v1/users/me/wallet/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["balance"] == 0
        assert resp_data["data"]["recentTransactions"] == []

    def test_get_wallet_unauthenticated_fails(self):
        """Should reject unauthenticated request."""
        client = APIClient()
        url = "/api/v1/users/me/wallet/"
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestWalletTransactions:
    """Tests for GET /users/me/wallet/transactions/"""

    def test_get_transactions_list(self, auth_client, user, wallet_service):
        """Should return transaction list."""
        for _i in range(5):
            wallet_service.charge(user=user, amount=100)

        url = "/api/v1/users/me/wallet/transactions/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["success"] is True
        assert len(resp_data["data"]["results"]) == 5

    def test_get_transactions_empty(self, auth_client):
        """Should return empty list if no transactions."""
        url = "/api/v1/users/me/wallet/transactions/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["results"] == []

    def test_get_transactions_with_pagination(self, auth_client, user, wallet_service):
        """Should paginate transaction list."""
        for _i in range(25):
            wallet_service.charge(user=user, amount=10)

        url = "/api/v1/users/me/wallet/transactions/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        # Default pagination
        assert len(resp_data["data"]["results"]) <= 20

    def test_get_transactions_unauthenticated_fails(self):
        """Should reject unauthenticated request."""
        client = APIClient()
        url = "/api/v1/users/me/wallet/transactions/"
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAdminWalletAdjustment:
    """Tests for POST /admin/wallet/{user_id}/adjustment/"""

    def test_admin_adjustment_positive(self, admin_client, user, db):
        """Admin should be able to add coins."""
        WalletService.charge(user=user, amount=1000)

        url = f"/api/v1/admin/wallet/{user.id}/adjustment/"
        data = {
            "amount": 500,
            "description": "Compensation for issue",
        }
        response = admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["balance"] == 1500

    def test_admin_adjustment_negative(self, admin_client, user, db):
        """Admin should be able to deduct coins."""
        WalletService.charge(user=user, amount=1000)

        url = f"/api/v1/admin/wallet/{user.id}/adjustment/"
        data = {
            "amount": -300,
            "description": "Correction",
        }
        response = admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["balance"] == 700

    def test_non_admin_cannot_adjust(self, auth_client, user, db):
        """Non-admin should be forbidden."""
        other_user = baker.make(User)
        WalletService.charge(user=other_user, amount=1000)

        url = f"/api/v1/admin/wallet/{other_user.id}/adjustment/"
        data = {"amount": 500}
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_adjustment_nonexistent_user_fails(self, admin_client):
        """Should return 404 for non-existent user."""
        url = "/api/v1/admin/wallet/99999/adjustment/"
        data = {"amount": 500}
        response = admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
