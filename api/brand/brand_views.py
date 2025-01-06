from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, permissions
from api.brand.brand_serializers import BrandSerializer, BrandLogoSerializer
from api.models import Brand
from api.views import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

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


class BrandLogoView(generics.RetrieveAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandLogoSerializer

    def get(self, request, *args, **kwargs):
        try:
            brand = self.get_object()
            if not brand.brand_logo:
                return Response({"error": "This brand does not have a logo."}, status=404)
            return Response(self.get_serializer(brand).data)
        except Brand.DoesNotExist:
            raise NotFound("Brand not found")