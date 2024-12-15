from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework import permissions, generics
from rest_framework.pagination import PageNumberPagination

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
