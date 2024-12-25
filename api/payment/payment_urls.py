from django.urls import path
from .payment_views import *

urlpatterns = [
    path('methods/', PaymentMethodsView.as_view(), name='order-list'),
]