from django.urls import path
from .brand_views import *

urlpatterns = [
    path('list/', BrandListView.as_view(), name='brand-list'),
    path('create/', BrandCreateView.as_view(), name='brand-create'),
    path('detail/<int:pk>/', BrandDetailView.as_view(), name='brand-update-delete'),
    path('logo/<int:pk>/', BrandLogoView.as_view(), name='brand-logo'),
]