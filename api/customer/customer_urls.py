from django.urls import path
from .customer_views import *

urlpatterns = [
    path('list/', CustomerManagerView.as_view(), name='customer-manager'),
    path('create/', CustomerManagerView.as_view(), name='customer-create'),
    path('detail/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
]