from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from rest_framework import filters as drf_filters, status, permissions
from rest_framework.response import Response
from rest_framework import generics
from api.models import Product
from api.product.product_serializers import ProductSerializer
from api.views import StandardResultsSetPagination

class ProductFilter(FilterSet):
    price__gte = NumberFilter(field_name="price", lookup_expr='gte')
    price__lte = NumberFilter(field_name="price", lookup_expr='lte')
    category__name = CharFilter(field_name='category__name', lookup_expr='icontains')
    status = CharFilter(field_name='status', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['category__name', 'price', 'status']


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku', 'category__name']  # có thể search theo name, desc, sku, category
    ordering_fields = ['price', 'name', 'stock', 'status', 'category__name']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        category_names = request.query_params.getlist('category__name__in', [])
        category_logic = request.query_params.get('category_logic', 'OR')

        if category_names:
            queryset = queryset.filter(category__name__in=category_names).distinct()


        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'INACTIVE'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
