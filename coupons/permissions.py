from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """只允许超级管理员访问"""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_superadmin()

class IsAdminOrSuperAdmin(BasePermission):
    """只允许管理员或超级管理员访问"""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_admin() or user.is_superadmin())

class IsMerchant(BasePermission):
    """只允许商家访问"""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_merchant()

class IsConsumer(BasePermission):
    """只允许消费者访问"""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_consumer()
