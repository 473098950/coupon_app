from rest_framework.routers import DefaultRouter
from django.urls import path, include

from coupons.views.consumer_views import (
    MembershipCardViewSet,
    RedemptionViewSet,
    ReferralViewSet,
    ConsumerApplyMerchantViewSet,
    UserRegisterView,  # 自定义注册接口
)
from coupons.views.merchant_views import MerchantCouponViewSet, MerchantRedemptionViewSet
from coupons.views.admin_views import (
    AdminAssignRoleView,
    AdminRemoveRoleView,
    AdminMerchantViewSet,
)
from coupons.views.auth_views import CustomTokenObtainPairView  # 自定义 JWT 登录
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import viewsets
from rest_framework.response import Response
from coupons.models import Merchant
from coupons.permissions import IsAdminOrSuperAdmin

# -----------------------
# DRF Router
# -----------------------
router = DefaultRouter()

# ---------------- 消费者接口 ----------------
router.register(r'consumer/membership-cards', MembershipCardViewSet, basename='membership-card')
router.register(r'consumer/redemptions', RedemptionViewSet, basename='redemption')
router.register(r'consumer/referrals', ReferralViewSet, basename='referral')
router.register(r'consumer/apply-merchant', ConsumerApplyMerchantViewSet, basename='apply-merchant')

# ---------------- 商家接口 ----------------
router.register(r'merchant/coupons', MerchantCouponViewSet, basename='merchant-coupon')
router.register(r'merchant/redemptions', MerchantRedemptionViewSet, basename='merchant-redemption')

# ---------------- 管理员接口 ----------------


router.register(r'admin/merchants', AdminMerchantViewSet, basename='admin-merchant')

# ---------------- 用户注册 / 登录 / JWT ----------------
urlpatterns = [
    # 用户注册（公开接口）
    path('user/register/', UserRegisterView.as_view(), name='user-register'),

    # 用户登录（自定义 JWT 登录接口，支持 username/password 和 wechat_openid）
    path('user/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # JWT 刷新接口
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 管理员分配角色
    path('admin/assign-role/', AdminAssignRoleView.as_view(), name='admin-assign-role'),

    # 管理员移除角色
    path('admin/remove-role/', AdminRemoveRoleView.as_view(), name='admin-remove-role'),

    # 包含所有 DRF Router 自动生成的业务接口
    path('', include(router.urls)),
]
