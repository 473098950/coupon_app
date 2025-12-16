from rest_framework.routers import DefaultRouter
from .views import MerchantViewSet, MembershipCardViewSet, CouponRuleViewSet, RedemptionViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'merchants', MerchantViewSet)
router.register(r'membership_cards', MembershipCardViewSet)
router.register(r'coupon_rules', CouponRuleViewSet)
router.register(r'redemptions', RedemptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
