# coupons/permissions.py
from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """只允许超级管理员访问"""
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'is_superadmin', lambda: False)())

class IsAdminOrSuperAdmin(BasePermission):
    """只允许管理员或超级管理员访问"""
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and (
            getattr(user, 'is_admin', lambda: False)() or getattr(user, 'is_superadmin', lambda: False)()
        ))

class IsMerchant(BasePermission):
    """只允许商家访问"""
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'is_merchant', lambda: False)())

class IsConsumer(BasePermission):
    """只允许消费者访问"""
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'is_consumer', lambda: False)())
