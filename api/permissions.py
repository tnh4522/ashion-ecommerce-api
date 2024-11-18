from .models import UserPermission, RolePermission
from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        model_name = getattr(view, 'model_name', None)
        action = getattr(view, 'action', None)

        if not model_name or not action:
            return False

        return request.user.has_permission(model_name, action)


class HasRolePermission(BasePermission):
    def has_permission(self, request, view):
        model_name = getattr(view, 'model_name', None)
        action = getattr(view, 'action', None)

        if not model_name or not action:
            return False

        user = request.user

        if UserPermission.objects.filter(
                user=user, permission__model_name=model_name, permission__action=action, allowed=True
        ).exists():
            return True

        if user.role and RolePermission.objects.filter(
                role=user.role, permission__model_name=model_name, permission__action=action, allowed=True
        ).exists():
            return True

        return False
