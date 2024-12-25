import asyncio

from asgiref.sync import sync_to_async
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions, generics
from rest_framework.pagination import PageNumberPagination
import json
from django.http import StreamingHttpResponse
from api.activity.activity_serializers import *
from api.models import ActivityLog


class ActivityLogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ActivityLogListView(generics.ListAPIView):
    serializer_class = ActivityLogListViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ActivityLog.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'status', 'action', 'model', 'context', 'created_at']
    search_fields = ['user', 'status', 'action', 'model', 'context', 'created_at']
    ordering_fields = ['user', 'status', 'action', 'model', 'context', 'created_at']
    pagination_class = ActivityLogPagination


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ActivityLogCreateView(generics.CreateAPIView):
    serializer_class = ActivityLogCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ActivityLog.objects.all()

    def perform_create(self, serializer):
        ip_address = get_client_ip(self.request)
        serializer.save(ip_address=ip_address)


class ActivityLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityLogListViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ActivityLog.objects.all()


@sync_to_async
def fetch_initial_logs():
    logs = ActivityLog.objects.select_related('user').all().order_by('-created_at')[:10]
    serialized_logs = [
        {
            'id': log.id,
            'user': log.user.username if log.user else 'Anonymous',
            'model': log.model,
            'action': log.action,
            'timestamp': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'details': log.data
        }
        for log in logs
    ]
    return serialized_logs


@sync_to_async
def fetch_new_logs(last_log_id):
    logs = ActivityLog.objects.select_related('user').filter(id__gt=last_log_id).order_by('-created_at')
    serialized_logs = [
        {
            'id': log.id,
            'user': log.user.username if log.user else 'Anonymous',
            'model': log.model,
            'action': log.action,
            'timestamp': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'details': log.data
        }
        for log in logs
    ]
    return serialized_logs


async def activity_log_stream(request):
    """
    Streams activity logs to the client using Server-Sent Events (SSE).
    """

    async def event_stream():
        last_log_id = None

        initial_logs = await fetch_initial_logs()
        if initial_logs:
            for log_data in initial_logs:
                yield f"data: {json.dumps(log_data)}\n\n"
            last_log_id = initial_logs[0]['id']

        while True:
            new_logs = await fetch_new_logs(last_log_id)

            if new_logs:
                for log_data in new_logs:
                    yield f"data: {json.dumps(log_data)}\n\n"
                last_log_id = new_logs[0]['id']

            await asyncio.sleep(2)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
