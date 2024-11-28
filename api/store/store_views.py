from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework import generics

from api.models import Store
from api.store.store_serializers import StoreSerializer
from api.views import StandardResultsSetPagination


class StoreCreateView(generics.CreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Store'
    # action = 'add'

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


# List All Stores
class StoreListView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store_name', 'is_verified']
    search_fields = ['store_name', 'store_description']
    ordering_fields = ['store_name', 'rating', 'total_sales']
    pagination_class = StandardResultsSetPagination


# Store Detail, Update, Delete
class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Store'

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None