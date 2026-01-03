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
        default_version='V0.2',
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
urlpatterns = [
    # 首页
    path('', home, name='home'),

    # Django Admin
    path('admin/', admin.site.urls),

    # API 入口（指向 coupons app 的 urls.py）
    path('api/', include('coupons.urls')),

    # Swagger 文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
