# coupons/views/auth_views.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from coupons.serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    用户登录接口
    支持：
      1. username + password（网页端 / 通用 API）
      2. wechat_openid（小程序登录）
    返回：
      access / refresh token
      username
      roles
      default_role（默认登录角色）
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="用户登录获取 JWT",
        operation_description="支持 username/password 登录，返回 access 和 refresh token，以及用户角色信息",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            one_of=[
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['username', 'password'],
                    properties={
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description='用户名'),
                        'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
                    }
                ),
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['wechat_openid'],
                    properties={
                        'wechat_openid': openapi.Schema(type=openapi.TYPE_STRING, description='微信小程序 OpenID')
                    }
                )
            ]
        ),
        responses={
            200: openapi.Response(
                description="登录成功",
                examples={
                    "application/json": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "username": "testuser",
                        "roles": ["consumer"],
                        "default_role": "consumer"
                    }
                }
            ),
            401: openapi.Response(
                description="认证失败",
                examples={"application/json": {"detail": "用户名或密码错误"}}
            ),
            400: openapi.Response(
                description="请求参数错误",
                examples={"application/json": {"username": ["此字段为必填项"], "password": ["此字段为必填项"]}}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
