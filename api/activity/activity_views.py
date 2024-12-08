from rest_framework import permissions, generics

from api.activity.activity_serializers import ActivityLogSerializer
from api.models import ActivityLog


class ActivityLogListView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ActivityLog.objects.all()