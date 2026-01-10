# coupons/views/admin_views.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from coupons.permissions import IsAdminOrSuperAdmin
from coupons.models import User, Merchant


# ---------------------------
# 管理员分配用户角色
# ---------------------------
class AdminAssignRoleView(APIView):
    """
    管理员接口：给用户分配角色
    """
    permission_classes = [IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary="分配用户角色",
        operation_description="管理员接口：给指定用户名的用户分配角色（consumer / merchant / admin / superadmin）",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'role'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='需要修改角色的用户名'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='角色名称，可选值: consumer, merchant, admin, superadmin')
            }
        ),
        responses={
            200: openapi.Response(
                description="分配成功",
                examples={"application/json": {"message": "已给用户 testuser 分配角色 consumer", "roles": ["consumer"]}}
            ),
            400: openapi.Response(
                description="请求参数错误",
                examples={"application/json": {"error": "username 和 role 必填"}}
            ),
            404: openapi.Response(
                description="用户不存在",
                examples={"application/json": {"error": "用户不存在"}}
            ),
            403: openapi.Response(
                description="权限不足",
                examples={"application/json": {"detail": "您没有执行该操作的权限。"}}
            )
        }
    )
    def post(self, request):
        username = request.data.get('username')
        role = request.data.get('role')

        if not username or not role:
            return Response({"error": "username 和 role 必填"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        if role not in ['consumer', 'merchant', 'admin', 'superadmin']:
            return Response({"error": "角色不合法"}, status=status.HTTP_400_BAD_REQUEST)

        if role in getattr(user, 'roles', []):
            return Response({"message": f"用户已经有角色 {role}", "roles": user.roles})

        user.add_role(role)
        return Response({"message": f"已给用户 {username} 分配角色 {role}", "roles": user.roles})


# ---------------------------
# 管理员移除用户角色
# ---------------------------
class AdminRemoveRoleView(APIView):
    """
    管理员接口：移除用户角色
    """
    permission_classes = [IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary="移除用户角色",
        operation_description="管理员接口：从指定用户名的用户移除角色（consumer / merchant / admin / superadmin）",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'role'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='需要修改角色的用户名'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='角色名称，可选值: consumer, merchant, admin, superadmin')
            }
        ),
        responses={
            200: openapi.Response(
                description="移除成功",
                examples={"application/json": {"message": "已从用户 testuser 移除角色 consumer", "roles": []}}
            ),
            400: openapi.Response(
                description="请求参数错误",
                examples={"application/json": {"error": "username 和 role 必填"}}
            ),
            404: openapi.Response(
                description="用户不存在",
                examples={"application/json": {"error": "用户不存在"}}
            ),
            403: openapi.Response(
                description="权限不足",
                examples={"application/json": {"detail": "您没有执行该操作的权限。"}}
            )
        }
    )
    def post(self, request):
        username = request.data.get('username')
        role = request.data.get('role')

        if not username or not role:
            return Response({"error": "username 和 role 必填"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        if role not in ['consumer', 'merchant', 'admin', 'superadmin']:
            return Response({"error": "角色不合法"}, status=status.HTTP_400_BAD_REQUEST)

        if role not in getattr(user, 'roles', []):
            return Response({"message": f"用户没有角色 {role}", "roles": user.roles})

        user.remove_role(role)
        return Response({"message": f"已从用户 {username} 移除角色 {role}", "roles": user.roles})


# ---------------------------
# 管理员管理商家接口
# ---------------------------
class AdminMerchantViewSet(viewsets.ModelViewSet):
    """
    管理员接口：管理商家（列表 / 创建 / 更新 / 删除）
    """
    queryset = Merchant.objects.all()
    permission_classes = [IsAdminOrSuperAdmin]

    @swagger_auto_schema(operation_summary="列出所有商家")
    def list(self, request, *args, **kwargs):
        merchants = [{"id": m.id, "name": m.name} for m in self.queryset]
        return Response({"merchants": merchants})

    @swagger_auto_schema(operation_summary="查看单个商家详情")
    def retrieve(self, request, pk=None):
        try:
            merchant = Merchant.objects.get(pk=pk)
            data = {"id": merchant.id, "name": merchant.name}
            return Response(data)
        except Merchant.DoesNotExist:
            return Response({"error": "商家不存在"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary="创建商家",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={'name': openapi.Schema(type=openapi.TYPE_STRING, description='商家名称')}
        )
    )
    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response({"error": "name 必填"}, status=status.HTTP_400_BAD_REQUEST)
        merchant = Merchant.objects.create(name=name)
        return Response({"id": merchant.id, "name": merchant.name}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="更新商家",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={'name': openapi.Schema(type=openapi.TYPE_STRING, description='商家名称')}
        )
    )
    def update(self, request, pk=None):
        try:
            merchant = Merchant.objects.get(pk=pk)
            name = request.data.get('name')
            if not name:
                return Response({"error": "name 必填"}, status=status.HTTP_400_BAD_REQUEST)
            merchant.name = name
            merchant.save()
            return Response({"id": merchant.id, "name": merchant.name})
        except Merchant.DoesNotExist:
            return Response({"error": "商家不存在"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(operation_summary="删除商家")
    def destroy(self, request, pk=None):
        try:
            merchant = Merchant.objects.get(pk=pk)
            merchant.delete()
            return Response({"message": "商家已删除"})
        except Merchant.DoesNotExist:
            return Response({"error": "商家不存在"}, status=status.HTTP_404_NOT_FOUND)
