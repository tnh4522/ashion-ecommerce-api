from django.urls import path
from .product_views import *
from .variant_views import *

urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-manager'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('stock-variants/<int:pk>/', StockVariantUpdateView.as_view(), name='stock-variant-update'),
    path('stock-variants/<int:pk>/delete/', StockVariantDestroyView.as_view(), name='stock-variant-delete'),
    path('update_stock_variants/', UpdateStockVariantsAPIView.as_view(), name='update_stock_variants'),
]
