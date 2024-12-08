from rest_framework import serializers
from ..models import ActivityLog
from ..serializers import UserSerializer


class ActivityLogListViewSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'status', 'action', 'model', 'context', 'data', 'created_at']


class ActivityLogCreateSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField(required=False)

    class Meta:
        model = ActivityLog
        fields = ['user', 'status', 'action', 'model', 'context', 'data', 'ip_address']
