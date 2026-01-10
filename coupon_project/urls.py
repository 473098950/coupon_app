# coupon_project/urls.py

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# -----------------------
# 首页测试视图
# -----------------------
def home(request):
    return HttpResponse("Welcome to Coupon Backend!")


# -----------------------
# Swagger / OpenAPI 配置
# -----------------------
schema_view = get_schema_view(
    openapi.Info(
        title="Coupon Backend API",
        default_version='V0.3',
        description="优惠券后台系统 API 文档（消费者 / 商家 / 管理员）",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# -----------------------
# 项目级 URL 配置
# -----------------------
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # 首页
    path('', home, name='home'),

    # Django Admin
    path('admin/', admin.site.urls),

    # -----------------------
    # JWT 登录 / 刷新接口
    # -----------------------
    # POST /api/token/         -> 登录，返回 access + refresh
    # POST /api/token/refresh/ -> 刷新 access
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # -----------------------
    # 业务 app 入口
    # -----------------------
    path('api/', include('coupons.urls')),

    # -----------------------
    # Swagger 文档
    # -----------------------
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
