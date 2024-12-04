from django.urls import path
from .product_views import *

urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-manager'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]