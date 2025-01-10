from django.urls import path
from .stock_views import *

urlpatterns = [
    path('', StockListView.as_view(), name='stock-list'),
    path('create/', StockCreateView.as_view(), name='stock-create'),
    path('<int:pk>/', StockUpdateDeleteView.as_view(), name='stock-update-delete'),
    path('<int:stock_id>/products/', StockProductVariantListView.as_view(), name='stock-product-list'),
]



