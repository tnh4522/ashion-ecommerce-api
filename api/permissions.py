from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import UserPermission


class HasModelPermission(BasePermission):
    def has_permission(self, request, view):
        model_name = getattr(view, 'model_name', None)
        action = getattr(view, 'action', None)

        if not model_name or not action:
            return False

        user_permissions = UserPermission.objects.filter(
            user=request.user, model_name=model_name, action=action, allowed=True
        )

        return user_permissions.exists()


class IsAdminOrSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'SELLER']


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SELLER'
