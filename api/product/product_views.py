from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters as dj_filters
from rest_framework import filters as drf_filters, status
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.db.models import Case, When, Value, IntegerField
from api.models import Product
from api.product.product_serializers import ProductSerializer
from api.views import StandardResultsSetPagination

class ProductFilter(FilterSet):
    price__gte = dj_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price__lte = dj_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category__name = dj_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    categories__name = dj_filters.MultipleChoiceFilter(field_name='category__name', lookup_expr='in')

    status = dj_filters.CharFilter(field_name='status', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['categories__name','price','status']

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Product.objects.annotate(
            status_order=Case(
                When(status='ACTIVE', then=Value(1)),
                When(status='DRAFT', then=Value(2)),
                When(status='INACTIVE', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('status_order', 'id')

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'INACTIVE'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
