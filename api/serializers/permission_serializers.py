# my_app/serializers/permission_serializers.py

from rest_framework import serializers
from ..models import Permission, UserPermission, Role, RolePermission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class UserPermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = UserPermission
        fields = ('id', 'permission', 'allowed')

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(child=serializers.CharField(), write_only=True)
    permissions_display = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'permissions', 'permissions_display')

    def get_permissions_display(self, obj):
        permissions = RolePermission.objects.filter(allowed=True, role=obj)
        return [f"{perm.permission.model_name}:{perm.permission.action}" for perm in permissions]

    def validate_permissions(self, value):
        permissions = []
        for perm_str in value:
            try:
                model_name, action = perm_str.split(':')
                permission = Permission.objects.get(model_name=model_name, action=action)
                permissions.append(permission)
            except (ValueError, Permission.DoesNotExist):
                raise serializers.ValidationError(f"Invalid permission: {perm_str}")
        return permissions

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )
        role_permissions = [
            RolePermission(role=role, permission=permission, allowed=True)
            for permission in permissions
        ]
        RolePermission.objects.bulk_create(role_permissions)
        return role
