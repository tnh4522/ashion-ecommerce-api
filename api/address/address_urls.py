from django.urls import path
from api.address.address_views import *

urlpatterns = [
    path('create/', AddressCreateView.as_view(), name='address-create'),
    path('detail/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
]