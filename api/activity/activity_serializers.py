from rest_framework import serializers
from ..models import ActivityLog
from ..serializers import UserSerializer


class ActivityLogSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user = UserSerializer(required=False)

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'status', 'action', 'model', 'context', 'ip_address', 'data', 'created_at']
