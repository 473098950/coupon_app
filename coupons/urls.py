from rest_framework.routers import DefaultRouter
from django.urls import path, include

# 导入各端的 ViewSet
from .views.admin_views import AdminMerchantViewSet
from .views.merchant_views import MerchantCouponViewSet, MerchantRedemptionViewSet
from .views.consumer_views import MembershipCardViewSet, RedemptionViewSet, ReferralViewSet

router = DefaultRouter()

# ---------------------------
# 管理员端 (超级管理员 / 管理员)
# ---------------------------
router.register(
    'admin/merchants',
    AdminMerchantViewSet,
    basename='admin-merchant'
)

# ---------------------------
# 商家端
# ---------------------------
router.register(
    'merchant/coupons',
    MerchantCouponViewSet,
    basename='merchant-coupon'
)
router.register(
    'merchant/redemptions',
    MerchantRedemptionViewSet,
    basename='merchant-redemption'
)

# ---------------------------
# 消费者端
# ---------------------------
router.register(
    'consumer/membership_cards',
    MembershipCardViewSet,
    basename='consumer-membership-card'
)
router.register(
    'consumer/redemptions',
    RedemptionViewSet,
    basename='consumer-redemption'
)
router.register(
    'consumer/referrals',
    ReferralViewSet,
    basename='consumer-referral'
)

# ---------------------------
# 最终路由
# ---------------------------
urlpatterns = [
    path('', include(router.urls)),
]
