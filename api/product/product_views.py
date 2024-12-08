from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, permissions

from api.models import Product
from api.product.product_serializers import ProductSerializer
from api.views import StandardResultsSetPagination


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        product = serializer.save()
        updated_serializer = self.get_serializer(product)
        self.final_response_data = updated_serializer.data

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'price', 'stock']
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = StandardResultsSetPagination


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [HasRolePermission]
    # model_name = 'Product'
    # action = 'change'
