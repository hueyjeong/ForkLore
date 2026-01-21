import pytest
from unittest.mock import patch
from apps.interactions.services import SubscriptionService
from apps.interactions.models import PlanType, Subscription, SubscriptionStatus
from apps.interactions.constants import PLAN_PRICES
from apps.interactions.exceptions import PaymentFailedException
from apps.users.models import User


@pytest.mark.django_db
class TestSubscriptionPayment:
    def setup_method(self):
        """
        테스트 메서드 실행 전 구독 서비스 인스턴스와 테스트 사용자를 초기화합니다.
        
        테스트에서 재사용할 SubscriptionService 인스턴스를 생성하고, 데이터베이스에 사용자 계정(username="testuser")을 생성합니다.
        """
        self.service = SubscriptionService()
        self.user = User.objects.create_user(username="testuser", password="password")

    @patch("apps.interactions.services.PaymentService")
    def test_subscribe_with_payment_success(self, mock_payment_service_class):
        # Arrange
        """
        결제가 성공할 때 SubscriptionService.subscribe가 활성 구독을 생성하고 결제 확인을 올바르게 호출하는지 검증한다.
        
        구체적으로, 생성된 구독의 상태가 ACTIVE인지, 요청한 플랜과 결제 ID가 저장되었는지 확인하고, PaymentService.confirm_payment가 payment_key, order_id, amount 인수로 한 번 호출되었는지 검증한다.
        """
        payment_id = "payment_key_123"
        order_id = "order_id_123"
        plan_type = PlanType.BASIC
        price = PLAN_PRICES[plan_type]

        mock_instance = mock_payment_service_class.return_value
        mock_instance.confirm_payment.return_value = {"status": "DONE"}

        # Act
        subscription = self.service.subscribe(
            user=self.user, plan_type=plan_type, payment_id=payment_id, order_id=order_id
        )

        # Assert
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.plan_type == plan_type
        assert subscription.payment_id == payment_id

        mock_instance.confirm_payment.assert_called_once_with(
            payment_key=payment_id, order_id=order_id, amount=price
        )

    @patch("apps.interactions.services.PaymentService")
    def test_subscribe_with_payment_failure(self, mock_payment_service_class):
        # Arrange
        payment_id = "payment_key_fail"
        order_id = "order_id_fail"
        plan_type = PlanType.PREMIUM
        price = PLAN_PRICES[plan_type]

        mock_instance = mock_payment_service_class.return_value
        mock_instance.confirm_payment.side_effect = PaymentFailedException("Payment failed")

        # Act & Assert
        with pytest.raises(PaymentFailedException):
            self.service.subscribe(
                user=self.user, plan_type=plan_type, payment_id=payment_id, order_id=order_id
            )

        # Verify no subscription created
        assert not Subscription.objects.filter(user=self.user).exists()

        mock_instance.confirm_payment.assert_called_once_with(
            payment_key=payment_id, order_id=order_id, amount=price
        )