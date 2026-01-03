from django.urls import path, include
from rest_framework.routers import DefaultRouter
from coupons.views.consumer_views import (
    MembershipCardViewSet,
    RedemptionViewSet,
    ReferralViewSet,
    ConsumerApplyMerchantViewSet,
    UserRegisterView,
    UserLoginView
)
from coupons.views.merchant_views import (
    MerchantCouponViewSet,
    MerchantRedemptionViewSet,
)
from coupons.views.admin_views import AdminMerchantViewSet

# -----------------------
# DRF 默认路由
# -----------------------
router = DefaultRouter()

# 消费者接口
router.register(r'consumer/membership-cards', MembershipCardViewSet, basename='membership-card')
router.register(r'consumer/redemptions', RedemptionViewSet, basename='redemption')
router.register(r'consumer/referrals', ReferralViewSet, basename='referral')
router.register(r'consumer/apply-merchant', ConsumerApplyMerchantViewSet, basename='apply-merchant')

# 商家接口
router.register(r'merchant/coupons', MerchantCouponViewSet, basename='merchant-coupon')
router.register(r'merchant/redemptions', MerchantRedemptionViewSet, basename='merchant-redemption')

# 管理员接口
router.register(r'admin/merchants', AdminMerchantViewSet, basename='admin-merchant')


# -----------------------
# 用户注册 / 登录接口
# -----------------------
urlpatterns = [
    path('user/register/', UserRegisterView.as_view(), name='user-register'),
    path('user/login/', UserLoginView.as_view(), name='user-login'),

    # 包含所有 ViewSet 自动生成的路由
    path('', include(router.urls)),
]
