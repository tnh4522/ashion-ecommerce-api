from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework import generics

from api.models import Stock, StockProduct
from api.stock.stock_serializers import *
from ..views import StandardResultsSetPagination


class StockCreateView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Update, delete, or get specific stock
class StockUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [permissions.IsAuthenticated]


# List all stocks
class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'is_active', 'location']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination


# Create new stock product entry
class StockProductCreateView(generics.CreateAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Update, delete, or get specific stock product
class StockProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer
    # permission_classes = [permissions.IsAuthenticated]


# List all stock products
class StockProductListView(generics.ListAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product__name', 'quantity']
    search_fields = ['product__name']
    ordering_fields = ['quantity', 'updated_at']
    pagination_class = StandardResultsSetPagination


class StockProductVariantListView(generics.ListAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductVariantSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        stock_id = self.kwargs['pk']
        return StockVariant.objects.filter(stock_id=stock_id)