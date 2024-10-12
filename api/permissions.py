from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import Permission


class HasModelPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Determine the action based on the request method
        if request.method in permissions.SAFE_METHODS:
            action = 'view'
        elif request.method == 'POST':
            action = 'add'
        elif request.method in ['PUT', 'PATCH']:
            action = 'change'
        elif request.method == 'DELETE':
            action = 'delete'
        else:
            return False  # Method not allowed

        # Get the model name from the view
        model_name = view.get_queryset().model.__name__

        # Check if the user has permission
        return Permission.objects.filter(
            user=request.user,
            model_name=model_name,
            action=action,
            allowed=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        # For object-level permissions, we can use the same logic
        return self.has_permission(request, view)


class IsAdminOrSeller(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'SELLER']


class IsSeller(permissions.BasePermission):
    """
    Custom permission to only allow sellers to perform certain actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SELLER'
