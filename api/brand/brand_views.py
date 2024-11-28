from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, permissions

from api.brand.brand_serializers import BrandSerializer
from api.models import Brand
from api.views import StandardResultsSetPagination


class BrandCreateView(generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Brand'
    # action = 'add'


# List All Brands
class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand_name', 'is_verified']
    search_fields = ['brand_name', 'brand_description']
    ordering_fields = ['brand_name', 'created_at']
    pagination_class = StandardResultsSetPagination


# Brand Detail, Update, Delete
class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Brand'

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None
